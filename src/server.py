import socket
import threading
from _thread import *

import pickle

from src.network.game_states import GameStates

SERVER_IP = "0.0.0.0"
PORT = 5555

games = dict()
lock = threading.Lock()

def send(conn, data):
    conn.send(pickle.dumps(data))

def receive(conn):
    data = conn.recv(8192)

    if not data:
        return None, None # Disconnected

    return pickle.loads(data)

# Client managing thread
def threaded_client(conn):
    try:
        request, data = receive(conn)

        if request != "register" or not data:
            send(conn, ("error", ["illegal request"]))
            return

        with lock:
            game_id = data[:1][0]
            game_state = games.get(game_id)
            if game_state is None:
                game_state = GameStates()
                games[game_id] = game_state
                player_id = 0
            elif game_state.started:
                send(conn, ("error", ["game id already in use"]))
                return
            else:
                game_state.started = True
                player_id = 1

        game_state.add_player()
        game_state.add_state(player_id, data[1:])
        send(conn, ("ok", [player_id, game_state.seed]))

        while True:
            request, data = receive(conn)
            if not request:
                break

            with lock:
                game_state = games.get(game_id)
                if not game_state or (game_state.started and game_state.player_count < 2):
                    send(conn, ("error", ["no_game"]))
                    break

            match request:
                case "waiting": # For game, for redraw, for move, for endgame
                    opponent_state = game_state.get_state(1 - player_id)
                    send(conn, ("ok", []) if opponent_state is None else ("response", opponent_state))

                case "play":
                    game_state.add_state(player_id, data)
                    send(conn, ("ok", []))

                case "rematch":
                    game_state.reseed()
                    game_state.add_state(player_id, data)
                    send(conn, ("ok", [game_state.seed]))

                case _:
                    send(conn, ("error", ["illegal request"]))

    except (socket.error, pickle.PickleError, EOFError) as e:
        print(f"Communication error with player {player_id} of game {game_id}: {e}")

    finally:
        print(f"Connection lost to player {player_id} of game {game_id}")
        conn.close()
        game_state.remove_player()

        with lock:
            if game_state.player_count == 0:
                # last player
                del games[game_id]

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((SERVER_IP, PORT))
        s.listen()
        s.settimeout(1.0)
        print(f"Server started on port {PORT}, waiting for connections")
    except socket.error as e:
        print(f"Binding error: {e}")
        return

    try:
        while True:
            try:
                # Client connects
                conn, addr = s.accept()
                print(f"Connected to: {addr}")
                threading.Thread(target=threaded_client, args=(conn,), daemon=True).start()
            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        s.close()

if __name__ == "__main__":
    main()