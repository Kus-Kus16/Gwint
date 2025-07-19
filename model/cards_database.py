import json
from collections import defaultdict

from model.card import Card
from model.commander import Commander
from model.card_holders.deck import Deck
from model.enums.card_type import CardType

with open("./data/cards.json", "r", encoding="utf-8") as file:
    card_list = json.load(file)
    card_dict = {card["id"]: card for card in card_list}

    faction_dict = defaultdict(list)
    for card in card_list:
        faction_dict[card["faction"]].append(card)

with open("./data/factions.json", "r", encoding="utf-8") as file:
    faction_list = json.load(file)

with open("./data/muster.json", "r", encoding="utf-8") as file:
    muster_dict = json.load(file)

with open("./data/bond.json", "r", encoding="utf-8") as file:
    bond_dict = json.load(file)

with open("./data/recall.json", "r", encoding="utf-8") as file:
    recall_dict = json.load(file)

# Nicknames
def faction_to_nickname(fullname):
    mapping = {
        "Królestwa Północy": "polnoc",
        "Cesarstwo Nilfgaardu": "nilfgaard",
        "Potwory": "potwory",
        "Scoia'tael": "scoiatael",
        "Skellige": "skellige",
        "Księstwo Toussaint": "toussaint",
        "Kult Wiecznego Ognia": "ogien"
    }
    return mapping.get(fullname)

# Dictionary
def find_card_by_id(card_id):
    return card_dict.get(card_id)

def find_commander_by_id(commander_id):
    for faction in faction_list:
        for commander in faction["commanders"]:
            if commander["id"] == commander_id:
                return commander, faction["name"]

def get_faction_cards(fullname, neutral=False):
    cards = list(faction_dict.get(fullname, []))
    if neutral:
        cards.extend(faction_dict.get("Neutralne", []))

    return cards

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
        if card.is_card_type(CardType.SPECIAL):
            special += count
        if card.is_card_type(CardType.UNIT) or card.is_card_type(CardType.HERO):
            units += count

        if card_entry["count"] > card_entry["max_count"]:
            raise ValueError(f"Max count of {card_entry['max_count']} exceeded"
                             f"for card: {card_id}:{card.name}")

        if special > 10:
            raise ValueError("Max count (10) of specials cards exceeded")

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