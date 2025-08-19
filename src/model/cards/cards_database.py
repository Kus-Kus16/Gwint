import json
from collections import defaultdict

from src.model.cards.card import Card
from src.model.cards.commander import Commander
from src.model.card_holders.deck import Deck
from src.model.enums.card_type import CardType
from src.model.enums.faction_type import FactionType

#TODO REfactor

with open("./resources/data/cards.json", "r", encoding="utf-8") as file:
    card_list = json.load(file)
    card_dict = {card["id"]: card for card in card_list}

    faction_cards_dict = defaultdict(list)
    for card in card_list:
        if card["count"] == 0:
            continue

        faction = FactionType.fullname_to_faction(card["faction"])
        faction_cards_dict[faction].append(card)

with open("./resources/data/factions.json", "r", encoding="utf-8") as file:
    faction_list = json.load(file)

    faction_commanders_dict = defaultdict(list)
    for faction_data in faction_list:
        faction = FactionType.fullname_to_faction(faction_data["name"])
        faction_commanders_dict[faction] = faction_data["commanders"]

with open("./resources/data/muster.json", "r", encoding="utf-8") as file:
    muster_dict = json.load(file)

with open("./resources/data/bond.json", "r", encoding="utf-8") as file:
    bond_dict = json.load(file)

with open("./resources/data/recall.json", "r", encoding="utf-8") as file:
    recall_dict = json.load(file)

with open("./resources/data/berserker.json", "r", encoding="utf-8") as file:
    berserker_dict = json.load(file)

with open("./resources/data/thirsty.json", "r", encoding="utf-8") as file:
    thirsty_dict = json.load(file)

# Dictionary
def find_card_by_id(card_id):
    return card_dict.get(card_id)

def find_commander_by_id(commander_id):
    for faction in faction_list:
        for commander in faction["commanders"]:
            if commander["id"] == commander_id:
                commander["faction"] = faction["name"]
                return commander

def get_faction_cards(faction_type, include_neutral=False):
    cards = list(faction_cards_dict.get(faction_type, []))
    if include_neutral:
        cards.extend(faction_cards_dict.get(FactionType.NEUTRAL, []))

    return cards

def get_faction_commanders(faction_type):
    faction_name = FactionType.faction_to_fullname(faction_type)
    commanders = faction_commanders_dict[faction_type]

    for data in commanders:
        data["faction"] = faction_name

    return commanders

def create_verified_deck(data, commander_id):
    commander_data = find_commander_by_id(commander_id)

    if commander_data is None:
        raise ValueError(f"Commander: {commander_id} does not exist")

    faction = commander_data["faction"]
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

# Berserker
def get_berserker(card_id):
    card_id = berserker_dict[f"{card_id}"]
    card_data = find_card_by_id(card_id)
    return Card(card_data)

# Thirsty
def get_thirsty(card_id):
    card_id = thirsty_dict[f"{card_id}"]
    card_data = find_card_by_id(card_id)
    return Card(card_data)