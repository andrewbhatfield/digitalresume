class Board:
    '''keeps board info/methods for square boardSize-length tictactoe board
    board is array of length boardSize**2
    '''
    boardSize = 3
    playerMark = 'x'
    botMark = 'o'
    emptyMark = ''
    nodeCount = 0


    def __init__(self, board=None) -> None:
        if board is None:
            board = [Board.emptyMark for x in range(Board.boardSize**2)]
        self.board = board 

    def makeMove(self, index, mark) -> None:
        self.board[index] = mark

    def makeBotMove(self, index) -> None:
        self.makeMove(index, Board.botMark)

    def makePlayerMove(self, index) -> None:
        self.makeMove(index, Board.playerMark)

    def oppositeMark(mark) -> str:
        assert (mark in [Board.playerMark, Board.botMark]), '????'
        if mark == Board.playerMark:
            return Board.botMark
        elif mark == Board.botMark:
            return Board.playerMark

    def checkWin(self, mark) -> bool: # most efficient python program gigachad TODO fix this bullshit
        if len(self.empties) > Board.boardSize*(Board.boardSize - 1): # can skip checking if there are too many empty
            return False
        for i in range(Board.boardSize):
            # checking rows
            rowIndices = range(i*Board.boardSize,(i+1)*Board.boardSize)
            if(all([self.board[index] == mark for index in rowIndices])):
                return True
            # checking cols
            colIndices = range(i,Board.boardSize**2, Board.boardSize)
            if(all([self.board[index] == mark for index in colIndices])):
                return True
        # checking main diag
        diagIndices = [i * Board.boardSize + i for i in range(Board.boardSize)]
        if(all([self.board[index] == mark for index in diagIndices])):
            return True    
        # checking off diag
        offDiagIndices = [i*Board.boardSize - i for i in range(1, Board.boardSize+1)]
        if(all([self.board[index] == mark for index in offDiagIndices])):
            return True    
        return False
    
    def minimax(board, mark, alpha, beta) -> dict:
        '''returns {'move': #, 'score': #} of optimal ply'''
        # note alpha is the minimum score for maximizing player and beta is maximum score of minimizing player
        b = Board(board=board)
        #print(board)
        Board.nodeCount += 1

        # check if game is over
        if (b.checkWin(Board.playerMark)):
            return 1
        elif b.checkWin(Board.botMark):
            return -1
        elif b.empties == []:
            return 0
    
        best = {}
        if (mark == Board.playerMark):
            value = -999
            for i in b.empties: 
                b.makeMove(i, mark)
                mm = Board.minimax(b.board, Board.oppositeMark(mark), alpha, beta)
                b.makeMove(i, Board.emptyMark)
                if type(mm) is int:
                    score = mm
                else:
                    score = mm['score']
                if score > value:
                    best = {'move': i, 'score': score}
                    value = score
                alpha = max(alpha, value)
                if value >= beta:
                    break
            return best
        else:
            value = 999
            best = {}
            for i in b.empties:
                move = i
                b.makeMove(i, mark)
                mm = Board.minimax(b.board, Board.oppositeMark(mark), alpha, beta)
                b.makeMove(i, Board.emptyMark)
                if type(mm) is int:
                    score = mm
                else:
                    score = mm['score']
                if score < value:
                    best = {'move': i, 'score': score}
                    value = score
                beta = min(beta, value)
                if value <= alpha:
                    break
            return best

    def __repr__(self) -> str:
        return str(self.board)
    
    def __hash__(self) -> int: # attempt to prevent caching hash collisions?
        return hash(repr(self)) 

    def __str__(self) -> str:
        '''output board as (e.g. 3x3)
        [
            [0,1,2], 
            [3,4,5], 
            [6,7,8]
        ]
        '''
        fboard = [[Board.emptyMark for x in range(Board.boardSize)] for x in range(Board.boardSize)]
        for index in range(len(self.board)):
            fboard[(index // Board.boardSize)][(index % Board.boardSize)] = self.board[index]
        return '\n'.join([str(i) for i in fboard] + [''])
    
    
    @property
    def empties(self) -> list:
        return [i for i in range(Board.boardSize**2) if self.board[i]==Board.emptyMark]

    @property
    def gameState(self) -> str:
        if self.empties == []:
            return 'Game is drawn.' # draw
        elif self.checkWin(Board.playerMark):
            return 'Player has won.'
        elif self.checkWin(Board.botMark):
            return 'Bot has won.'
        else: return 'Game is in progress.' # no current winner