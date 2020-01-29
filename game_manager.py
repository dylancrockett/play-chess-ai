import chess
import secrets
import enum
import random
import time
import datetime
import threading


# definitions for the results of a game
class GameState(enum.Enum):
    STALEMATE = "stalemate"
    INSUFFICIENT_MATERIAL = "insufficient_material"
    THREEFOLD = "threefold"
    FIVEFOLD = "fivefold"
    FIFTY_MOVES = "fifty_moves"
    SEVENTYFIVE_MOVES = "seventyfive_moves"
    CHECKMATE = "checkmate"
    NONE = "none"


# Working on updating so that an AI can play another AI by having the AI inherit from the player class
# player class for storing player data in the game manager
class Player:
    def __init__(self, username="Guest", player_id="guest", color=None):
        self.username = username
        self.id = player_id
        self.avatar_url = "/static/img/avatars/guest/cupcake.png"

        self.color = color
        return

    # overwritten by AI player type
    def get_move(self, fen):
        return None

    # change the Player's color
    def set_color(self, color):
        self.color = color

    def data(self):
        return {
            "name": self.username,
            "id": self.id,
            "avatar_url": self.avatar_url,
            "color": self.color
        }


# AI class for storing AI data in the game manager (also stores the AI engine)
class AI(Player):
    def __init__(self, ai, username="AI", player_id="ai", color=None):
        super().__init__(username, player_id, color)
        self.ai = ai
        self.username = username
        self.id = player_id
        self.avatar_url = "/static/img/avatars/guest/cupcake.png"

        self.color = color
        return

    # get the ai's next move based on a fen string
    def get_move(self, fen):
        return self.ai.get_move(fen=fen)

    # change the AI's color
    def set_color(self, color):
        self.color = color
        self.ai.change_color(color)

    # return the AI's data as a dict
    def data(self):
        return {
            "name": self.username,
            "id": self.id,
            "avatar_url": self.avatar_url,
            "color": self.color
        }


