from model.card_holder import CardHolder


class Grave(CardHolder):

    def return_to_deck(self, deck):
        remove = []
        for card in self.cards:
            if card.is_avenging():
                remove.append(card)

        for card in remove:
            self.remove_card(card)

        self.transfer_all_cards(deck)