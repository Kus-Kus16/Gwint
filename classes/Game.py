from classes.Board import Board
import random

from classes import CardsDatabase
from classes.Row import RowType


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

    def play_card(self, player_id, card_id, row, targets = None):
        if targets is None:
            targets = []

        if self.current_player_id != player_id:
            print("wrong player")
            return False

        player = self.players[player_id]
        card = player.hand.find_card_by_id(card_id)
        row_type = RowType[row.upper()]

        if card is None:
            print("wrong card")
            return False

        if not card.is_row_playable(row_type):
            print("wrong row")
            return False

        if card.is_special():
            valid = self.handle_special(player, card, row_type, targets)
            if not valid:
                print("wrong special action")
                return False
            player.play_to_board(card)
        else:
            additional_actions = self.handle_abilities(player, card, row_type, targets)
            if additional_actions is None:
                print("wrong ability use")
                return False

            player.play_to_board(card)
            self.board.play_card(card, row_type, player_id)
            for action in additional_actions:
                action()

        self.update_points()
        self.next_turn()

        return True

    def play_extra_card(self, player_id, card, row, targets = None):
        # Ignores the limits except abilities
        if targets is None:
            targets = []
        player = self.players[player_id]
        row_type = RowType[row.upper()]

        if card.is_special():
            self.handle_special(player, card, row_type, targets)
        else:
            additional_actions = self.handle_abilities(player, card, row_type, targets)
            self.board.play_card(card, row_type, player_id)
            for action in additional_actions:
                action()
        self.update_points()

    def handle_special(self, player, card, row_type, targets):
        card_id = card.id
        player_id = player.id

        for ability in card.abilities:
            match ability:
                case "decoy":
                    target_id = targets.pop(0)
                    row, row_owner_id = self.board.get_row(row_type, player_id)
                    if row_owner_id != player_id:
                        return False

                    target = row.find_card_by_id(target_id)
                    if target is None or not target.is_unit():
                        return False

                    row.add_card(card)
                    row.remove_card(target)
                    player.hand.add_card(target)
                case "horn":
                    row, row_owner_id = self.board.get_row(row_type, player_id)
                    if row_owner_id != player_id or not row.add_horn(card):
                        return False
                case "scorch":
                    self.grave_cards(self.board.scorch())
                    card.send_to_owner_grave()
                case "clear" | "frost" | "fog" | "rain" | "storm":
                    if self.board.is_weather_active(ability):
                        card.send_to_owner_grave()
                    else:
                        self.board.add_weather(card, ability)
                case "mardroeme":
                    pass
                case "sangreal":
                    pass

        return True

    def handle_abilities(self, player, card, row_type, targets):
        actions = []
        card_id = card.id
        player_id = player.id

        for ability in card.abilities:
            match ability:
                case "spy":
                    actions.append(lambda p=player: p.draw_cards(2))
                case "muster":
                    other_ids = CardsDatabase.get_muster(card_id)
                    for id in other_ids:
                        extra = player.hand.get_card_by_id(id) or player.deck.get_card_by_id(id)
                        if extra is not None and extra != card:
                            actions.append(lambda p=player_id, e=extra, r=extra.rows[0]: self.play_extra_card(p, e, r))
                case "scorchRow":
                    actions.append(lambda r=row_type, p=1 - player_id: self.grave_cards(self.board.scorch_row(r, p)))
                case "scorch":
                    actions.append(lambda: self.grave_cards(self.board.scorch()))
                case "medic":
                    grave = self.players[player_id].grave
                    target_id = targets.pop(0)
                    target = grave.find_card_by_id(target_id)
                    if target is None:
                        return None

                    actions.append(lambda p=player, t=target: p.grave.remove_card(t))
                    actions.append(lambda p=player_id, c=target, r=target.rows[0], t=targets: self.play_extra_card(p, c, r, t))

        return actions

    def pass_round(self, player_id):
        if self.current_player_id != player_id:
            print("wrong player")
            return False

        self.players[player_id].passed = True
        self.next_turn()

        return True

    def next_turn(self):
        next_player = self.players[1 - self.current_player_id]

        if not next_player.passed:
            self.current_player_id = next_player.id
            return

    def update_points(self):
        player0_pts, player1_pts = self.board.rows_sum()

        self.players[0].points = player0_pts
        self.players[1].points = player1_pts

    def start_game(self):
        #TODO game start
        self.current_round = 0
        self.round_history = []
        self.first_player_id = self.rng.randint(0, 1)
        self.ready = True

        for player in self.players:
            player.hp = 2
            player.shuffle_deck(self.rng)
            player.draw_cards(10)

    def end_game(self):
        self.board.clear_rows(self.players)
        self.board.clear_weather()
        self.update_points()

        for player in self.players:
            player.return_cards()
        for player in self.players:
            player.deck_from_grave()

    def end_round(self):
        #TODO round end
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

    def start_round(self):
        self.current_round += 1
        self.current_player_id = (1 - self.first_player_id + self.current_round) % 2

    def to_string(self, player_id):
        return self.board.rows_tostring(player_id) + "\n\n" + str(self.players[player_id])

    def add_player(self, player):
        player_count = len(self.players)

        if player_count > 1:
            return None

        self.players.append(player)
        player.id = player_count
        return player_count

    def get_player(self, player_id):
        return self.players[player_id]

    def set_seed(self, seed):
        self.rng = random.Random(seed)

    def winning_round(self, player_id):
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