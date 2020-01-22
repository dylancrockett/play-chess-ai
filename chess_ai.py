from concurrent.futures import ThreadPoolExecutor
import chess
import random

# <> advance scoring tables <>
# white pawn modifier array
black_pawn_modifier = [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
                       5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,
                       1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0,
                       0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5,
                       0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0,
                       0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5,
                       0.5,  1.0, 1.0,  -2.0, -2.0,  1.0,  1.0,  0.5,
                       0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]

# white knight modifier array
black_knight_modifier = [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
                         -4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0,
                         -3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0,
                         -3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0,
                         -3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0,
                         -3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0,
                         -4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0,
                         -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]

# white bishop modifier array
black_bishop_modifier = [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
                         -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
                         -1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0,
                         -1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0,
                         -1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0,
                         -1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0,
                         -1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0,
                         -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]

# white rook modifier array
black_rook_modifier = [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
                       0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5,
                       -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
                       -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
                       -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
                       -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
                       -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
                       0.0,   0.0, 0.0,  0.5,  0.5,  0.0,  0.0,  0.0]

# white queen modifier array
black_queen_modifier = [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
                        -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
                        -1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
                        -0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
                        0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
                        -1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
                        -1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0,
                        -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]

# white king modifier array
black_king_modifier = [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                       -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                       -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                       -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
                       -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
                       -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
                       2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0,
                       2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0]

white_pawn_modifier = [ele for ele in reversed(black_pawn_modifier)]
white_knight_modifier = [ele for ele in reversed(black_knight_modifier)]
white_bishop_modifier = [ele for ele in reversed(black_bishop_modifier)]
white_rook_modifier = [ele for ele in reversed(black_rook_modifier)]
white_queen_modifier = [ele for ele in reversed(black_queen_modifier)]
white_king_modifier = [ele for ele in reversed(black_king_modifier)]


# a custom board for the AI that allows it to get values like all possible moves and the current strength of the board
class AIBoard(chess.Board):
    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        super().__init__(fen=fen)

    # get a list of the valid legal moves
    def valid_moves(self):
        return list(self.legal_moves)

    # gets a random valid move
    def random_move(self):
        return random.choice(self.valid_moves())

    # calculates the score of a given side
    def calculate_score(self, side_color):
        # the ongoing score of the board
        score = 0

        # go through each square
        for square in range(0, 64):
            # get the piece at the current square
            piece = self.piece_at(square)

            # pass if there is no piece on the square
            if piece is None:
                continue

            # if the current piece belongs to the side we are scoring then add it as a positive, otherwise a negative
            if piece.color == side_color:
                score += piece_score(piece.piece_type)
            if piece.color != side_color:
                score -= piece_score(piece.piece_type)

        # return the score for that player
        return score

    def calculate_advanced_score(self, side_color):
        # the ongoing score of the board
        score = 0

        # go through each square
        for square in range(0, 64):
            # get the piece at the current square
            piece = self.piece_at(square)

            # pass if there is no piece on the square
            if piece is None:
                continue

            # if the current piece belongs to the side we are scoring then add it as a positive, otherwise a negative
            if piece.color == side_color:
                score += advanced_piece_score(piece.piece_type, square, piece.color)
            if piece.color != side_color:
                score -= advanced_piece_score(piece.piece_type, square, piece.color)

        # return the score for that player
        return score

    # counts the number of pieces on the board
    def count_pieces(self):
        num = 0

        # go through each square
        for square in range(0, 64):
            # get the piece at the current square
            piece = self.piece_at(square)

            # pass if there is no piece on the square
            if piece is None:
                continue
            else:
                num += 1

        return num


# get a score based on a piece type
def piece_score(piece_type):
    if piece_type == chess.PAWN:
        return 10
    elif piece_type == chess.KNIGHT:
        return 30
    elif piece_type == chess.BISHOP:
        return 30
    elif piece_type == chess.ROOK:
        return 50
    elif piece_type == chess.QUEEN:
        return 90
    elif piece_type == chess.KING:
        return 900


# get a score based on a piece type and position and color
def advanced_piece_score(piece_type, position, color):
    if color == chess.WHITE:
        if piece_type == chess.PAWN:
            # pawn score at the given position based on the modifier + the value of the piece
            return white_pawn_modifier[position] + 10
        elif piece_type == chess.KNIGHT:
            # pawn score at the given position based on the modifier + the value of the piece
            return white_knight_modifier[position] + 35
        elif piece_type == chess.BISHOP:
            # pawn score at the given position based on the modifier + the value of the piece
            return white_bishop_modifier[position] + 35
        elif piece_type == chess.ROOK:
            # pawn score at the given position based on the modifier + the value of the piece
            return white_rook_modifier[position] + 52.5
        elif piece_type == chess.QUEEN:
            # pawn score at the given position based on the modifier + the value of the piece
            return white_queen_modifier[position] + 100
        elif piece_type == chess.KING:
            # pawn score at the given position based on the modifier + the value of the piece
            return white_king_modifier[position] + 1000
    elif color == chess.BLACK:
        if piece_type == chess.PAWN:
            # pawn score at the given position based on the modifier + the value of the piece
            return black_pawn_modifier[position] + 10
        elif piece_type == chess.KNIGHT:
            # pawn score at the given position based on the modifier + the value of the piece
            return black_knight_modifier[position] + 30
        elif piece_type == chess.BISHOP:
            # pawn score at the given position based on the modifier + the value of the piece
            return black_bishop_modifier[position] + 30
        elif piece_type == chess.ROOK:
            # pawn score at the given position based on the modifier + the value of the piece
            return black_rook_modifier[position] + 50
        elif piece_type == chess.QUEEN:
            # pawn score at the given position based on the modifier + the value of the piece
            return black_queen_modifier[position] + 90
        elif piece_type == chess.KING:
            # pawn score at the given position based on the modifier + the value of the piece
            return black_king_modifier[position] + 1000


