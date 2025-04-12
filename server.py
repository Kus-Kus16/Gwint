import socket
from _thread import *

from classes.CardsDatabase import CardsDatabase
from classes.Game import Game
from classes.Player import Player
from classes.Row import RowType

import pickle


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
database = CardsDatabase()

# Funkcja zarządzająca klientami
def threaded_client(conn, game_id):
    global id_counter

    def send(data):
        conn.send(pickle.dumps(data))

    def receive():
        return pickle.loads(conn.recv(2048))

    try:
        request, data = receive()
        if request != "connect":
            raise ValueError("Illegal request")

        valid, deck = database.create_verified_deck(data[0])
        if not valid:
            send( ("error", [f"deck_invalid_{deck}"]) )

        game = games[game_id]
        player_id = game.add_player(Player(deck, None))

        send( ("ok", [player_id]) if player_id is not None else ("error", ["game_full"]) )

        if player_id == 1:
            game.start_game()

        while True:
            request, data = receive()
            if not request:
                break

            if not game_id in games:
                send( ("error", ["no_game"]) )
                break

            if request == "get_status":
                send( ("ok", ["game_started" if game.ready else "game_waiting"]) )

            elif request == "get_game":
                send( ("ok", [game]) )

            elif request == "play_card":
                card_id, row = data
                card_id = int(card_id)
                if row == "pass":
                    result =  game.pass_round(player_id)
                else:
                    result = game.play_card(player_id, card_id, RowType[row.upper()])

                send( ("ok", [result]) )
            else:
                raise ValueError("Błędny format danych")

    except Exception as e:
        print(f"Błąd w połączeniu: {e}")

    print("Connection lost")
    games.pop(game_id, None)
    id_counter -= 1
    conn.close()

# Client connects
while True:
    new_connection, addr = s.accept()
    print("Connected to:", addr)

    id_counter += 1
    new_game_id = (id_counter - 1) // 2
    if id_counter % 2 == 1:
        games[new_game_id] = Game(new_game_id)
        print("New game created")

    start_new_thread(threaded_client, (new_connection, new_game_id))