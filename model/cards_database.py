import json

from model.card import Card
from model.commander import Commander
from model.deck import Deck

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

with open("./data/find.json", "r", encoding="utf-8") as file:
    find_dict = json.load(file)

def faction_to_nickname(fullname):
    mapping = {
        "Królestwa Północy": "polnoc",
        "Cesarstwo Nilfgaardu": "nilfgaard",
        "Potwory": "potwory",
        "Scoia'tael": "scoiatael",
        "Skellige": "skellige",
    }
    return mapping.get(fullname)

# Dictionary
def find_card(predicate):
    for card in card_dict:
        if predicate(card):
            return card

def find_card_by_id(card_id):
    return find_card(lambda card: card["id"] == card_id)

def find_card_by_name(card_name):
    return find_card(lambda card: card["name"] == card_name)

def find_commander_by_id(commander_id):
    for faction in faction_dict:
        for commander in faction["commanders"]:
            if commander["id"] == commander_id:
                return commander, faction["name"]

def create_verified_deck(data, commander_id):
    commander_data, faction = find_commander_by_id(commander_id)

    if commander_data is None:
        raise ValueError(f"Commander: {commander_id} does not exist")

    commander_data["faction"] = faction
    commander = Commander(commander_data)

    processed = {}
    units = 0
    special = 0

    for item in data:
        card_id, count = item["id"], item["count"]

        if card_id not in processed:
            card_data = find_card_by_id(card_id)

            if card_data is None:
                raise ValueError(f"Card: {card_id} does not exist")

            faction_valid = card_data["faction"] in ("Neutralne", faction)

            if not faction_valid:
                raise ValueError(f"Card: {card_id}:{card_data['name']} does not belong to {faction}")

            processed[card_id] = {
                "count": 0,
                "max_count": card_data["count"],
                "data": card_data,
                "object": Card(card_data)
            }

        card_entry = processed[card_id]
        card = card_entry["object"]

        card_entry["count"] += count
        if card.is_special():
            special += count
        if card.is_unit() or card.is_hero():
            units += count

        if card_entry["count"] > card_entry["max_count"]:
            raise ValueError(f"Max count of {card_entry['max_count']} exceeded"
                             f"for card: {card_id}:{card.name}")

        if special > 10:
            raise ValueError("Max count (10) of special cards exceeded")

    if units < 22:
        raise ValueError(f"Insufficient unit cards, expected >=22, got {units}")

    deck = []
    for card_entry in processed.values():
        for _ in range(card_entry["count"]):
            deck.append(Card(card_entry["data"]))

    return Deck(deck), commander

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

# Find
def get_find(card_id):
    return find_dict[f"{card_id}"]