class ChessAI:
    def __init__(self, color=None):
        # the board used for calculating AI moves
        self.board = AIBoard()

        # set the AI's color
        if color == "w":
            self.color = chess.WHITE
        elif color == "b":
            self.color = chess.BLACK

    # allow a change in the AI's color
    def change_color(self, color=None):
        # set the AI's color
        if color == "w":
            self.color = chess.WHITE
        elif color == "b":
            self.color = chess.BLACK

    # get the AI's move from a given fen
    def get_move(self, fen):
        return


# ai that returns a random move
class RandomAI(ChessAI):
    def __init__(self, color=None):
        super().__init__(color)

    def get_move(self, fen):
        self.board.set_fen(fen)

        return self.board.random_move()


# ai will choose the move that will result in it having the highest point value
class PointAI(ChessAI):
    def __init__(self, color=None):
        super().__init__(color)

    # get the AI's move from a given fen
    def get_move(self, fen):
        self.board.set_fen(fen)

        # keeps track of the move that results in the highest score for the AI and what that score is
        best_move = None
        best_score = -9999

        # keeps track of neutral moves, if the AI's best score is the same as it's current then choose from the neutral
        # move pool
        neutral_score = self.board.calculate_score(self.color)
        neutral_moves = []

        for move in self.board.legal_moves:
            # make the move
            self.board.push(move)

            # if the resulting score of the current move is higher than the best resulting score found so fare set it as
            # the new best move and score
            if self.board.calculate_score(self.color) > best_score:
                best_move = move
                best_score = self.board.calculate_score(self.color)
            elif self.board.calculate_score(self.color) == neutral_score:
                neutral_moves.append(move)

            # undo the move
            self.board.pop()

        # if no best move was found then choose from one of the neutral moves
        if best_score == neutral_score:
            try:
                best_move = random.choice(neutral_moves)
            except IndexError:
                best_move = self.board.random_move()

        return best_move


# ai will choose the move that will result in it having the highest point value (using advanced point calcs)
class AdvancedPointAI(ChessAI):
    def __init__(self, color=None):
        super().__init__(color)

    # get the AI's move from a given fen
    def get_move(self, fen):
        self.board.set_fen(fen)

        # keeps track of the move that results in the highest score for the AI and what that score is
        best_move = None
        best_score = -9999

        # keeps track of neutral moves, if the AI's best score is the same as it's current then choose from the neutral
        # move pool
        neutral_score = self.board.calculate_score(self.color)
        neutral_moves = []

        for move in self.board.legal_moves:
            # make the move
            self.board.push(move)

            # if the resulting score of the current move is higher than the best resulting score found so fare set it as
            # the new best move and score
            if self.board.calculate_advanced_score(self.color) > best_score:
                best_move = move
                best_score = self.board.calculate_advanced_score(self.color)
            elif self.board.calculate_score(self.color) == neutral_score:
                neutral_moves.append(move)

            # undo the move
            self.board.pop()

        # if no best move was found then choose from one of the neutral moves
        if best_score == neutral_score:
            try:
                best_move = random.choice(neutral_moves)
            except IndexError:
                best_move = self.board.random_move()

        return best_move


