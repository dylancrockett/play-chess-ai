from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, emit, join_room
import secrets
import chess_ai
from concurrent.futures import ThreadPoolExecutor
import game_manager as gm

"""
    Once the flask app is launched go to the following url in a web browser to play an AI: 'localhost:5000'
    > The page styles are designed and tested using Chrome 
    > There are technically 5 different AI's implemented (including a random AI)
    > Currently you cannot play an AI against an AI (desired feature if enough time)
    
    > This project makes use of the following non-standard libraries:
        - flask - web app library used to display web pages
        - flask-socketio.py - a socketio extension for the flask library allowing for easy socket communications 
        - chess.py - used as the server chess engine for validating moves and getting a list of valid moves for the AI
        - jquery.js - used for web page programming and is a req for chessboard.js
        - chessboard.js - used for client side chess board visualization and interactions
        - chess.js - used as a chess engine on the user side to calculate valid moves and prevent invalid ones
        - socket.io.js - used for the client side socketio communications 
"""

# flask app config and instance creation
app = Flask("Chess AI", template_folder="templates",
            static_folder="static")
app.config['SECRET_KEY'] = secrets.token_urlsafe(32)

# socketIO config
socket_io = SocketIO(app, async_mode='threading')

# create
manager = gm.GameManager()

# thread pool
pool = ThreadPoolExecutor(max_workers=32)


@app.route('/')
def homepage():
    return redirect('/play')


@app.route('/play')
def play():
    return render_template("choose-ai.html")


@app.route('/new/player-vs-ai/<ai_id>')
def create_player_vs_ai_game(ai_id):
    ai_player = get_ai_by_name(ai_id)

    if ai_player is None:
        return "Invalid AI"

    guest_player = gm.Player()

    # create a player-vs-ai game
    session_url, session_secret = manager.create_game(guest_player, ai_player)

    return redirect('/play/player-vs-ai/' + session_url)


@app.route('/new/ai-vs-ai')
def create_ai_vs_ai_game():
    try:
        white_ai = get_ai_by_name(request.args["white_ai"])
        black_ai = get_ai_by_name(request.args["black_ai"])
    except KeyError:
        return "Invalid URL"

    # create a ai-vs-ai game
    session_url, session_secret = manager.create_game(white_ai, black_ai, player_color='w', ai_game=True)

    return redirect('/play/ai-vs-ai/' + session_url)


@app.route('/play/player-vs-ai/<game_session>')
def player_vs_ai(game_session):
    if not manager.check_session(game_session):
        return redirect('/play')

    return render_template("play/player-ai.html", data=manager.player_data(game_session))


@app.route('/play/ai-vs-ai/<game_session>')
def ai_vs_ai(game_session):
    if not manager.check_session(game_session):
        return redirect('/play')

    return render_template("play/ai-ai.html", data=manager.player_data(game_session))


@socket_io.on('verify_move')
def verify_move(data):
    verified, state, fen = manager.verify_move(data["session_url"], data)

    if state != "none":
        response = {
            "fen": fen,
            "state": state
        }

        # update the player
        emit('update_fen', response)

        print("Game over! Reason: " + state)

        # delete the game now that it is over (to conserve memory)
        manager.delete_game(data["session_url"])
        return

    # correct the players board if the move was no verified
    if not verified:
        response = {
            "fen": fen,
            "state": state
        }

        # update the player
        emit('update_fen', response)
    else:
        # make the ai move
        pool.submit(threaded_ai_move, data)

    return


@socket_io.on('get_fen')
def get_fen(data):
    response = {
        "fen": manager.get_fen(data["session_url"])
    }

    emit('give_fen', response)
    return


@socket_io.on('ai_move')
def ai_move(data):
    # make the ai move
    pool.submit(threaded_ai_move, data)
    return


@socket_io.on('join_game')
def on_join(data):
    join_room(data["session_url"])


def threaded_ai_move(data):
    # make the ai move
    fen, state, move = manager.ai_move(data["session_url"])

    if move is None:
        return

    response = {
        "fen": fen,
        "state": state,
        "move": move
    }

    # update the player
    socket_io.emit('update_fen', response, room=data["session_url"])
    return


def get_ai_by_name(ai_name):
    if ai_name == "random":
        ai = gm.AI(
            chess_ai.RandomAI(),
            "Random AI",
        )
    elif ai_name == "point":
        ai = gm.AI(
            chess_ai.PointAI(),
            "Point AI",
        )
    elif ai_name == "advanced_point":
        ai = gm.AI(
            chess_ai.AdvancedPointAI(),
            "Advanced Point AI",
        )
    elif ai_name == "minimax":
        ai = gm.AI(
            chess_ai.MiniMaxAI(),
            "Minmax AI",
        )
    elif ai_name == "advanced_minimax":
        ai = gm.AI(
            chess_ai.AdvancedMiniMaxAI(),
            "Advanced Minmax AI",
        )
    else:
        ai = None

    return ai


if __name__ == '__main__':
    socket_io.run(app=app)

