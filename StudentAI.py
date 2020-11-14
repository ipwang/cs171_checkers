from random import randint
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

import datetime

class Node():
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

"""
FROM discord
    - 3 second timer: 300-600 playouts (low at start, peaks towards ends)
    heuristics implemented in simulation part, selection part (defined by UCB in book)
        heuristic could be num pieces for each side: use board.white_count and black_count()
    each node: game state/board object (not very memory efficient)
    want to limit depth, or will regret
    - avg ~50 moves per game on 8x8 board, ~25 moves/player; 19 sec to make move: play safe and use 15
    - EXPANSION start: add root of tree and all its children, 
    - keep track of one board at a time, use board has undo function
    import copy and do copydeepcopy(self.board): or use board.undo
"""

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

        self.root = Node(self.color, -1)
        self.start = None

    def flatten(self, ini_list) -> list:
        return sum(ini_list, [])

    def isTimeLeft(self):
        if (self.start - datetime.datetime.now()).seconds < 15:
            return True
        return False

    def chooseMove(self, node) -> Move: #returns Move if valid move is available, else None
        #choose random move from node given
        moves = self.flatten(self.board.get_all_possible_moves(node.color))
        if len(moves) != 0:
            # move is possible
            i = randint(0, len(moves) - 1)
            self.board.make_move(moves[i], self.color)
            self.color = self.opponent[node.color]
            return moves[i]
        else:
            # move is not possible, just change the color w/o changing board
            self.color = self.opponent[self.color]
            return None

    def select(self, moves) -> Node:
        child = None
        result = None

        #expand all children from ROOT only
        if len(self.root.children) == 0: #TODO: update so if only has some children, gets all
            for m in moves:
                child = self.root.children.append(Node(self.opponent[self.color], m, self.root))
                result = self.simulate(child) #TODO check
                self.backProp(result, child)

        #go to a leaf node randomly TODO UCT/UCB instead
        leaf = self.root
        leafIndex = None
        while len(leaf.children) != 0:
            leafIndex = randint(0, len(moves)-1)
            leaf = leaf.children[leafIndex]
            self.board.make_move(leaf.move, self.color)
            self.color = self.opponent[self.color]
        return leaf

    def expand(self, leaf) -> Node:
        moveToMake = self.chooseMove(leaf)
        if moveToMake is None:
            #moveToMake didn't have options TODO
            pass
        else:
            #moveToMake was valid and returned a Move object and updated board
            child = Node(self.opponent[leaf.color], moveToMake, leaf)
            leaf.children.append(child)
        return child

    def simulate(self, child):
        players = {1: "B", 2: "W"}
        winner = None
        counter = 0

        self.color = child.color #prob dont need this line but just in case
        while self.board.is_win(players[self.color]) == 0:
            moves = self.flatten(self.board.get_all_possible_moves(self.color))
            if len(moves) != 0: #player has moves
                i = randint(0, len(moves) - 1)
                self.board.make_move(moves[i], self.color)
                self.color = self.opponent[self.color]
                ++counter
            else: #player doesnt have moves, but game hasn't ended yet
                self.color = self.opponent[self.color]

        winner = self.board.is_win(players[self.color])
        while counter != 0:
            self.board.undo()
            --counter
        return winner

    def backProp(self, result, child):
        while child is not None:
            child.upSims()
            if result != child.color:
                child.upWins()
            child = child.parent

    def MCTS(self, moves) -> Move:
        while (self.isTimeLeft()):
            self.select(moves)
            leaf= self.select(self.root)
            child = self.expand(leaf) #TODO check if expand() returns None
            result = self.simulate(child)
            self.backProp(result, child)

#TODO CHECK THIS
        bestChild = None
        bestWR = 0
        i = 0
        while i != len(self.root.children):
            if self.root.children[i].getWinRate() > bestWR:
                bestWR = self.root.children[i].getWinRate()
                bestChild = self.root.children[i]
            ++i

        return bestChild
        #return the move in Actions(state) whose node has highest number of playouts highest w/s

    def get_move(self,move):
        if len(move) != 0:                                          #If opponent made move, length = 1, else 0
            self.board.make_move(move,self.opponent[self.color])    #Update board with opponent's move
        else:
            self.color = 1                                          #Opponent couldn't make a move, pass

        # TODO added
        self.start = datetime.datetime.now()

        if self.root.move == -1:
            #no move was made previously (ie first player's turn) TODO check if opponent got stuck
            #do MCTS normally
            pass
        else:
            #update root to move just picked from opponent if move exists
            i = 0
            while i != len(self.root.children):
                if self.root.children[i].move is move:
                    break
                ++i
            self.root = self.root.children[i]

        moves = self.flatten(self.board.get_all_possible_moves(self.color))
        move = self.MCTS(self, moves)

        # update root to move just picked from MCTS
        i = 0
        while i != len(self.root.children):
            if self.root.children[i].move is move:
                break
            ++i
        self.root = self.root.children[i]


        #Determine and make moves below (BROKEN)
        #For every current node, make a new tree and do MC; after a move has been made, make a new tree for that node and so on

        # if len(self.tree.children) == 0:                            #Leaf node, must expand
        # moves = self.board.get_all_possible_moves(self.color)
        # index = randint(0,len(moves)-1)                             #Indexes move from list with first coordinates as selected checker and second coordinates as selected move
        # inner_index =  randint(0,len(moves[index])-1)               #...
        # move = moves[index][inner_index]

        self.board.make_move(move,self.color)
        return move

"""
start at root (first players move)
REPEAT: check the time
select: first time: root
R
A, B, C, D
expand: first time: expand all children of R
simulate: first time: choose one A-D using UCT/UCB formula: choose random move until termination:
back: termination, go up children using parent pointer (while also Board.undo()), update w, s in each node
"""

