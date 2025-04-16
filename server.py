import socket
from _thread import *

import pickle

from network.GameStates import GameStates

server = "192.168.1.44"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection, Server Started")

games = {}
id_counter = 0

# Funkcja zarządzająca klientami
def threaded_client(conn, game_id, player_id):
    global id_counter

    def send(data):
        conn.send(pickle.dumps(data))

    def receive():
        return pickle.loads(conn.recv(2048))

    try:
        request, data = receive()
        if request != "register":
            send( ("error", ["illegal request"]) )

        game_state = games[game_id]
        game_state.add_state(player_id, data)
        send( ("ok", [player_id, game_state.seed]) )

        while True:
            request, data = receive()
            if not request:
                break

            if not game_id in games:
                send( ("error", ["no_game"]) )
                break

            match request:
                case "waiting-for-game":
                    opponent_state = game_state.get_state(1 - player_id)
                    send( ("ok", []) if opponent_state is None else ("start-game", opponent_state) )

                case "play":
                    game_state.add_state(player_id, data)
                    send( ("ok", []) )

                case "waiting":
                    opponent_state = game_state.get_state(1 - player_id)
                    send( ("ok", []) if opponent_state is None else ("play", opponent_state) )

                case "rematch":
                    game_state.reseed()
                    game_state.add_state(player_id, data)
                    send( ("ok", []) )

                case "waiting-for-endgame":
                    opponent_state = game_state.get_state(1 - player_id)
                    send( ("ok", []) if opponent_state is None else ("replay-game", opponent_state + [game_state.seed]) )

                case _:
                    send(("error", ["illegal request"]) )

    except Exception as e:
        print(f"Błąd w połączeniu: {e}")

    print("Connection lost")
    games.pop(game_id, None)
    id_counter -= 1
    conn.close()

# Client connects
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    id_counter += 1
    game_id = (id_counter - 1) // 2
    if id_counter % 2 == 1:
        player_id = 0
        games[game_id] = GameStates()
        print("New game created")
    else:
        player_id = 1

    start_new_thread(threaded_client, (conn, game_id, player_id))