import json
import time

from classes.CardsDatabase import CardsDatabase
from classes.Game import Game
from classes.Player import Player
from network.network import Network

def play_game(deck, commander):
    def handle_turn(player_id):
        nonlocal game_state

        print("\n\n" + str(game.players[1- my_id]) + "\n\n")
        print(game.to_string(my_id))
        own_turn = player_id == my_id

        if own_turn:
            print("\n Enter card id: ")
            card_id = int(input())
            print("\n Enter row (close, ranged, siege): ")
            row = input()
        else:
            response, data = n.send(("waiting", []))
            if response == "ok":
                return True
            card_id, row = data

        if row == "pass":
            valid = game.pass_round(player_id)
        else:
            valid = game.play_card(player_id, card_id, row)

        if not valid:
            return False

        if own_turn:
            n.send(("play-card", [card_id, row]))

        if game.current_player_id == my_id:
            game_state = "playing"
        elif game.current_player_id == 1 - my_id:
            game_state = "waiting"
        else:
            print(game.round_history)
            game_state = "game-over"

        return True


    n = Network()
    response, data = n.send(("register", [deck, None]))

    if response == "ok":
        my_id, seed = data
    else:
        raise ValueError("No response")

    me = Player(deck, commander)
    opponent = None
    game = None
    game_state = 'waiting-for-game'

    while True:
        time.sleep(1)
        # Sprawdź status gry
        match game_state:
            case "waiting-for-game":
                response, data = n.send(("waiting-for-game", []))

                if response == "start-game":
                    opponent = Player(data[0], data[1])
                    game = Game(seed)
                    if my_id == 0:
                        game.add_player(me)
                        game.add_player(opponent)
                    else:
                        game.add_player(opponent)
                        game.add_player(me)
                    game_state = 'starting-game'

            case "starting-game":

                # Scoia'tael choosing here
                game.start_game()
                game_state = 'playing' if game.current_player_id == my_id else "waiting"

            case "playing":
                handle_turn(my_id)

            case "waiting":
                if not handle_turn(1 - my_id):
                    raise ValueError("Illegal opponent move")

            case "game-over":
                print("\nExit / Rematch?")
                rematch = True if input().lower() == "rematch" else False
                n.send(("rematch", [rematch]))

                if not rematch:
                    return

                game_state = "waiting-for-endgame"

            case "waiting-for-endgame":
                response, data = n.send(("waiting-for-endgame", []))

                if response == "ok":
                    continue

                if data[0]:
                    game.set_seed(data[1])
                    game_state = 'starting-game'
                else:
                    return

def main():
    #Deck crafting
    print("\n Enter deck 0 North/1 Nilfgaard: ")
    i = int(input())
    database = CardsDatabase()
    with open("./data/exampledecks.json", "r", encoding="utf-8") as file:
        deck = json.load(file)[i]

    valid, deck = database.create_verified_deck(deck)
    if not valid:
        raise ValueError("Illegal deck")

    #Connection
    try:
       play_game(deck, None)
    except Exception as e:
        print(f"Error: {e}")

main()