import json

from classes.Card import Card
from classes.Deck import Deck

with open("./data/cards.json", "r", encoding="utf-8") as file:
    dictionary = json.load(file)

with open("./data/muster.json", "r", encoding="utf-8") as file:
    muster_dict = json.load(file)

with open("./data/bond.json", "r", encoding="utf-8") as file:
    bond_dict = json.load(file)

# Dictionary
def find_card(predicate):
    for card in dictionary:
        if predicate(card):
            return card

def find_card_by_id(card_id):
    return find_card(lambda card: card["id"] == card_id)

def find_card_by_name(card_name):
    return find_card(lambda card: card["name"] == card_name)

def get_max_card_duplicates(card_id):
    return find_card_by_id(card_id)["count"]

def create_verified_deck(data):
    ## TODO
    processed = {}
    # id -> cnt, maxcnt, Card

    for item in data:
        card_id, count = item["id"], item["count"]

        if card_id not in processed:
            card_data = find_card_by_id(card_id)
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

# Muster
def get_muster(card_id):
    return muster_dict[f"{card_id}"]

# Bond
def get_bond(card_id):
    return bond_dict[f"{card_id}"]
