import json
import threading

from classes.CardsDatabase import CardsDatabase
from presenter.ConsoleGamePresenter import ConsoleGamePresenter
from presenter.GamePresenter import GamePresenter
from view.ConsoleView import ConsoleView
from view.PyGameView import PygameView


def main():
    #Deck crafting
    # print("\n Enter deck 0 North/1 Nilfgaard: ")
    # i = int(input())
    database = CardsDatabase()
    with open("./data/exampledecks.json", "r", encoding="utf-8") as file:
        deck = json.load(file)[0]

    commander = None
    valid, deck = database.create_verified_deck(deck)
    if not valid:
        raise ValueError("Illegal deck")

    try:

        view = PygameView()
        presenter = GamePresenter(deck, commander, view)
        threading.Thread(target=presenter.run, daemon=True).start()
        view.run()
    except Exception as e:
        print(f"Error: {e}")

main()