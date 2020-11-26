from random import randint
from BoardClasses import Move
from BoardClasses import Board

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.

import datetime
import math

EXPLORE_CONSTANT = 2
SIM_THRESHOLD = 3 #5
DEFAULT_WIN = 9 #2
DEFAULT_SIM = 10 #5
DEFAULT_UCT = 1000
FEW_MOVES = 4
SHORT_TURN = 7
FULL_TURN = 12
DEPTH_LEVEL = 10

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

    def select(self, moves) -> Node:
        ptr = self.root
        maxNode = None
        maxNodes = []
        uct = None

        while len(ptr.children) == len(moves):
            # all of ptr's children have been expanded
            # iterate through all children moves and set child with highest uct value as ptr (and update board)
            maxNodes.clear()
            maxUct = -1
            for c in ptr.children:
                uct = c.UCT()
                if uct > maxUct:
                    maxUct = uct
                    maxNodes.clear()
                    maxNodes.append(c)
                elif uct == maxUct:
                    maxUct = uct
                    maxNodes.append(c)

            i = randint(0, len(maxNodes) - 1)
            maxNode = maxNodes[i]

            self.board.make_move(maxNode.move, ptr.color)
            ptr = maxNode
            moves = self.flatten(self.board.get_all_possible_moves(self.opponent[ptr.color]))
            # if len(moves) == 0:
            #     # no moves possible
            #     # TODO alternatively: move up using parent pointers to a parent with 1+ child?
            #     # set as sentinel value that gets checked in MCTS
            #     return -1

        return ptr


    def expand(self, node) -> Node:
        '''
        Assumes node has unexpanded children (fix assumption: initial toMove to None and fix
        '''
        moves = self.flatten(self.board.get_all_possible_moves(node.color))

        # print("inside expand: len of moves is ", len(moves))
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
        self.board.make_move(toMove, node.color)
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


    def count_heuristic(self) -> int:
        # heuristic counts for black-white
        return self.board.black_count - self.board.white_count


    def king_heuristic(self):
        '''
        gives a higher score to boards that are closer to attaining more kings
        king piece: 100 points each
        man piece: 5*row
        '''
        score = 0
        players = {0: ".", 1: "B", 2: "W"}
        player = players[self.color]
        board_row = self.board.row
        board_col = self.board.col
        board = self.board.board

        for r in range(board_row):
            for c in range(board_col):
                piece = board[r][c]
                if piece.color == player:
                    #exists checker piece and color matches
                    if piece.is_king:
                        # piece is a king
                        score += 100
                    else:
                        # piece is a man
                        if self.color == 1:
                            # black
                            score += r*5
                        else:
                            # white
                            score += 5*(board_row-r-1)
        return score


    def simulate(self, child):
        players = {1: "B", 2: "W"}
        color = child.color
        winner = None
        counter = 0
        depth = 0
        while self.board.is_win(players[color]) == 0 or depth == DEPTH_LEVEL:
            moves = self.flatten(self.board.get_all_possible_moves(color))
            if len(moves) != 0:
                # player has moves

                # 1. choose random move to simulate
                # i = randint(0, len(moves) - 1)
                # self.board.make_move(moves[i], color)

                # 2. choose move based on king's heuristic
                maxScore = -1
                m = randint(0, len(moves)-1) # default random
                for i in range(len(moves)):
                    self.board.make_move(moves[i], color)
                    score = self.king_heuristic()
                    if score > maxScore:
                        maxScore = score
                        m = i
                    self.board.undo()
                self.board.make_move(moves[m], color)

                color = self.opponent[color]
                counter += 1
            else:
                # player doesnt have moves, but game hasn't ended yet
                color = self.opponent[color]
            depth += 1

        if self.board.is_win(players[color]) == 0:
            if self.count_heuristic() > 0:
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
        # child is the root
        child.upSims()
        if result != child.color:
            child.upWins()

        for i in range(counter):
            self.board.undo()

    def MCTS(self, moves) -> Move:
        if len(moves) <= FEW_MOVES:
            self.turnDuration = SHORT_TURN
        else:
            self.turnDuration = FULL_TURN

        while (self.isTimeLeft()):
            parent = self.select(moves)
            expand = self.expand(parent)  # TODO check if expand() returns None
            result = self.simulate(expand)
            self.backProp(result, expand)

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

        # TODO remove these print statements for AI_Runner
        # print("player's turn: ", self.color)
        # print("len moves", len(moves))
        self.board.make_move(move, self.color)
        # TODO remove these print statements for AI_Runner
        # print("len children", len(self.root.children))
        # print("num real wins at root: ", self.root.wins)
        # print("num real sims at root: ", self.root.sims)
        # print("move chosen: ", move)

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