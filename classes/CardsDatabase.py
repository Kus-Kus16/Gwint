import json

from classes.Card import Card
from classes.Commander import Commander
from classes.Deck import Deck

with open("./data/cards.json", "r", encoding="utf-8") as file:
    card_dict = json.load(file)

with open("./data/factions.json", "r", encoding="utf-8") as file:
    faction_dict = json.load(file)

with open("./data/muster.json", "r", encoding="utf-8") as file:
    muster_dict = json.load(file)

with open("./data/bond.json", "r", encoding="utf-8") as file:
    bond_dict = json.load(file)

with open("./data/recall.json", "r", encoding="utf-8") as file:
    recall_dict = json.load(file)

# Dictionary
def find_card(predicate):
    for card in card_dict:
        if predicate(card):
            return card

def find_card_by_id(card_id):
    return find_card(lambda card: card["id"] == card_id)

def find_card_by_name(card_name):
    return find_card(lambda card: card["name"] == card_name)

def get_max_card_duplicates(card_id):
    return find_card_by_id(card_id)["count"]

def find_commander_by_id(commander_id):
    for faction in faction_dict:
        for commander in faction["commanders"]:
            if commander["id"] == commander_id:
                return commander, faction["name"]

def create_verified_deck(data, commander_id):
    commander_data, faction = find_commander_by_id(commander_id)

    if commander_data is None:
        return False, None

    commander = Commander(commander_data, faction)

    processed = {}
    # id -> cnt, maxcnt, data

    for item in data:
        card_id, count = item["id"], item["count"]

        if card_id not in processed:
            card_data = find_card_by_id(card_id)
            faction_valid = True
            #faction_valid = card_data["faction"] == "Neutralne" or card_data["faction"] == faction

            if card_data is None or not faction_valid:
                return False, card_id

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

    return True, (Deck(deck), commander)

# Muster
def get_muster(card_id):
    return muster_dict[f"{card_id}"]

# Bond
def get_bond(card_id):
    return bond_dict[f"{card_id}"]

# Recall
def get_recall(card_id):
    card_id = recall_dict[f"{card_id}"]
    card_data = find_card_by_id(card_id)
    return Card(card_data)