# manages all ongoing games within the app
class GameManager:
    class Game:
        class CustomBoard(chess.Board):
            def __init__(self):
                super().__init__()
                self.reset()

            def verify_fen(self, fen):
                if fen == self.fen():
                    return True
                else:
                    return False

        def __init__(self, player_data, ai_data, player_color, ai_game):
            self.ai_game = ai_game

            # session information
            self.session_url = secrets.token_urlsafe(16)
            self.session_secret = secrets.token_urlsafe(32)

            # a datetime which represents the time at which the last action was made in this game
            self.last_action = datetime.datetime.now()

            # game board
            self.board = self.CustomBoard()

            # player object
            self.player = player_data
            self.ai = ai_data

            # set players color and create the ai
            if player_color == "w":
                self.player.set_color("w")
                self.ai.set_color("b")
            elif player_color == "b":
                self.player.set_color("b")
                self.ai.set_color("w")
            else:
                # randomize the colors
                if bool(random.getrandbits(1)):
                    self.player.set_color("w")
                    self.ai.set_color("b")
                else:
                    self.player.set_color("b")
                    self.ai.set_color("w")
            return

        # make a move using the ai
        def ai_move(self):
            if self.ai_game:
                if self.board.turn == chess.WHITE:
                    print("MAKING WHITE MOVE USING: " + self.player.username)
                    try:
                        move = self.player.get_move(self.fen())
                    except Exception as e:
                        print(e)
                else:
                    print("MAKING WHITE MOVE USING: " + self.ai.username)
                    move = self.ai.get_move(self.fen())
            else:
                # the move the ai wants to make
                move = self.ai.get_move(self.fen())

            # in the case the move is None
            if move is None:
                return None

            print("AI MOVE: " + move.uci())

            # make the move
            self.board.push(move)

            # return the string value of the move
            return move.uci()

        # resets the last_action datetime value to the current time
        def reset_timeout(self):
            self.last_action = datetime.datetime.now()

        # checks if there is a special state of the board
        def current_state(self):
            if self.board.is_stalemate():
                return "stalemate"
            elif self.board.is_insufficient_material():
                return "insufficient_material"
            elif self.board.can_claim_threefold_repetition():
                return "threefold"
            elif self.board.can_claim_fifty_moves():
                return "fifty_moves"
            elif self.board.is_fivefold_repetition():
                return "fivefold"
            elif self.board.is_seventyfive_moves():
                return "seventyfive_moves"
            elif self.board.is_checkmate():
                return "checkmate"
            else:
                return "none"

        # attempt to make a move, if the move is not valid then return false
        def make_move(self, move):
            # set the promotion
            move.promotion = chess.QUEEN

            # check if the move is valid with promotion
            if move in self.board.legal_moves:
                # if the move is legal then register it
                self.board.push(move)

                # return the move was validated
                return True

            # if promotion move fails then try move without promotion
            move.promotion = None

            # check if the move is valid without promotion
            if move in self.board.legal_moves:
                # if the move is legal then register it
                self.board.push(move)

                # return the move was validated
                return True
            else:
                # return that the move was not validated
                return False

        # check if a move is a valid move returns a bool
        def check_move(self, move):
            # set the promotion
            move.promotion = chess.QUEEN

            # check if the move is valid with promotion
            if move in self.board.legal_moves:
                # return the move was validated
                return True

            # if promotion move fails then try move without promotion
            move.promotion = None

            # check if the move is valid without promotion
            if move in self.board.legal_moves:
                # return the move was validated
                return True
            else:
                # return that the move was not validated
                return False

        # compare the fen of the client board and the server board and update based on that
        def fen(self):
            return self.board.fen()

        # checks if the game session has timed out returns a bool
        def session_timed_out(self):
            time_delta = datetime.datetime.now() - self.last_action

            # check if the difference between the current time and the time since the last action is 15 min or more
            if time_delta >= datetime.timedelta(minutes=15):
                return True
            else:
                return False

        # return the player data as a dict
        def game_info(self):
            return {
                "session_url": self.session_url,
                "session_secret": self.session_secret,
                "current_fen": self.board.fen(),
                "state": self.current_state(),
                "player": self.player.data(),
                "ai": self.ai.data()
            }

        # return the game session info as a tuple (session_url, session_secret)
        def session_info(self):
            return (
                self.session_url,
                self.session_secret
            )

    def __init__(self, timeout_check_delay = 15):
        # the delay between checking if games are still alive
        self.timeout_check_delay = timeout_check_delay

        # a list of current ongoing games
        self.__games = []

        # a list of background task threads
        self.__threads = []

        # start background threads
        self.__start_threads()

    # check if a given session url has a matching game in the manager
    def check_session(self, session_url):
        # check if a given session_url exists
        for game in self.__games:
            if game.session_url == session_url:
                return True
        return False

    # creates a new game with some given player data
    def create_game(self, player_data, ai_data, player_color="r", ai_game=False):
        # create a new game
        new_game = self.Game(player_data, ai_data, player_color, ai_game)

        # add the game to the list
        self.__games.append(new_game)

        # return the new games session info
        return new_game.session_info()

    # get the player data of a given game given its url token, returns None if the url doesnt match a current game
    def player_data(self, session_url):
        for game in self.__games:
            if game.session_url == session_url:
                return game.game_info()
        return None

    # verify a move sent by a client
    def verify_move(self, session_url, move):
        # find the game with the matching session_url
        for game in self.__games:
            # resets the game's timeout counter
            game.reset_timeout()

            if game.session_url == session_url:
                # verify the move
                verification_status = game.make_move(
                    chess.Move.from_uci(move["move"]["source"] + move["move"]["target"]))

                # get the board state
                board_state = game.current_state()

                # board fen
                board_fen = game.board.fen()

                return verification_status, board_state, board_fen
        return None

    # makes a move using the ai
    def ai_move(self, session_url):
        for game in self.__games:
            if game.session_url == session_url:
                # resets the game's timeout counter
                game.reset_timeout()

                # has the ai make a move, returns the string of the move
                move = game.ai_move()

                return game.fen(), game.current_state(), move
        return None

    # delete a given game
    def delete_game(self, session_url):
        for game in self.__games:
            if game.session_url == session_url:
                self.__games.remove(game)

        return

    # returns the fen of a given board
    def get_fen(self, session_url):
        for game in self.__games:
            if game.session_url == session_url:
                return game.board.fen()
        return None

    # checks the timeout of games and will delete the game if it has timed out
    def __check_timeouts(self):
        while True:
            # delay between checks
            time.sleep(self.timeout_check_delay)

            # check if each game has timed out
            for game in self.__games:
                # if the game has  timed out remove it from the list of ongoing games
                if game.session_timed_out():
                    self.__games.remove(game)

    # starts all background task threads of the manager
    def __start_threads(self):
        # add the thread which checks the game timeouts
        self.__threads.append(threading.Thread(target=self.__check_timeouts, daemon=False))

        # start all of the threads
        for thread in self.__threads:
            thread.start()



