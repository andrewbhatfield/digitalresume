from collections import deque
from random import sample

pieces = ['I','J','L','Z','S','T','O']

class Tetris():
    def __init__(self, queue=None, board=None, hold=None):
        if queue is None:
            queue = deque()
            queue.extend(self.randomBag())
            
        if board is None:
            board = ''
        if hold is None:
            hold = ''

        self.queue = queue
        self.board = board
        self.hold = hold

    def randomBag(self):
        return sample(pieces,len(pieces)) # new copy of shuffled list