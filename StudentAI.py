from random import randint
from BoardClasses import Move
from BoardClasses import Board

#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

import datetime
import math

turnTimer = 15
exploreConst = 1.4
simThreshold = 5
defaultWins = 1
defaultSims = 5
defaultUCT = 1000

class Node():
    def __init__(self, color, move, parent = None):
        self.color = color
        self.move = move
        self.wins = 0
        self.sims = 0
        self.children = []
        self.parent = parent


    def UCT(self):
        if self.parent is None:
            return defaultUCT
        return self.wins / self.sims + exploreConst * math.sqrt((math.log(self.parent.sims), self.sims))


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


    def getWins(self):
        if self.sims < simThreshold:
            return defaultWins
        return self.wins



    def getSims(self):
        if self.sims < simThreshold:
            return defaultSims
        return self.sims
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
        time = datetime.datetime.now()
        if (time - self.start).seconds < turnTimer: #TODO Change 15 seconds to something smaller when debugging
            return True
        return False


    def chooseMove(self, node) -> Move: #Given a node with a potential leaf, return that leaf node if it's not already part of the official children
        found = False
        moves = self.flatten(self.board.get_all_possible_moves(node.color))
        for m in moves:
            found = False
            for n in node.children:
                if not found and n.move.seq == m.seq: #TODO CHANGED
                    found = True
            if not found:
                return m

        """
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
        """

    def select(self) -> Node: #REMINDER: moves is the flattened list of all available moves
        maxNode = self.root
        maxUct = -1
        ptr = self.root
        uct = None
        found = False

        while len(ptr.children) != 0: #Node is not a leaf node
            moves = self.flatten(self.board.get_all_possible_moves(self.color))
            for m in moves:
                found = False
                for c in ptr.children:
                    if not found and m == c.move:
                        uct = c.UCT()
                        if uct > maxUct:
                            maxUct = uct
                            maxNode = c
                        found = True
                if not found:
                    return ptr #Node is a leaf node, return parent to expand later

            ptr = maxNode
            self.color = self.opponent[self.color]
            if maxNode.move != -1:
                self.board.make_move(maxNode.move, self.color)

        # Node is leaf node
        return ptr #Same thing as line 135


    def expand(self, node) -> Node:
        child = None
        moveToMake = self.chooseMove(node)
        if moveToMake is None:
            #moveToMake didn't have options TODO
            pass
        else:
            #moveToMake was valid and returned a Move object and updated board
            child = Node(self.opponent[node.color], moveToMake, node)
            node.children.append(child) #This line actually adds children to a node
        return child


    def simulate(self, child):
        players = {1: "B", 2: "W"}
        winner = None
        counter = 0

        #self.color = child.color #prob dont need this line but just in case
        while self.board.is_win(players[self.color]) == 0:
            moves = self.flatten(self.board.get_all_possible_moves(self.color))
            if len(moves) != 0: #player has moves
                i = randint(0, len(moves) - 1)
                self.board.make_move(moves[i], self.color)
                self.color = self.opponent[self.color]
                counter += 1
            else: #player doesnt have moves, but game hasn't ended yet
                self.color = self.opponent[self.color]

        winner = self.board.is_win(players[self.color])
        while counter != 0:
            self.board.undo()
            self.color = self.opponent[self.color]
            counter -= 1
        return winner


    def backProp(self, result, child):
        while child is not None:
            child.upSims()
            if result != child.color:
                child.upWins()
            child = child.parent


    def MCTS(self, moves) -> Move:
        while (self.isTimeLeft()):
            parent = self.select()
            expand = self.expand(parent) #TODO check if expand() returns None
            result = self.simulate(expand)
            self.backProp(result, expand)

        bestMove = None # self.root.children[i].move

        if len(self.root.children) == 0:# TODO ADDED
            index = randint(0, len(moves) - 1)
            bestMove = moves[index]
        else:
            bestWR = -1
            i = 0
            while i != len(self.root.children):
                if self.root.children[i].getWinRate() > bestWR:
                    bestWR = self.root.children[i].getWinRate()
                    bestMove = self.root.children[i].move
                i += 1

        return bestMove
        #return the move in Actions(state) whose node has highest number of playouts highest w/s

    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
            if self.root.parent is None: # len(self.root.children) == 0:
                #what if the root.children doesnt contain the one move we wanted?
                # FIX: checking len of self.root.children to moves of self.root
                self.root.move = move
            else:
                i = 0
                while i != len(self.root.children):
                    if self.root.children[i].move == move:
                        break
                    i += 1
                if i != len(self.root.children):
                    self.root = self.root.children[i]
                else: #no child node: add it
                    new_root = Node(self.color, move, self.root)
                    self.root.children.append(new_root)
                    self.root = new_root

        else:
            self.color = 1
            self.root.color = 1                                     #Opponent couldn't make a move, pass

        self.start = datetime.datetime.now()
        """
        if self.root.move == -1:
            #no move was made previously (ie first player's turn) TODO check if opponent got stuck
            #do MCTS normally
            pass
        else:
            #update root to move just picked from opponent if move exists
            i = 0
            while i != len(self.root.children):
                if self.root.children[i].move == move:
                    break
                i += 1
            self.root = self.root.children[i]
        """
        moves = self.flatten(self.board.get_all_possible_moves(self.color))
        move = self.MCTS(moves)

        self.board.make_move(move, self.color) # PROBLEM LINE: color mismatch
        # update root to move just picked from MCTS
        i = 0
        while i != len(self.root.children):
            if self.root.children[i].move == move:
                break
            i += 1
        self.root = self.root.children[i]
#        self.color = self.opponent[self.color]
        return move

# OLD SELECT TODO
"""
child = None
result = None

#expand all children from ROOT only

if len(self.root.children) != len(moves): #TODO: update so if only has some children, gets all
    for m in moves:
        for n in self.root.children:
            if moves
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
"""