# minmax AI using basic scoring
class MiniMaxAI(ChessAI):
    def __init__(self, color=None):
        super().__init__(color)

    # get the AI's move from a given fen
    def get_move(self, fen):
        self.board.set_fen(fen)

        # keeps track of the move that results in the highest score for the AI and what that score is
        best_move = None
        best_score = -9999

        # keeps track of neutral moves, if the AI's best score is the same as it's current then choose from the neutral
        # move pool
        neutral_score = self.board.calculate_score(self.color)
        neutral_moves = []

        # find the best of the legal moves
        for move in self.board.legal_moves:
            # make the move
            self.board.push(move)

            # calculate the score
            score = self.minmax(2, -10000, 10000, False)

            # undo the move
            self.board.pop()

            # if the score is higher than the current best score then set the best move and best_score
            if best_score <= score:
                best_move = move
                best_score = score
            elif score == neutral_score:
                neutral_moves.append(move)

        # if no best move was found then choose from one of the neutral moves
        if best_score == neutral_score:
            try:
                best_move = random.choice(neutral_moves)
            except IndexError:
                best_move = self.board.random_move()

        return best_move

    # minmax search algorithm using alpha-beta pruning
    def minmax(self, depth, alpha, beta, is_maximizing):
        # if the depth is zero then calculate the point value of the position
        if depth == 0:
            score = self.board.calculate_score(self.color)

            return score

        # list of valid moves
        valid_moves = self.board.valid_moves()

        if is_maximizing:
            # keep track of the best score
            best_score = -9999

            for move in valid_moves:
                # make a move
                self.board.push(move)

                # check if the calculated score is higher than the current best score
                best_score = max(best_score, self.minmax(depth - 1, alpha, beta, not is_maximizing))

                # reverse the move
                self.board.pop()

                # alpha beta pruning return
                if best_score >= beta:
                    return best_score

                # calculate the new alpha
                alpha = max(alpha, best_score)

            # fallback return if no pruning occurs
            return best_score
        else:
            # keep track of the best score
            best_score = 9999

            for move in valid_moves:
                # make a move
                self.board.push(move)

                # check if the calculated score is higher than the current best score
                best_score = min(best_score, self.minmax(depth - 1, alpha, beta, not is_maximizing))

                # reverse the move
                self.board.pop()

                # alpha beta pruning return
                if best_score <= alpha:
                    return best_score

                # calculate the new beta
                beta = min(beta, best_score)

            # fallback return if no pruning occurs
            return best_score


# minmax AI using basic scoring
class AdvancedMiniMaxAI(ChessAI):
    def __init__(self, color=None):
        super().__init__(color)

    # get the AI's move from a given fen
    def get_move(self, fen):
        self.board.set_fen(fen)

        # keeps track of the move that results in the highest score for the AI and what that score is
        best_move = None
        best_score = -9999

        # keeps track of neutral moves, if the AI's best score is the same as it's current then choose from the neutral
        # move pool
        neutral_score = self.board.calculate_advanced_score(self.color)
        neutral_moves = []

        # number of valid moves
        num_pieces = self.board.count_pieces()

        # find the best of the legal moves
        for move in self.board.legal_moves:
            # make the move
            self.board.push(move)

            # calculate the score (use a different depth if there are less moves)
            if num_pieces > 10:
                score = self.minmax(2, -10000, 10000, False)
            else:
                score = self.minmax(3, -10000, 10000, False)

            # undo the move
            self.board.pop()

            # if the score is higher than the current best score then set the best move and best_score
            if best_score <= score:
                best_move = move
                best_score = score
            elif score == neutral_score:
                neutral_moves.append(move)

        # if no best move was found then choose from one of the neutral moves
        if best_score == neutral_score:
            try:
                best_move = random.choice(neutral_moves)
            except IndexError:
                best_move = self.board.random_move()

        return best_move

    # minmax search algorithm using alpha-beta pruning
    def minmax(self, depth, alpha, beta, is_maximizing):
        # if the depth is zero then calculate the point value of the position
        if depth == 0:
            score = self.board.calculate_advanced_score(self.color)

            return score

        # list of valid moves
        valid_moves = self.board.valid_moves()

        if is_maximizing:
            # keep track of the best score
            best_score = -9999

            for move in valid_moves:
                # make a move
                self.board.push(move)

                # check if the calculated score is higher than the current best score
                best_score = max(best_score, self.minmax(depth - 1, alpha, beta, not is_maximizing))

                # reverse the move
                self.board.pop()

                # alpha beta pruning return
                if best_score >= beta:
                    return best_score

                # calculate the new alpha
                alpha = max(alpha, best_score)

            # fallback return if no pruning occurs
            return best_score
        else:
            # keep track of the best score
            best_score = 9999

            for move in valid_moves:
                # make a move
                self.board.push(move)

                # check if the calculated score is higher than the current best score
                best_score = min(best_score, self.minmax(depth - 1, alpha, beta, not is_maximizing))

                # reverse the move
                self.board.pop()

                # alpha beta pruning return
                if best_score <= alpha:
                    return best_score

                # calculate the new beta
                beta = min(beta, best_score)

            # fallback return if no pruning occurs
            return best_score


class MonteCarloAI(ChessAI):
    def __init__(self, color=None):
        super().__init__(color)

    def get_move(self, fen):
        self.board.set_fen(fen)

        best_score = 0
        best_move = None
        neutral_moves = []

        # find the best of the legal moves
        for move in self.board.legal_moves:
            # make the move
            self.board.push(move)

            # score the move
            score = self.monte_carlo(10)

            # undo the move
            self.board.pop()

            # if the score is higher than the current best score then set the best move and best_score
            if best_score <= score:
                best_move = move
                best_score = score

        # if no best move was found then choose from one of the neutral moves
        if best_score == 0:
            best_move = self.board.random_move()

        return best_move

    # execute a monte carlo search on the board
    def monte_carlo(self, games):
        results = 0

        for x in range(1, games):
            results += self.play_random_game()

        return results / games

    # plays a random game from a given position and returns the result
    def play_random_game(self):


        return
