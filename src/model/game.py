import logging

from src.model.abilities.commanders.block_ability import BlockAbility
from src.model.board import Board
import random

from src.model.enums.card_type import CardType
from src.model.enums.row_type import RowType


class Game:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.ready = False
        self.board = Board()
        self.players = []
        self.current_player_id = None
        self.first_player_id = None
        self.current_round = 0
        self.round_history = []
        self.gamerules = {
            "heal_random": False
        }

    def play_card(self, player_id, card_id, row_type, targets=None):
        returns = []
        if targets is None:
            targets = []

        if self.current_player_id != player_id:
            raise ValueError(f"Wrong player, expected p{self.current_player_id}")

        player = self.players[player_id]
        card = player.hand.find_card_by_id(card_id) or player.get_commander(card_id)

        if card is None:
            raise ValueError(f"Wrong card, cannot find card for p{player_id}")

        if not card.is_row_playable(row_type):
            raise ValueError(f"Card {card.id}:{card.name} is not playable for given row: {row_type}")

        if card.is_card_type(CardType.COMMANDER):
            returns = self.handle_commander(player, card, targets)
            card.disable()
        elif card.is_card_type(CardType.SPECIAL):
            self.handle_special(player, card, row_type, targets)
            player.play_to_board(card)
        else:
            additional_actions = self.handle_abilities(player, card, row_type, targets)
            player.play_to_board(card)
            self.board.play_card(card, row_type, player_id)

            for action in additional_actions:
                action()

        self.update_points()
        self.next_turn()

        return returns

    def play_extra_card(self, player_id, card, row_type, targets=None):
        # Ignores the limits except abilities
        if targets is None:
            targets = []

        player = self.get_player(player_id)

        try:
            if card.is_card_type(CardType.SPECIAL):
                self.handle_special(player, card, row_type, targets)
            else:
                additional_actions = self.handle_abilities(player, card, row_type, targets)
                self.board.play_card(card, row_type, player_id)
                for action in additional_actions:
                    action()
        except ValueError as e:
            logging.info(f"play_extra_card ignored exception: {str(e)}")

        self.update_points()

    def handle_special(self, player, card, row_type, targets):
        for ability in card.abilities:
            ability.on_board_play(self, player, row_type, targets)

    def handle_abilities(self, player, card, row_type, targets):
        additional_actions = []

        for ability in card.abilities:
            actions = ability.on_board_play(self, player, row_type, targets)
            additional_actions.extend(actions)

        return additional_actions

    def handle_commander(self, player, commander, targets):
        if not commander.active:
            raise ValueError(f"Wrong commander use: commander is not active for p{player.id}")

        ability = commander.ability()
        return ability.on_board_play(self, player, RowType.ANY, targets)

    def pass_round(self, player_id):
        if self.current_player_id != player_id:
            raise ValueError(f"Wrong player, expected p{self.current_player_id}")

        self.players[player_id].passed = True
        self.next_turn()

    def redraw_cards(self, player_id, targets):
        player = self.players[player_id]
        if not targets:
            player.redraws = 0
            return

        if len(targets) > player.redraws:
            raise ValueError(f"Wrong redraw: not enough redraws for p{player_id}")

        for card_id in targets:
            card = player.hand.find_card_by_id(card_id)
            if card is None:
                raise ValueError(f"Wrong redraw: cannot find card {card_id} in p{player_id}")

            player.hand.remove_card(card)
            player.deck.add_card(card)
            player.draw_card()
            player.redraws -= 1

    def end_redraws(self):
        for player in self.players:
            player.redraws = 0
            player.shuffle_deck(self.rng)

    def next_turn(self):
        next_player = self.players[1 - self.current_player_id]

        if not next_player.passed:
            self.current_player_id = next_player.id

    def update_points(self):
        player0_pts, player1_pts = self.board.rows_sum()

        self.players[0].points = player0_pts
        self.players[1].points = player1_pts

    def start_game(self):
        self.reset_gamerules()
        self.current_round = 0
        self.round_history = []
        self.first_player_id = self.rng.randint(0, 1)
        self.ready = True

        for player in self.players:
            player.hp = 2
            player.redraws = 2
            player.commander.enable()
            player.shuffle_deck(self.rng)
            player.draw_cards(10)

        for player in self.players:
            ability = player.commander.ability()
            if isinstance(ability, BlockAbility):
                ability.on_start_game(self, player)
                return

        for player in self.players:
            ability = player.commander.ability()
            ability.on_start_game(self, player)

    def start_round(self):
        self.current_round += 1
        self.current_player_id = (1 - self.first_player_id + self.current_round) % 2

    def end_round(self):
        self.current_player_id = None
        player0, player1 = self.players[0], self.players[1]

        player0.passed = False
        player1.passed = False

        player0_pts, player1_pts = player0.points, player1.points
        self.round_history.append((player0_pts, player1_pts))

        if player0_pts > player1_pts:
            player1.lower_hp()
        elif player1_pts > player0_pts:
            player0.lower_hp()
        else:
            player0.lower_hp()
            player1.lower_hp()

        self.board.clear_rows(self.players)
        self.board.clear_weather()
        self.update_points()

    def end_game(self):
        self.board.clear_rows(self.players)
        self.board.clear_weather()
        self.update_points()

        for player in self.players:
            player.return_cards()
        for player in self.players:
            player.deck_from_grave()

    def add_player(self, player):
        player_count = len(self.players)
        if player_count > 1:
            raise ValueError(f"Too many players, 2 already added")

        self.players.append(player)
        player.id = player_count
        return player_count

    def get_player(self, player_id):
        return self.players[player_id]

    def set_seed(self, seed):
        self.rng = random.Random(seed)

    def is_winning_round(self, player_id):
        return self.players[player_id].points > self.players[1- player_id].points

    def get_round_history(self, player_id):
        if player_id == 0:
            return self.round_history

        history = []
        for pl0, pl1 in self.round_history:
            history.append((pl1, pl0))

        return history

    def grave_cards(self, cards_data):
        for card, player_id in cards_data:
            player = self.players[player_id]
            player.send_to_grave(card)

    def peek_cards(self, player_id, count):
        cards = list(self.players[player_id].hand.cards)
        self.rng.shuffle(cards)
        return cards[:count]

    def reset_gamerules(self):
        for rule in self.gamerules:
            self.gamerules[rule] = False

    def gamerule(self, rule):
        return self.gamerules[rule]