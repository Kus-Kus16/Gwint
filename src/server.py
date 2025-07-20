import socket
import threading
from _thread import *

import pickle

from src.network.game_states import GameStates

SERVER_IP = "0.0.0.0"
PORT = 5555

games = {}
lock = threading.Lock()

def send(conn, data):
    conn.send(pickle.dumps(data))

def receive(conn):
    data = conn.recv(8192)

    if not data:
        return None, None # Disconnected

    return pickle.loads(data)

# Client managing thread
def threaded_client(conn, game_id, player_id):
    try:
        request, data = receive(conn)

        if request != "register":
            send(conn, ("error", ["illegal request"]))
            return

        with lock:
            if game_id not in games:
                send(conn, ("error", ["no_game"]))
                return

            game_state = games[game_id]

        game_state.add_state(player_id, data)
        send(conn, ("ok", [player_id, game_state.seed]))

        while True:
            request, data = receive(conn)
            if not request:
                break

            with lock:
                if not game_id in games:
                    send(conn, ("error", ["no_game"]))
                    break
                game_state = games[game_id]

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

        with lock:
            games.pop(game_id, None)

def main():
    id_counter = 0
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

                with lock:
                    id_counter += 1
                    game_id = (id_counter - 1) // 2

                    if id_counter % 2 == 1:
                        # Player 0
                        player_id = 0
                        games[game_id] = GameStates()
                        print(f"New game {game_id} created")
                    else:
                        # Player 1
                        if game_id not in games:
                            id_counter += 1
                            game_id = (id_counter - 1) // 2
                            player_id = 0
                            games[game_id] = GameStates()
                            print(f"New game {game_id} created, skipped invalid place")
                        else:
                            player_id = 1

                threading.Thread(target=threaded_client, args=(conn, game_id, player_id), daemon=True).start()
            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        s.close()

if __name__ == "__main__":
    main()