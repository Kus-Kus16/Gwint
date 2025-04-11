import socket
from _thread import *
import json

from classes.Card import Card
from classes.Deck import Deck
from classes.Game import Game
from classes.Player import Player
from classes.Row import RowType

import pickle


server = "192.168.243.83"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection, Server Started")

players_connected = 0
connections = []
game = None
players = {}

# Funkcja tworząca nową grę
def start_game():
    global game, players

    with open("./data/cards.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    cards = [Card(d) for d in data]
    card_holder0 = Deck(cards[0:10])
    card_holder1 = Deck(cards[20:30])

    player0 = Player(card_holder0, None)
    player1 = Player(card_holder1, None)
    game = Game(1)

    player0.id = game.add_player(player0)
    player1.id = game.add_player(player1)
    game.start_game()

    player0.draw_cards(10)
    player1.draw_cards(10)

    players = {0: player0, 1: player1}
    print("Game started!")

# Funkcja zarządzająca klientami
def threaded_client(conn):
    global players_connected, game
    try:
        player_id = players_connected
        players_connected += 1
        connections.append(conn)
        data = conn.recv(2048).decode()
        if data == "connect":
            conn.send(str.encode(str(player_id)))

        if players_connected == 2 and game is None:
            start_game()

        while True:
            data = conn.recv(2048).decode()
            if not data:
                break
            if data == "status":
                if game is not None:
                    conn.send(str.encode("game_started"))
                else:
                    conn.send(str.encode(str(players_connected)))
            elif data == "get_game":
                serialized_data = pickle.dumps(game)
                #print(f"Rozmiar danych: {len(serialized_data)} bajtów")
                conn.send(serialized_data)
            elif ":" in data:
                card_id, row = data.split(":")
                card_id = int(card_id)
                if row == "pass":
                    if game.pass_round(players[game.current_player_id]):
                        conn.send(str.encode("success"))
                    else:
                        conn.send(str.encode("FALSE"))
                else:
                    if game.play_card(players[game.current_player_id], card_id, RowType[row.upper()]):
                        conn.send(str.encode("success"))
                    else:
                        conn.send(str.encode("FALSE"))
            else:
                raise ValueError("Błędny format danych")

    except Exception as e:
        print(f"Błąd w połączeniu: {e}")

    players_connected -= 1
    if conn in connections:
        connections.remove(conn)
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn,))