from classes.Grave import Grave
from classes.Hand import Hand


class Player:
    def __init__(self, deck, commander):
        self.id = None
        self.deck = deck
        self.hand = Hand()
        self.grave = Grave()
        self.commander = commander
        self.points = 0
        self.passed = False

        self.own_cards()

    def add_card(self, card, container):
        container.add_card(card)

    def remove_card(self, card, container):
        container.remove_card(card)

    def draw_card(self):
        card = self.deck.get_next_card()

        if card is None:
            return

        self.add_card(card, self.hand)

    def draw_cards(self, n):
        for _ in range(n):
            self.draw_card()

    def play_to_board(self, card):
        self.remove_card(card, self.hand)

    def send_to_grave(self, card):
        self.add_card(card, self.grave)

    def own_cards(self):
        self.deck.own_cards(self)

    def __str__(self):
        return str(self.hand) + "\n" + f'\nH: {self.hand.size()} D: {self.deck.size()}, G: {self.grave.size()} PTS: {self.points}'
