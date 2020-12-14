from random import randint
from BoardClasses import Move
from BoardClasses import Board

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.

from random import seed
from datetime import datetime
from math import sqrt
from math import log
from copy import deepcopy

PLAYERS = {0: ".", 1: "B", 2: "W"}
EXPLORE_CONSTANT = 2
SIM_THRESHOLD = 10
DEFAULT_WIN = 8
DEFAULT_SIM = 10
FEW_MOVES = 4
SHORT_TURN = 8
FULL_TURN = 18
DEPTH_LEVEL = 16


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
        return self.getWins() / self.getSims() + EXPLORE_CONSTANT * sqrt(log(sp) / self.getSims())

    def getWinRate(self):
        if self.sims != 0:
            return self.wins / self.sims
        else:
            return -1

    def getWins(self):
        if self.sims <= SIM_THRESHOLD:
            return DEFAULT_WIN
        return self.wins

    def getSims(self):
        if self.sims <= SIM_THRESHOLD:
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
        self.startTurn = datetime.now()
        self.turnDuration = FULL_TURN
        seed(datetime.now())
        self.path = [] #AMAF

    def flatten(self, ini_list) -> list:
        return sum(ini_list, [])

    def isTimeLeft(self):
        time = datetime.now()
        if (time - self.startTurn).seconds < self.turnDuration:
            return True
        return False


    def select(self) -> Node:
        ptr = self.root
        maxNodes = []

        while len(ptr.children) != 0:
            # ptr is not a leaf; it has some to all children/moves
            moves = self.flatten(self.board.get_all_possible_moves(ptr.color))
            if len(ptr.children) < len(moves):
                # ptr has only expanded some children/moves
                return ptr
            if len(moves) == 0:
                # len(ptr.children) == 1, since its nonzero
                ptr = ptr.children[0]
            else:
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
                i = randint(0, len(maxNodes) - 1)
                maxNode = maxNodes[i]

                self.board.make_move(maxNode.move, ptr.color)
                self.path.append(maxNode.move) #AMAF
                ptr = maxNode
        return ptr


    def atLeastOneMove(self, color) -> bool:
        player = PLAYERS[color]
        board = self.board.board

        for r in range(self.board.row):
            for c in range(self.board.col):
                if board[r][c].color == player and len(board[r][c].get_possible_moves(self.board)) != 0:
                    # there exists a piece that has at least one move
                    return True
        return False


    def expand(self, node) -> Node:
        # if node has no children/moves, return itself
        moves = self.flatten(self.board.get_all_possible_moves(node.color))
        if len(moves) == 0:
            if self.board.is_win(PLAYERS[node.color]) != 0:
                # no moves since game ended
                return node
            else:
                # no moves since blocked
                if self.atLeastOneMove(self.opponent[node.color]):
                    # opponent has moves available, so make node here and return it
                    child = Node(self.opponent[node.color], -1, node)
                    node.children.append(child)
                    return child

        toMove = moves[0]
        childrenMoves = []
        for c in node.children:
            childrenMoves.append(c.move.seq)
        for m in moves:
            # looks for first move in list of all moves that hasn't been expanded
            if childrenMoves.count(m.seq) == 0:
                toMove = m
                break

        child = Node(self.opponent[node.color], toMove, node)
        node.children.append(child)
        self.board.make_move(toMove, node.color)
        self.path.append(toMove) #AMAF
        return child


    def count_heuristic(self) -> int:
        # heuristic counts for black-white
        return self.board.black_count - self.board.white_count


    def old_king_heuristic(self, turn, prev_black, prev_white):
        # gives a higher score to boards that are closer to attaining more kings
        kings_worth = 10
        mans_worth = 1
        eaten_worth = -2

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
                    # checker piece exists and color matches
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


    def king_heuristic(self):
        kings_worth = 10
        mans_worth = 1
        # eaten_worth = -2
        bScore = 0
        wScore = 0

        board_row = self.board.row
        board_col = self.board.col
        board = self.board.board

        # tempBoard = deepcopy(self.board)
        # tempBoard.undo()
        # bScore -= eaten_worth * (tempBoard.black_count - self.board.black_count)
        # wScore -= eaten_worth * (tempBoard.white_count - self.board.white_count)

        for r in range(board_row):
            for c in range(board_col):
                piece = board[r][c]
                if piece.color == "B": # BLACK
                    if piece.is_king:
                        bScore += kings_worth
                    else:
                        bScore += r*mans_worth
                if piece.color == "W": # WHITE
                    if piece.is_king:
                        wScore += kings_worth
                    else:
                        wScore += (board_row-r-1)*mans_worth
        return bScore, wScore # RETURN TUPLE OF SCORES, (BLACK, WHITE)


    def simulate(self, child):
        color = child.color
        winner = self.board.is_win(PLAYERS[color])
        depth = 0

        while winner == 0 and depth <= DEPTH_LEVEL:
            moves = self.flatten(self.board.get_all_possible_moves(color))
            if len(moves) != 0:
                # player has moves

                # 1. choose move randomly
                m = randint(0, len(moves) - 1)
                self.board.make_move(moves[m], color)
                self.path.append(moves[m]) #AMAF
                '''
                # 2. choose move based on king's heuristic
                prev_black = self.board.black_count
                prev_white = self.board.white_count
                maxScore = -1
                m = randint(0, len(moves) - 1)  # default random
                for i in range(len(moves)):
                    self.board.make_move(moves[i], color)
                    score = self.old_king_heuristic(color, prev_black, prev_white)
                    if score > maxScore:
                        maxScore = score
                        m = i
                    self.board.undo()
                self.board.make_move(moves[m], color)
                '''
            color = self.opponent[color]
            depth += 1
            winner = self.board.is_win(PLAYERS[color])

        if winner == 0:
            '''
            # 3. evaluate unfinished game with count heuristic
            if self.count_heuristic() > 0:
                winner = 1
            else:
                winner = 2
            '''
            # 4. evaluate unfinished game with king heuristic
            scoreBlack, scoreWhite = self.king_heuristic()
            if scoreBlack > scoreWhite:  # Compares black with white
                winner = 1
            elif scoreBlack == scoreWhite:
                # too hard to determine real winner (TBD)
                winner = 0.5
            else:
                winner = 2
        else:
            if winner == -1:
                # simulation ended with a tie: ties are considered wins
                winner = self.color
        return winner


    def backProp(self, result, child):
        '''
        # 1. original backprop
        while child != self.root:
            child.upSims()
            if result == 0.5 and child.color == self.color:
                # handle TBD results
                child.wins += result
            elif result != child.color:
                # originally the only if branch
                child.upWins()
            child = child.parent

        # child is the root
        child.upSims()
        if result != child.color:
            child.upWins()
        '''
        # 2. Attempt at AMAF:
        while child != self.root:
            child.upSims()
            if result == 0.5 and child.color == self.color:
                # handle TBD results
                child.wins += result
            elif result != child.color:
                # originally the only if branch; adjusted for AMAF (but not above)
                child.upWins()
                siblings = child.parent.children
                for sib in siblings:
                    if self.path.count(sib.move) != 0 and child.move != sib.move:
                        sib.upSims()
                        sib.upWins()
            child = child.parent

            # child is the root
        child.upSims()
        if result != child.color:
            child.upWins()

    def MCTS(self, moves) -> Move:
        if len(moves) <= FEW_MOVES:
            self.turnDuration = SHORT_TURN
        else:
            self.turnDuration = FULL_TURN

        boardOrig = deepcopy(self.board)
        while (self.isTimeLeft()):
            self.path.clear() #AMAF
            parent = self.select()
            expand = self.expand(parent)
            result = self.simulate(expand)
            self.backProp(result, expand)
            self.board = deepcopy(boardOrig)

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
        '''
        returns index of move m amongst children of the root
        if returns 1 + the len of the children, the move was not found (not yet expanded)
        '''
        i = 0
        while i != len(self.root.children):
            if self.root.children[i].move.seq == m.seq:
                break
            i += 1
        return i

    def get_move(self, move):
        self.startTurn = datetime.now()
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
                    # self.root.sims = self.root.wins #RESET
                else:
                    # add new child
                    new_root = Node(self.color, move, self.root)
                    self.root.children.append(new_root)
                    self.root = new_root
        else:
            self.color = 1
            self.root.color = 1

        # print("(pre) num real wins at root: ", self.root.wins)
        # print("(pre) num real sims at root: ", self.root.sims)
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
        # print("(post) num real wins at root: ", self.root.wins)
        # print("(post) num real sims at root: ", self.root.sims)
        # print("move chosen: ", move)

        # update root (own move)
        if len(moves) != 1:
            # set to existing child
            self.root = self.root.children[self.findIndexWithMove(move)]
            # self.root.sims = self.root.wins  #RESET
        else:
            # add new child
            new_root = Node(self.opponent[self.color], move, self.root)
            self.root.children.append(new_root)
            self.root = new_root

        return move