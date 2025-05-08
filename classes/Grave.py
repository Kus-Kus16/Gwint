from classes.CardHolder import CardHolder


class Grave(CardHolder):
    def __init__(self):
        super().__init__()

    def redo_deck(self, deck_container):
        remove = []
        for card in self.cards:
            if card.is_avenging():
                remove.append(card)

        for card in remove:
            self.remove_card(card)

        self.transfer_all_cards(deck_container)