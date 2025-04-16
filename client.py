import json

from classes.CardsDatabase import CardsDatabase
from presenter.ConsoleGamePresenter import ConsoleGamePresenter
from presenter.GamePresenter import GamePresenter
from view.ConsoleView import ConsoleView


def main():
    #Deck crafting
    print("\n Enter deck 0 North/1 Nilfgaard: ")
    i = int(input())
    database = CardsDatabase()
    with open("./data/exampledecks.json", "r", encoding="utf-8") as file:
        deck = json.load(file)[i]

    commander = None
    valid, deck = database.create_verified_deck(deck)
    if not valid:
        raise ValueError("Illegal deck")

    try:
       presenter = ConsoleGamePresenter(deck, commander)
       presenter.run()
    except Exception as e:
        print(f"Error: {e}")

main()