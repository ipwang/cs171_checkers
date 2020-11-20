from random import randint
from BoardClasses import Move
from BoardClasses import Board

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.

import datetime
import math

EXPLORE_CONSTANT = 2
SIM_THRESHOLD = 5
DEFAULT_WIN = 2
DEFAULT_SIM = 5
DEFAULT_UCT = 1000
FEW_MOVES = 4
SHORT_TURN = 7
FULL_TURN = 12


class Node():
    def __init__(self, color, move, parent=None):
        self.color = color
        self.move = move
        self.wins = 0
        self.sims = 0
        self.children = []
        self.parent = parent

    def UCT(self):
        if self.parent is None:
            return DEFAULT_UCT
        return self.wins / self.sims + EXPLORE_CONSTANT * math.sqrt((math.log(self.parent.getSims()) / self.getSims()))

    def getWinRate(self):
        if self.sims != 0:
            return self.wins / self.sims
        else:
            return -1

    def getWins(self):
        if self.sims < SIM_THRESHOLD:
            return DEFAULT_WIN
        return self.wins

    def getSims(self):
        if self.sims < SIM_THRESHOLD:
            return DEFAULT_SIM
        return self.sims

    def upWins(self):
        self.wins += 1

    def upSims(self):
        self.sims += 1


class StudentAI():
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1: 2, 2: 1}
        self.color = 2
        self.root = Node(self.color, -1)
        self.startTurn = datetime.datetime.now()
        self.turnDuration = FULL_TURN

    def flatten(self, ini_list) -> list:
        return sum(ini_list, [])

    def isTimeLeft(self):
        time = datetime.datetime.now()
        if (time - self.startTurn).seconds < self.turnDuration:
            return True
        return False

    def select(self) -> Node:
        maxNode = self.root
        maxUct = -1
        ptr = self.root
        uct = None
        found = False

        while len(ptr.children) != 0:  # ptr is not a leaf node
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
                    return ptr  # Node is a leaf node, return parent to expand later

            if maxNode.move != -1:
                self.board.make_move(maxNode.move, ptr.color)
            ptr = maxNode

        # Node is leaf node
        return ptr  # Same thing as line 135

    def expand(self, node) -> Node:
        moves = self.flatten(self.board.get_all_possible_moves(node.color))
        toMove = moves[0]  # TODO change to improve time?

        childrenMoves = []
        for c in node.children:
            childrenMoves.append(c.move.seq)
        for m in moves:
            # TODO: improve time
            # looks for first move in list of all moves that hasn't been expanded
            if childrenMoves.count(m.seq) == 0:
                toMove = m
                break

        child = Node(self.opponent[node.color], toMove, node)
        node.children.append(child)
        self.board.make_move(toMove, node.color)  # ADDED
        return child

    def heuristic(self, move, turn) -> int:
        # heuristic that is turn-dependent (ie whose turn it currently is)
        self.board.make_move(move, turn)
        num = 0
        if turn == 1:
            # black
            num = self.board.black_count - self.board.white_count
        else:
            # white
            num = self.board.white_count - self.board.black_count
        self.board.undo()
        return num


    def heuristic2(self) -> int:
        # heuristic counts for black-white
        return self.board.black_count - self.board.white_count


    def simulate(self, child):
        players = {1: "B", 2: "W"}
        color = child.color
        winner = None
        counter = 0
        '''
        while self.board.is_win(players[color]) == 0:
            moves = self.flatten(self.board.get_all_possible_moves(color))
            if len(moves) != 0:
                #player has moves

                # choose random move to simulate
                #i = randint(0, len(moves) - 1)
                #self.board.make_move(moves[i], color)

                # choose move with heuristic (the first one)
                """
                scores = []
                for i in range(len(moves)):
                    scores.append(self.heuristic(moves[i], color))
                maxScore = -1
                moveIndex = 0
                for j in range(len(scores)):
                    if scores[j] > maxScore:
                        maxScore = scores[j]
                        moveIndex = j
                self.board.make_move(moves[moveIndex], color)
                # print("all moves:", moves)
                # print("all scores:", scores)
                # print("move simulated: ", moves[moveIndex])
                # print("score of move simulated: ", scores[moveIndex])
                """

                color = self.opponent[color]
                counter += 1
            else:
                #player doesnt have moves, but game hasn't ended yet
                color = self.opponent[color]
        '''
        depth = 0
        while self.board.is_win(players[color]) == 0 or depth == 10:
            moves = self.flatten(self.board.get_all_possible_moves(color))
            if len(moves) != 0:
                # player has moves

                # choose random move to simulate
                i = randint(0, len(moves) - 1)
                self.board.make_move(moves[i], color)

                color = self.opponent[color]
                counter += 1
            else:
                # player doesnt have moves, but game hasn't ended yet
                color = self.opponent[color]
            depth += 1

        if self.board.is_win(players[color]) == 0:
            if self.heuristic2() > 0:
                winner = 1
            else:
                winner = 2
        else:
            winner = self.board.is_win(players[color])
        while counter != 0:
            self.board.undo()
            counter -= 1
        return winner

    def backProp(self, result, child):
        counter = 0
        while child != self.root:
            child.upSims()
            if result != child.color:
                child.upWins()
            child = child.parent
            counter += 1
        for i in range(counter):
            self.board.undo()  # Added

    def MCTS(self, moves) -> Move:
        if len(moves) <= FEW_MOVES:
            self.turnDuration = SHORT_TURN
        else:
            self.turnDuration = FULL_TURN

        while (self.isTimeLeft()):
            # print("board before select")
            # self.board.show_board()
            parent = self.select()
            # print("board after select")
            # self.board.show_board()
            expand = self.expand(parent)  # TODO check if expand() returns None
            # print("board after expand")
            # self.board.show_board()
            result = self.simulate(expand)
            # print("board after simulation")
            # self.board.show_board()
            self.backProp(result, expand)
            # print("board after backprop (same as before select)")
            # self.board.show_board()

        bestMove = None  # self.root.children[i].move
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

    def findIndexWithMove(self, m) -> int:
        i = 0
        while i != len(self.root.children):
            if self.root.children[i].move == m:
                break
            i += 1
        return i

    def get_move(self, move):
        self.startTurn = datetime.datetime.now()
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])

            # update root (opponent's move)
            if self.root.parent is None:
                self.root.move = move
            else:
                i = self.findIndexWithMove(move)
                if i != len(self.root.children):
                    # set to existing child
                    self.root = self.root.children[i]
                else:
                    # add new child
                    new_root = Node(self.color, move, self.root)
                    self.root.children.append(new_root)
                    self.root = new_root
        else:
            self.color = 1
            self.root.color = 1

        moves = self.flatten(self.board.get_all_possible_moves(self.root.color))
        if len(moves) == 1:
            move = moves[0]
        else:
            move = self.MCTS(moves)

        # print("num moves avail:", len(moves))
        # print("num real sims at root: ", self.root.sims)
        # print("player whose turn: ", self.color)

        # self.board.show_board()
        self.board.make_move(move, self.color)

        # update root (own move)
        if len(moves) != 1:
            # set to existing child
            self.root = self.root.children[self.findIndexWithMove(move)]
        else:
            # add new child
            new_root = Node(self.opponent[self.color], move, self.root)
            self.root.children.append(new_root)
            self.root = new_root

        return move