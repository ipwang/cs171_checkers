from random import randint
from BoardClasses import Move
from BoardClasses import Board

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.

import datetime
import math

PLAYERS = {0: ".", 1: "B", 2: "W"}
EXPLORE_CONSTANT = 2
SIM_THRESHOLD = 5
DEFAULT_WIN = 9 #2
DEFAULT_SIM = 10 #5
FEW_MOVES = 4
SHORT_TURN = 7
FULL_TURN = 10 #12
DEPTH_LEVEL = 15 #10


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
            sp = 100
        else:
            sp = self.parent.getSims()
        return self.getWins() / self.getSims() + EXPLORE_CONSTANT * math.sqrt(math.log(sp) / self.getSims())

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
        self.select_ctr = 0

    def flatten(self, ini_list) -> list:
        return sum(ini_list, [])

    def isTimeLeft(self):
        time = datetime.datetime.now()
        if (time - self.startTurn).seconds < self.turnDuration:
            return True
        return False

    def select(self, moves) -> Node:
        # does not need moves param
        ptr = self.root
        maxNodes = []
        self.select_ctr = 0

        while len(ptr.children) != 0:
            # ptr is not a leaf; it has some to all children/moves
            moves = self.flatten(self.board.get_all_possible_moves(ptr.color))
            if len(ptr.children) < len(moves):
                # ptr has only expanded some children/moves
                return ptr

            # all children/moves have been expanded
            maxNodes.clear()
            maxUct = -1
            for c in ptr.children:
                uct = c.UCT()
                if uct > maxUct:
                    maxUct = uct
                    maxNodes.clear()
                    maxNodes.append(c)
                elif uct == maxUct:
                    maxNodes.append(c)
            i = randint(0, len(maxNodes) - 1) #raised InvalidMoveError
            maxNode = maxNodes[i]

            # try:
            self.board.make_move(maxNode.move, ptr.color) # TODO raised InvalidMoveError
            # except:
            #     print("error: InvalidMoveError")
            #     return
            self.select_ctr += 1
            ptr = maxNode

        # check that ptr has children to expand (could be a terminal state)
        moves = self.flatten(self.board.get_all_possible_moves(ptr.color))
        if len(moves) == 0:
            return -1

        return ptr

        '''
        # CODE FROM PRE-THANKSGIVING; raises Index error in expand()
        ptr = self.root
        maxNode = None
        maxNodes = []
        uct = None
        self.select_ctr = 0

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

            self.board.make_move(maxNode.move, ptr.color) #raised InvalidMoveError
            self.select_ctr += 1

            ptr = maxNode
            moves = self.flatten(self.board.get_all_possible_moves(self.opponent[ptr.color]))
            if self.board.is_win(PLAYERS[self.opponent[ptr.color]]) != 0:
                # TODO invalid move error!!!
                # someone won
                # add and check attribute in Node class to see if it is terminal
                # in MCTS: if is terminal, DO SMTH
                return -1

            # if len(moves) == 0:
            #     # no moves possible
            #     # TODO alternatively: move up using parent pointers to a parent with 1+ child?
            #     # set as sentinel value that gets checked in MCTS
            #     return -1

        return ptr
        '''


    def expand(self, node) -> Node:
        '''
        Assumes node has unexpanded children (fix assumption: initial toMove to None and fix
        '''
        moves = self.flatten(self.board.get_all_possible_moves(node.color))

        toMove = moves[0]

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


    def count_heuristic(self) -> int:
        # heuristic counts for black-white
        return self.board.black_count - self.board.white_count


    def king_heuristic(self, turn, prev_black, prev_white):
        # gives a higher score to boards that are closer to attaining more kings
        kings_worth = 10
        mans_worth = 1
        eaten_worth = -2
        # TODO improve: change point values? calculate by specific pieces?
        score = 0
        player = PLAYERS[turn]
        board_row = self.board.row
        board_col = self.board.col
        board = self.board.board

        if turn == 1:
            # black
            score -= eaten_worth*(prev_black-self.board.black_count)
        else:
            # white
            score -= eaten_worth*(prev_white-self.board.white_count)

        for r in range(board_row):
            for c in range(board_col):
                piece = board[r][c]
                if piece.color == player:
                    #exists checker piece and color matches
                    if piece.is_king:
                        # piece is a king
                        score += kings_worth
                        # TODO update so score doesnt purely exist while king is alive?
                    else:
                        # piece is a man
                        if turn == 1:
                            # black
                            score += r*mans_worth
                        else:
                            # white
                            score += mans_worth*(board_row-r-1)
        return score


    def simulate(self, child):
        color = child.color
        winner = None
        counter = 0
        depth = 0

        while self.board.is_win(PLAYERS[color]) == 0 or depth <= DEPTH_LEVEL:
            moves = self.flatten(self.board.get_all_possible_moves(color))
            if len(moves) != 0:
                # player has moves

                # choose move based on king's heuristic
                prev_black = self.board.black_count
                prev_white = self.board.white_count
                maxScore = -1
                m = randint(0, len(moves)-1) # default random
                for i in range(len(moves)):
                    self.board.make_move(moves[i], color)
                    score = self.king_heuristic(color, prev_black, prev_white)
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

        if self.board.is_win(PLAYERS[color]) == 0:
            if self.count_heuristic() > 0:
                winner = 1
            else:
                winner = 2
        else:
            winner = self.board.is_win(PLAYERS[color])
            if winner == -1:
                # simulation ended with a tie: ties are considered wins
                winner = self.color
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
            # self.board.undo()

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
            if parent != -1:
                expand = self.expand(parent)
                result = self.simulate(expand)
                self.backProp(result, expand)
            else:
                for i in range(self.select_ctr):
                    self.board.undo()

        bestMove = None
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