from random import choice, randint
from math import sqrt
from collections import deque

import numpy as np


class Maze():
    def __init__(self, maze=None, dimensions=(31,31)):
        self.dimensions = dimensions
        if maze is None:
            maze = self.generate()
        else: 
            self.dimensions = [int(sqrt(len(maze)))] * 2 # square only?
        self.maze = maze

    def toCoordinates(self, index):
        return (index // self.dimensions[1], index % self.dimensions[1]) # row,col
    
    def toIndex(self, x,y): #(x,y)
        return x * self.dimensions[1] + y if x * self.dimensions[1] + y >= 0 else self.dimensions[1] * self.dimensions[0] + x * self.dimensions[1] + y

    def generate(self): 
        '''prims algorithm for minimal spanning tree, see wikipedia entry on https://en.wikipedia.org/wiki/Maze_generation_algorithm#Iterative_randomized_Prim's_algorithm_(without_stack,_without_sets)'''
        # use 0 for walls and 1 for passages
        maze = [0] * (self.dimensions[0]*self.dimensions[1])
        maze[0] = 1 # set top left corner to passage for convenience
        pairs = [(0, neighbor) for neighbor in self.getNeighbors(0)] # walls stored as pairs of cells they divide

        while pairs:
            pair = choice(pairs)
            pairs.remove(pair)

            c1 = pair[0]
            c2 = pair[1]

            if maze[c2] == 0: # check other side is not already visited (c1 is always a passage due to the way we store pairs)
                x1, y1 = self.toCoordinates(c1)
                x2, y2 = self.toCoordinates(c2)
                between = self.toIndex((x1 + x2) // 2, (y1 + y2) // 2)

                maze[between] = 1
                maze[c2] = 1


            for neighbor in self.getNeighbors(c2):
                if maze[neighbor] == 0:
                    pairs.append((c2, neighbor))

        

        return maze

    def getNeighbors(self, index): # not suitable for maze solving - offsets by 2 to allow walls to generate between passages
        x, y = self.toCoordinates(index)
        offsets = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        neighbors = []
        for dx, dy in offsets:
            nx = x + dx
            ny = y + dy
            if 0 <= nx < self.dimensions[0] and 0 <= ny < self.dimensions[1]:
                neighbors.append(self.toIndex(nx,ny))

        return neighbors

    @property
    def padded(self): # pads maze with walls
        arr = np.pad(np.reshape(self.maze, (self.dimensions[0],self.dimensions[1])), pad_width=1, mode='constant', constant_values=0)
        return arr



class Solver(Maze):
    def __init__(self, maze):
        self.maze = maze

    def right(self, direction): # gotta be a better way to do these, 'cycle' mod 4?
        if direction == (-1,0): 
            return (0,1)
        elif direction == (0,1):
            return (1,0)
        elif direction == (1,0):
            return (0,-1)
        elif direction == (0,-1):
            return (-1,0)
        
    def left(self, direction):
        if direction == (-1,0): 
            return (0,-1)
        elif direction == (0,-1):
            return (1,0)
        elif direction == (1,0):
            return (0,1)
        elif direction == (0,1):
            return (-1,0)
        
    def rightHandRule(self):
        recent = 0 #always start in top left pixel (top border)
        direction = (1,0) # always start facing south
        height, width = self.maze.dimensions[0], self.maze.dimensions[1]

        yield (0,)

        while recent != height*width-1: # height*width-1 is index of last pixel
            x1, y1 = self.maze.toCoordinates(recent)
            dx, dy = direction
            try: 
                if self.maze.maze[self.maze.toIndex(x1 + dx, y1 + dy)] == 0:
                    direction = self.left(direction)
                else:
                    if not (0 <= x1 + dx <= width - 1 and 0 <= y1 + dy <= height):
                        raise Exception('oob')
                    recent = self.maze.toIndex(x1 + dx, y1 + dy)
                    yield (recent,)
                    # check if right hand is still a wall after moving forward
                    checkX, checkY = self.right(direction)
                    if 0 <= x1 + dx + checkX <= width - 1 and 0 <= y1 + dy + checkY <= height - 1:
                        checkWall = self.maze.toIndex(x1 + dx + checkX, y1 + dy + checkY)
                        if self.maze.maze[checkWall] == 1: # right hand is passage
                            direction = self.right(direction)

            except Exception as e: # tried to walk oob or into wall
                direction = self.left(direction)

        yield (recent,)

        return
    
    
    def l1(self, point, goal):
        # a 'normal' (probably not great) heuristic is the l1/taxicab metric - things that are closer visually to the bottom right are probably close to reaching the end of the maze
        x1, y1 = self.maze.toCoordinates(point)
        x2, y2 = self.maze.toCoordinates(goal)
        return abs(x1 - x2) + abs(y1 - y2)

    def Astar(self):
        openSet = [0]
        parents = {}
        goal = self.maze.dimensions[0] * self.maze.dimensions[1] - 1
        passages = [i for i in range(self.maze.dimensions[0]*self.maze.dimensions[1]) if self.maze.maze[i] == 1]

        gScore = {i: 99999 for i in passages}
        gScore[0] = 0

        fScore = {i: gScore[i] + self.l1(i, goal) for i in passages} 
        fScore[0] = self.l1(0, goal)

        while openSet:
            current = list(dict(sorted({i: fScore[i] for i in openSet if i in fScore.keys()}.items(), key=lambda x: x[1])).keys())[0] # get lowest fscore from openset, this is hideous

            yield current, parents

            if current == goal:
                path = []
                while current != 0:
                    path.append(current)
                    current = parents[current]
                path.append(0)
                path.reverse()

                return
        
            openSet.remove(current)
            for neighbor in self.getNeighboringPassages(current):
                tentative_gScore = gScore[current] + 1 # normal algo checks d(current, neighbor) here but this is always 1
                if tentative_gScore < gScore[neighbor]:
                    parents[neighbor] = current
                    gScore[neighbor] = tentative_gScore
                    fScore[neighbor] = tentative_gScore + self.l1(neighbor, goal)
                    if neighbor not in openSet:
                        openSet.append(neighbor)

        return False

    def BFS(self): # uses queue
        q = deque() 
        explored = [0]
        q.append(0)
        goal = self.maze.dimensions[0] * self.maze.dimensions[1] - 1
        parents = {}

        while q:
            v = q.popleft()

            yield v, parents

            if v == goal:
                return

            for w in self.getNeighboringPassages(v):
                if self.maze.maze[w] == 1 and w not in explored:
                    explored.append(w)
                    parents[w] = v
                    q.append(w)
        
    def DFS(self): # uses stack
        q = []
        explored = [0]
        q.append(0)
        goal = self.maze.dimensions[0] * self.maze.dimensions[1] - 1
        parents = {}

        while q:
            v = q.pop()
            
            yield v, parents
            
            if v == goal:
                return

            for w in self.getNeighboringPassages(v):
                if self.maze.maze[w] == 1 and w not in explored:
                    explored.append(w)
                    parents[w] = v
                    q.append(w)

        
    def getNeighboringPassages(self, index): 
        x, y = self.maze.toCoordinates(index)
        height, width = self.maze.dimensions[0], self.maze.dimensions[1]
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dx, dy in offsets:
            nx = x + dx
            ny = y + dy
            if 0 <= nx < height and 0 <= ny < width:
                index = self.maze.toIndex(nx,ny) 
                if self.maze.maze[index] == 1:
                    neighbors.append(self.maze.toIndex(nx,ny))

        return neighbors
    
    def shortenPath(self, path):
        # cuts out all loops from final maze path, may be useful for bad algos like right hand rule
        complete = False
        while not complete:
            for i in range(len(path)):
                for j in reversed(range(i,len(path))):
                    if path[i] == path[j]:
                        path = path[:i] + path[j:]
                        break
            else:
                complete = True

        return path


    def generateFrames(self, method=None):
        if method == 'bfs':
            gen = self.BFS()
        elif method == 'dfs':
            gen = self.DFS()
        elif method == 'astar':
            gen = self.Astar()
        elif method == 'righthand':
            gen = self.rightHandRule()
        
        visited = []

        frames = []

        for state in gen:
            frame = []
            current = state[0]
            parents = None
            try: # rightHandRule doesn't generate parents
                parents = state[1]
            except:
                pass
            visited.append(current)

            # plot blue visited
            for cell in visited:
                y, x = self.maze.toCoordinates(cell)
                frame.append([y,x,.25])

            cy, cx = self.maze.toCoordinates(current) # save current coords before it gets updated in next block

            #plot green parents (if exists)
            if parents is None: # just use shortenPath so that rightHandRule can show a line in green as well?
                path = self.shortenPath(visited)
            if parents is not None:
                path = [0]
                while current != 0:
                    path.append(current)
                    current = parents[current]

            for cell in path:
                py, px = self.maze.toCoordinates(cell)
                frame.append([py,px,.5])
            
            # plot red current
            frame.append([cy,cx,.75])

            frames.append(frame)
            
        return frames
