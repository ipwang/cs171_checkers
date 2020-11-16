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
        if (time - self.start).seconds < turnTimer:
            return True
        return False


    def select(self) -> Node: #REMINDER: moves is the flattened list of all available moves
        maxNode = self.root
        maxUct = -1
        ptr = self.root
        uct = None
        found = False

        while len(ptr.children) != 0: #Node is not a leaf node
            moves = self.flatten(self.board.get_all_possible_moves(ptr.color))
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

            if maxNode.move != -1:
                self.board.make_move(maxNode.move, ptr.color)
            ptr = maxNode

        # Node is leaf node
        return ptr #Same thing as line 135


    def expand(self, node) -> Node:
        moves = self.flatten(self.board.get_all_possible_moves(node.color))
        toMove = moves[0]

        childrenMoves = []
        for c in node.children:
            childrenMoves.append(c.move.seq)
        for m in moves:
            if childrenMoves.count(m.seq) == 0:
                toMove = m
                break

        child = Node(self.opponent[node.color], toMove, node)
        node.children.append(child)
        return child


    def simulate(self, child):
        players = {1: "B", 2: "W"}
        winner = None
        counter = 0
        color = child.color

        while self.board.is_win(players[color]) == 0:
            moves = self.flatten(self.board.get_all_possible_moves(color))
            if len(moves) != 0: #player has moves
                i = randint(0, len(moves) - 1)
                self.board.make_move(moves[i], color)
                color = self.opponent[color]
                counter += 1
            else: #player doesnt have moves, but game hasn't ended yet
                color = self.opponent[color]

        winner = self.board.is_win(players[color])
        while counter != 0:
            self.board.undo()
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
        if len(self.root.children) == 0:
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
            self.root.color = 1

        self.start = datetime.datetime.now()
        moves = self.flatten(self.board.get_all_possible_moves(self.root.color))
        move = self.MCTS(moves)

        self.board.make_move(move, self.root.color) # PROBLEM LINE: color mismatch
        # update root to move just picked from MCTS
        i = 0
        while i != len(self.root.children):
            if self.root.children[i].move == move:
                break
            i += 1
        self.root = self.root.children[i]
#        self.color = self.opponent[self.color]
        return move