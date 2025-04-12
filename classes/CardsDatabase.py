import json

from classes.Card import Card
from classes.Deck import Deck


class CardsDatabase:
    def __init__(self):
        with open("./data/cards.json", "r", encoding="utf-8") as file:
            self.dictionary = json.load(file)

    def find_card(self, predicate):
        for card in self.dictionary:
            if predicate(card):
                return card

    def find_card_by_id(self, card_id):
        return self.find_card(lambda card: card["id"] == card_id)

    def find_card_by_name(self, card_name):
        return self.find_card(lambda card: card["name"] == card_name)

    def get_max_card_duplicates(self, card_id):
        return self.find_card_by_id(card_id)["count"]

    def create_verified_deck(self, data):
        processed = {}
        # id -> cnt, maxcnt, Card

        for item in data:
            card_id, count = item["id"], item["count"]

            if card_id not in processed:
                card_data = self.find_card_by_id(card_id)
                processed[card_id] = [0, card_data["count"], card_data]

            card = processed[card_id]
            card[0] += count
            if card[0] > card[1]:
                return False, card_id

            processed[card_id] = card

        deck = []
        for card in processed.values():
            for _ in range(card[0]):
                deck.append(Card(card[2]))

        return True, Deck(deck)

    def print_dict(self):
        print(self.dictionary)