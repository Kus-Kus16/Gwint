import logging
import random

from src.model.abilities.commanders.block_ability import BlockAbility
from src.model.board import Board
from src.model.enums.card_type import CardType
from src.model.enums.faction_type import FactionType


class Game:
    def __init__(self, presenter, seed):
        self.presenter = presenter
        self.rng = random.Random(seed)
        self.board = Board()
        self.players = []
        self.current_player_id = None
        self.first_player_id = None
        self.current_round = 0
        self.round_history = []
        self.gamerules = {
            "heal_random": False,
            "spies_double": False,
            "weak_scorch": False,
            "weather_half": set()
        }

    def play_card(self, player_id, own_id, card_id, row_type, targets=None):
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
            to_show = self.handle_commander(player, card, row_type, targets)
            card.disable()
            self.presenter.show_carousel(to_show, cancelable=True)
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
        self.next_turn(own_id)

    def play_extra_card(self, player_id, card, row_type, targets=None):
        #Ignores the limits
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

    def handle_commander(self, player, commander, row_type, targets):
        if not commander.active:
            raise ValueError(f"Wrong commander use: commander is not active for p{player.id}")

        ability = commander.ability()
        return ability.on_board_play(self, player, row_type, targets)

    def pass_round(self, player_id, own_id):
        if self.current_player_id != player_id:
            raise ValueError(f"Wrong player, expected p{self.current_player_id}")

        self.presenter.notification("pass" if player_id == own_id else "pass_op")
        self.players[player_id].passed = True
        self.next_turn(own_id)

        if not self.players[1 - player_id].passed:
            # other turn
            self.presenter.notification("waiting" if player_id == own_id else "playing")
            return

        # both passed
        notif = (
            "win_round" if self.is_winning_round(own_id)
            else "lose_round" if self.is_winning_round(1 - own_id)
            else "draw_round"
        )
        self.presenter.notification(notif)

        ending = self.end_round()
        if ending:
            return

        self.presenter.notification("round_start")
        self.start_round(own_id)

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

    def end_redraws(self, own_id):
        for player in self.players:
            player.redraws = 0

        for player in self.players:
            if player.faction == FactionType.OGIEN:
                self.presenter.notification("fire_ability")
                break

        self.shuffle_decks()
        self.presenter.notification("round_start")
        self.start_round(own_id)

    def shuffle_decks(self):
        for player in self.players:
            player.shuffle_deck(self.rng)

    def next_turn(self, own_id):
        next_player = self.players[1 - self.current_player_id]

        if not next_player.passed:
            self.current_player_id = next_player.id

        if any(player.passed for player in self.players):
            return

        self.presenter.notification("playing" if next_player.id == own_id else "waiting")

    def update_points(self):
        player0_pts, player1_pts = self.board.rows_sum()

        self.players[0].points = player0_pts
        self.players[1].points = player1_pts

    def need_first_player(self):
        p0 = self.players[0].faction == FactionType.SCOIATAEL
        p1 = self.players[1].faction == FactionType.SCOIATAEL

        if p0 == p1:
            return -1
        return 0 if p0 else 1

    def start_game(self, starting_player, player_id):
        self.reset_gamerules()
        self.current_round = 0
        self.round_history = []

        if starting_player is None:
            self.first_player_id = self.rng.randint(0, 1)
            notif = "start" if self.first_player_id == player_id else "op_start"
        else:
            self.first_player_id = starting_player
            if self.get_player(player_id).faction == FactionType.SCOIATAEL:
                notif = "scoia_start" if self.first_player_id == player_id else "scoia_op_start"
            else:
                notif = "op_scoia_start" if self.first_player_id == player_id else "op_scoia_op_start"

        self.presenter.notification(notif)

        for player in self.players:
            player.hp = 2
            player.redraws = 2 if player.faction != FactionType.OGIEN else 4
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

    def start_round(self, own_id):
        self.current_round += 1
        self.current_player_id = (1 - self.first_player_id + self.current_round) % 2
        self.presenter.notification("playing" if self.current_player_id == own_id else "waiting")

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

        extra = self.board.clear_rows(self.players)
        for card, player_id in extra:
            self.play_extra_card(player_id, card, card.rows[0])

        self.board.clear_weather()
        self.update_points()

        for player in self.players:
            ability = player.commander.ability()
            ability.on_round_end(self, player)

        if self.current_round == 3 or player0.is_dead() or player1.is_dead():
            self.presenter.end_game()
            return True

        return False

    def clear_game(self):
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
            raise ValueError("Too many players, 2 already added")

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

    def grave_scorch_cards(self, cards_data):
        self.rng.shuffle(cards_data)
        scorched_players = [False, False]

        for card, player_id, row in cards_data:
            if self.gamerule("weak_scorch") and scorched_players[player_id]:
                continue

            row.remove_card(card)
            player = self.players[player_id]
            player.send_to_grave(card)
            scorched_players[player_id] = True

    def shuffle_cards(self, card_holder):
        cards = list(card_holder.cards)
        self.rng.shuffle(cards)
        return cards

    def reset_gamerules(self):
        for rule in self.gamerules:
            self.gamerules[rule] = False

    def gamerule(self, rule):
        return self.gamerules[rule]