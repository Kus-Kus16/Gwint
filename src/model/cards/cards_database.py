from abc import ABC
from collections import defaultdict

from src.model.cards.card import Card
from src.model.cards.commander import Commander
from src.model.card_holders.deck import Deck
from src.model.enums.card_type import CardType
from src.model.enums.faction_type import FactionType
from src.presenter.loader import Loader


class CardsDatabase(ABC):
    # Cards
    __card_list = Loader.load_data("cards")
    __card_dict = {card["id"]: card for card in __card_list}

    __faction_cards_dict = defaultdict(list)
    for card in __card_list:
        if card["count"] == 0:
            continue

        faction = FactionType(card["faction"])
        __faction_cards_dict[faction].append(card)

    # Factions
    __faction_list = Loader.load_data("factions")
    __faction_commanders_dict = defaultdict(list)
    for faction_data in __faction_list:
        faction = FactionType(faction_data["faction"])
        __faction_commanders_dict[faction] = faction_data["commanders"]

    # Abilities
    __muster_dict = Loader.load_data("muster")
    __bond_dict = Loader.load_data("bond")
    __recall_dict = Loader.load_data("recall")
    __berserker_dict = Loader.load_data("berserker")
    __thirsty_dict = Loader.load_data("thirsty")

    # Dictionary
    @classmethod
    def find_card_by_id(cls, card_id):
        return cls.__card_dict.get(card_id)

    @classmethod
    def find_commander_by_id(cls, commander_id):
        for faction in cls.__faction_list:
            for commander in faction["commanders"]:
                if commander["id"] == commander_id:
                    commander["faction"] = FactionType(faction["faction"])
                    return commander

    @classmethod
    def get_faction_cards(cls, faction_type, include_neutral=False):
        cards = list(cls.__faction_cards_dict.get(faction_type, []))
        if include_neutral:
            cards.extend(cls.__faction_cards_dict.get(FactionType.NEUTRAL, []))

        return cards

    @classmethod
    def get_faction_commanders(cls, faction_type):
        commanders = cls.__faction_cards_dict[faction_type]
        for data in commanders:
            data["faction"] = faction_type

        return commanders

    @classmethod
    def create_verified_deck(cls, data, commander_id):
        commander_data = cls.find_commander_by_id(commander_id)
        if commander_data is None:
            raise ValueError(f"Commander: {commander_id} does not exist")

        faction_type = commander_data["faction"]
        commander = Commander(commander_data)

        processed = {}
        units = 0
        special = 0

        for item in data:
            card_id, count = item["id"], item["count"]

            if card_id not in processed:
                card_data = cls.find_card_by_id(card_id)

                if card_data is None:
                    raise ValueError(f"Card: {card_id} does not exist")

                faction_valid = FactionType(card_data["faction"]) in (FactionType.NEUTRAL, faction_type)

                if not faction_valid:
                    raise ValueError(f"Card: {card_id}:{card_data['name']} does not belong to {faction_type}")

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

    # Abilities
    @classmethod
    def get_muster(cls, card_id):
        return cls.__muster_dict[f"{card_id}"]

    @classmethod
    def get_bond(cls, card_id):
        return cls.__bond_dict[f"{card_id}"]

    @classmethod
    def get_recall_card(cls, card_id):
        card_id = cls.__recall_dict[f"{card_id}"]
        card_data = cls.find_card_by_id(card_id)
        return Card(card_data)

    @classmethod
    def get_berserker_card(cls, card_id):
        card_id = cls.__berserker_dict[f"{card_id}"]
        card_data = cls.find_card_by_id(card_id)
        return Card(card_data)

    @classmethod
    def get_thirsty_card(cls, card_id):
        card_id = cls.__thirsty_dict[f"{card_id}"]
        card_data = cls.find_card_by_id(card_id)
        return Card(card_data)