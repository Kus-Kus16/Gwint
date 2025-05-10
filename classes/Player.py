from classes.Grave import Grave
from classes.Hand import Hand


class Player:
    def __init__(self, deck, commander):
        self.id = None
        self.deck = deck
        self.hand = Hand()
        self.grave = Grave()
        self.commander = commander
        self.faction = commander.faction
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
        if card in self.hand.cards:
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
        self.grave.return_to_deck(self.deck)

    def get_grave_cards(self, playable_only=False):
        if not playable_only:
            return self.grave.cards

        cards = []
        for card in self.grave.cards:
            if card.is_special() or card.is_hero():
                continue

            cards.append(card)

        return cards

    def get_from_hand(self, card_id):
        return self.hand.get_card_by_id(card_id)

    def get_from_deck(self, card_id):
        return self.deck.get_card_by_id(card_id)

    def get_commander(self, card_id):
        card = self.commander
        return card if card.id == card_id else None

    def __str__(self):
        return str(self.hand) + "\n" + f'\nH: {self.hand.size()} D: {self.deck.size()}, G: {self.grave.size()} PTS: {self.points}'
