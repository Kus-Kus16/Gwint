from overrides import overrides

from model import cards_database as db
from model.card_holder import CardHolder
from enum import Enum
import bisect


class RowType(Enum):
    CLOSE = 0
    RANGED = 1
    SIEGE = 2
    CLOSE_OPP = 3
    RANGED_OPP = 4
    SIEGE_OPP = 5
    ANY = 6

class Row(CardHolder):
    def __init__(self):
        super().__init__()
        self.points = 0
        self.effects = {
            "weather": False,
            "morale": set(),
            "bond": {},
            "horn": set()
        }

    @overrides
    def add_card(self, card):
        bisect.insort(self.cards, card)
        self.handle_abilities_insert(card)
        self.recalculate()

    @overrides
    def remove_card(self, card):
        self.cards.remove(card)
        self.handle_abilities_remove(card)
        card.reset_power()
        self.recalculate()

    def recalculate(self):
        total = 0

        for card in self.cards:
            if card.is_special():
                continue

            self.apply_effects(card)
            total += card.power

        self.points = total
        return total

    def apply_effects(self, card):
        if card.is_hero():
            return

        card.power = card.base_power

        # Weather
        if self.effects["weather"]:
            card.power = min(card.power, 1)

        # Bond
        if "bond" in card.abilities:
            bond_id = db.get_bond(card.id)
            card.power *= self.effects["bond"][bond_id]

        # Morale
        for source in self.effects["morale"]:
            if card != source:
                card.power += 1

        # Horn
        horned = False
        for source in self.effects["horn"]:
            if card != source:
                horned = True
        if horned:
            card.power *= 2

    def add_weather(self):
        self.effects["weather"] = True
        self.recalculate()

    def clear_weather(self):
        self.effects["weather"] = False
        self.recalculate()

    def add_horn(self, card):
        id = card.id
        for source in self.effects["horn"]:
            if source.id == id:
                return False

        self.effects["horn"].add(card)
        self.recalculate()
        return True

    def find_strongest(self, ignore_heroes = False):
        maxi = -10e10
        for card in self.cards:
            if card.is_special() or (ignore_heroes and card.is_hero()):
                continue

            if card.power > maxi:
                maxi = card.power

        if ignore_heroes:
            fun = lambda card: not card.is_hero() and card.power == maxi
        else:
            fun = lambda card: card.power == maxi

        return self.find_cards(fun)

    def find_weakest(self, ignore_heroes = False):
        mini = 10e10
        for card in self.cards:
            if card.is_special() or (ignore_heroes and card.is_hero()):
                continue

            if card.power < mini:
                mini = card.power

        if ignore_heroes:
            fun = lambda card: not card.is_hero() and card.power == mini
        else:
            fun = lambda card: card.power == mini

        return self.find_cards(fun)

    def handle_abilities_insert(self, card):
        for ability in card.abilities:
            match ability:
                case "morale":
                    self.effects["morale"].add(card)
                case "bond":
                    bond_id = db.get_bond(card.id)
                    self.effects["bond"].setdefault(bond_id, 0)
                    self.effects["bond"][bond_id] += 1
                case "horn":
                    self.effects["horn"].add(card)

    def handle_abilities_remove(self, card):
        for ability in card.abilities:
            match ability:
                case "morale":
                    self.effects["morale"].remove(card)
                case "bond":
                    bond_id = db.get_bond(card.id)
                    self.effects["bond"][bond_id] -= 1
                case "horn":
                    self.effects["horn"].remove(card)

    def clear_boosts(self):
        remove = []
        for card in self.effects["horn"]:
            if card.is_special():
                self.effects["horn"].remove(card)
                card.send_to_owner_grave()
                break
            if card.is_commander():
                remove.append(card)

        for card in remove:
            self.effects["horn"].remove(card)

    def clear_row(self, player):
        remove = []
        add = []
        for card in self.cards:
            if card.is_recalling():
                extra = db.get_recall(card.id)
                extra.owner = player
                add.append((extra, player.id))

            remove.append(card)

        for card in remove:
            self.transfer_card(card, player.grave)

        return add

    def get_effect_cards(self):
        cards = []
        for card in self.effects["horn"]:
            if card.is_special():
                cards.append(card)

        return cards

    def __str__(self):
        return str(self.points) + " :: " + ", ".join(str(card) for card in self.cards)