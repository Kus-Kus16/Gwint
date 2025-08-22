from overrides import overrides

from src.model.card_holders.sorted_card_holder import SortedCardHolder
from src.model.cards.cards_database import CardsDatabase

from src.model.enums.ability_type import AbilityType
from src.model.enums.card_type import CardType


class Row(SortedCardHolder):
    def __init__(self):
        super().__init__()
        self.points = 0
        self.effects = {
            "weather": False,
            "bond": dict(),
            "low_morale": set(),
            "morale": set(),
            "horn": set(),
            "mardroeme": set(),
            "sangreal": set()
        }
        self.boosts = ["horn", "mardroeme", "sangreal"]

    @overrides
    def add_card(self, card):
        super().add_card(card)

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

        # Power mods
        for ability in card.abilities:
            ability.on_power_recalculate()

        # Weather
        if self.effects["weather"]:
            if card.owner.get_rule("weather_half") and card.power > 1:
                card.power = card.power // 2
            else:
                card.power = min(card.power, 1)

        # Bond
        if card.is_ability_type(AbilityType.BONDING):
            bond_id = CardsDatabase.get_bond(card.id)
            card.power *= self.effects["bond"][bond_id]

        # Morales
        morales = {
            "low_morale": (-1, +1),
            "morale": (+1, -1)
        }

        for morale, (normal, swapped) in morales.items():
            for source in self.effects[morale]:
                if card != source:
                    delta = swapped if source.owner.get_rule("swap_morale") else normal
                    if delta > 0:
                        card.power += delta
                    else:
                        card.power = max(card.power + delta, 0)

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

    def add_mardroeme(self, card):
        id = card.id
        for source in self.effects["mardroeme"]:
            if source.id == id:
                return False

        self.effects["mardroeme"].add(card)

        remove = []
        add = []
        for card in self.cards:
            if card.is_ability_type(AbilityType.BERSERK):
                extra = CardsDatabase.get_berserker_card(card.id)
                owner = card.owner
                extra.owner = owner
                add.append(extra)
                remove.append(card)

        for card in remove:
            self.remove_card(card)

        for card in add:
            self.add_card(card)

        return True

    def add_sangreal(self, card):
        id = card.id
        for source in self.effects["sangreal"]:
            if source.id == id:
                return False

        self.effects["sangreal"].add(card)
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
        for boost in self.boosts:
            self.clear_boost(boost)

    def clear_boost(self, boost_name):
        remove = []
        for card in self.effects[boost_name]:
            if card.is_card_type(CardType.SPECIAL):
                card.send_to_owner_grave()
                remove.append(card)
            if card.is_card_type(CardType.COMMANDER):
                remove.append(card)

        for card in remove:
            self.effects[boost_name].remove(card)

    def clear(self, player, ignored):
        if ignored is None:
            ignored = set()

        add = []
        remove = []
        destroy = []
        for card in self.cards:
            if card in ignored:
                continue

            if card.is_ability_type(AbilityType.RECALLING):
                extra = CardsDatabase.get_recall_card(card.id)
                extra.owner = player
                add.append((extra, player.id))

            elif card.is_ability_type(AbilityType.ENDURING) and card.power > card.base_power:
                continue

            elif self.effects["sangreal"] and card.is_ability_type(AbilityType.THIRSTY):
                extra = CardsDatabase.get_thirsty_card(card.id)
                extra.owner = player
                add.append((extra, player.id))
                destroy.append(card)
                continue

            remove.append(card)

        for card in remove:
            self.transfer_card(card, player.grave)

        for card in destroy:
            self.remove_card(card)

        return add

    def get_all_boosts_cards(self):
        cards = []
        for boost in self.boosts:
            cards.extend(self.get_boost_cards(boost))

        return cards

    def get_boost_cards(self, boost_name):
        cards = []
        for card in self.effects[boost_name]:
            if card.is_card_type(CardType.SPECIAL):
                cards.append(card)

        return cards