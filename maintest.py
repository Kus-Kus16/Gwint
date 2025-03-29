import json

from classes.Card import Card
from classes.Deck import Deck
from classes.Game import Game
from classes.Player import Player
from classes.Row import RowType

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

while True:
    current_player = game.current_player
    if current_player is None:
        break

    current_player_id = current_player.id

    print(game.game_tostring(current_player_id))

    print("\n Enter card id: ")
    card_id = int(input())
    print("\n Enter row (close, ranged, siege): ")
    row = input()

    if row == "pass":
        game.pass_round(players[current_player_id])
    else:
        game.play_card(players[current_player_id], card_id, RowType[row.upper()])
    print("-" * 30)


# game.play(player0, 9, RowType.CLOSE)
# print(game.game_tostring(0))
# print("-"*30)
#
# game.play(player1, 10, RowType.SIEGE)
# print(game.game_tostring(0))
# print("-"*30)