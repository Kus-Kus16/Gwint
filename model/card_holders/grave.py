
from model.card_holders.card_holder import CardHolder
from model.enums.ability_type import AbilityType


class Grave(CardHolder):
    def return_to_deck(self, deck):
        remove = []
        for card in self.cards:
            if card.is_ability_type(AbilityType.AVENGING):
                remove.append(card)

        for card in remove:
            self.remove_card(card)

        self.transfer_all_cards(deck)