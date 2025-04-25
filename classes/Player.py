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
        self.hp = 2
        self.passed = False

        self.own_cards()

    def draw_card(self):
        card = self.deck.get_next_card()

        if card is None:
            return

        self.hand.add_card(card)

    def draw_cards(self, n):
        for _ in range(n):
            self.draw_card()

    def play_to_board(self, card):
        self.hand.remove_card(card)

    def send_to_grave(self, card):
        self.grave.add_card(card)

    def own_cards(self):
        self.deck.own_cards(self)

    def lower_hp(self):
        self.hp -= 1
        return self.is_dead()
    
    def is_dead(self):
        return self.hp <= 0

    def shuffle_deck(self, rng):
        self.deck.shuffle(rng)

    def return_cards(self):
        self.hand.transfer_all_cards(self.grave)
        self.deck.transfer_all_cards(self.grave)

        for card in list(self.grave.cards):
            if card.owner != self:
                self.grave.remove_card(card)
                card.send_to_owner_grave()

    def deck_from_grave(self):
        self.grave.transfer_all_cards(self.deck)

    def __str__(self):
        return str(self.hand) + "\n" + f'\nH: {self.hand.size()} D: {self.deck.size()}, G: {self.grave.size()} PTS: {self.points}'
