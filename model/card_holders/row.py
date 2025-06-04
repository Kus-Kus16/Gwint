from overrides import overrides

from model import cards_database as db
from model.card_holders.card_holder import CardHolder
import bisect

from model.enums.ability_type import AbilityType
from model.enums.card_type import CardType


class Row(CardHolder):
    def __init__(self):
        super().__init__()
        self.points = 0
        self.effects = {
            "weather": False,
            "morale": set(),
            "bond": dict(),
            "horn": set()
        }

    @overrides
    def add_card(self, card):
        bisect.insort(self.cards, card)

        for ability in card.abilities:
            ability.on_row_insert(self)

        self.recalculate()

    @overrides
    def remove_card(self, card):
        self.cards.remove(card)

        for ability in card.abilities:
            ability.on_row_remove(self)

        card.reset_power()
        self.recalculate()

    def recalculate(self):
        total = 0

        for card in self.cards:
            if card.is_card_type(CardType.SPECIAL):
                continue

            self.apply_effects(card)
            total += card.power

        self.points = total
        return total

    def apply_effects(self, card):
        if card.is_card_type(CardType.HERO):
            return

        card.power = card.base_power

        # Weather
        if self.effects["weather"]:
            card.power = min(card.power, 1)

        # Bond
        if card.is_ability_type(AbilityType.BONDING):
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

    def find_strongest(self, ignore_heroes=False):
        maxi = -10e10
        for card in self.cards:
            if card.is_card_type(CardType.SPECIAL) or (ignore_heroes and card.is_card_type(CardType.HERO)):
                continue

            if card.power > maxi:
                maxi = card.power

        if ignore_heroes:
            fun = lambda card: not card.is_card_type(CardType.HERO) and card.power == maxi
        else:
            fun = lambda card: card.power == maxi

        return self.find_cards(fun)

    def find_weakest(self, ignore_heroes=False):
        mini = 10e10
        for card in self.cards:
            if card.is_card_type(CardType.SPECIAL) or (ignore_heroes and card.is_card_type(CardType.HERO)):
                continue

            if card.power < mini:
                mini = card.power

        if ignore_heroes:
            fun = lambda card: not card.is_card_type(CardType.HERO) and card.power == mini
        else:
            fun = lambda card: card.power == mini

        return self.find_cards(fun)

    def clear_boosts(self):
        remove = []
        for card in self.effects["horn"]:
            if card.is_card_type(CardType.SPECIAL):
                card.send_to_owner_grave()
                remove.append(card)
            if card.is_card_type(CardType.COMMANDER):
                remove.append(card)

        for card in remove:
            self.effects["horn"].remove(card)

    def clear(self, player):
        remove = []
        add = []
        for card in self.cards:
            if card.is_ability_type(AbilityType.RECALLING):
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
            if card.is_card_type(CardType.SPECIAL):
                cards.append(card)

        return cards

    def __str__(self):
        return str(self.points) + " :: " + ", ".join(str(card) for card in self.cards)