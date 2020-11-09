from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

class MCT():

    def __init__(self, color, move, parent = None):
        self.color = color
        self.move = move
        self.wins = 0
        self.sims = 0
        self.children = []
        self.parent = parent


    def getWinRate(self):
        if self.sims != 0:
            return self.wins / self.sims

        else:
            return -1   #No simulations run, cannot divide by 0


    def upWins(self):
        self.wins += 1


    def upSims(self):
        self.sims += 1


    def upChild(self, child):
        self.children.append(child)





class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        self.tree = MCT(self.color, -1) ######Might remove

    def get_move(self,move):
        if len(move) != 0:                                          #If opponent made move, length = 1, else 0
            self.board.make_move(move,self.opponent[self.color])    #Update board with opponent's move
        else:
            self.color = 1                                          #Opponent couldn't make a move, pass


        #Determine and make moves below (BROKEN)
        #For every current node, make a new tree and do MC; after a move has been made, make a new tree for that node and so on

        if len(self.tree.children) == 0:                            #Leaf node, must expand
            moves = self.board.get_all_possible_moves(self.color)
            index = randint(0,len(moves)-1)                             #Indexes move from list with first coordinates as selected checker and second coordinates as selected move
            inner_index =  randint(0,len(moves[index])-1)               #...
            move = moves[index][inner_index]




        self.board.make_move(move,self.color)
        return move
