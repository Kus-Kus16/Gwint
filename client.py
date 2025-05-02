import json
import threading

from classes import CardsDatabase
from presenter.GamePresenter import GamePresenter
from view.PyGameView import PygameView


def main():
    #Deck crafting
    # print("\n Enter deck 0 North/1 Nilfgaard: ")
    # i = int(input())
    with open("./data/exampledecks.json", "r", encoding="utf-8") as file:
        deck = json.load(file)[2]

    commander = None
    valid, deck = CardsDatabase.create_verified_deck(deck)
    if not valid:
        raise ValueError("Illegal deck")

    try:
        view = PygameView()
        presenter = GamePresenter(deck, commander, view)
        view.set_observer(presenter)
        threading.Thread(target=presenter.run, daemon=True).start()
        view.run()
    except Exception as e:
        print(f"Error: {e}")

main()