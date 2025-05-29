from model.board import Board
import random

from model import cards_database as db
from model.row import RowType


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
            "healRandom": False
        }

    def play_card(self, player_id, card_id, row, targets = None):
        returns = []
        if targets is None:
            targets = []

        if self.current_player_id != player_id:
            print("wrong player")
            return False

        player = self.players[player_id]
        card = player.hand.find_card_by_id(card_id) or player.get_commander(card_id)
        row_type = RowType[row.upper()]

        if card is None:
            print("wrong card")
            return False

        if not card.is_row_playable(row_type):
            print("wrong row")
            return False

        if card.is_commander():
            if not self.handle_commander(player, card, targets, returns):
                print("wrong commander use")
                return False
            card.disable()
        elif card.is_special():
            if not self.handle_special(player, card, row_type, targets):
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

        return returns if returns else True

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
                    other_ids = db.get_muster(card_id)
                    for id in other_ids:
                        extra = player.get_from_hand(id) or player.get_from_deck(id)
                        if extra is not None and extra != card:
                            actions.append(lambda p=player_id, e=extra, r=extra.rows[0]: self.play_extra_card(p, e, r))
                case "scorchRow":
                    actions.append(lambda r=row_type, p=1 - player_id: self.grave_cards(self.board.scorch_row(r, p)))
                case "scorch":
                    actions.append(lambda: self.grave_cards(self.board.scorch()))
                case "medic":
                    if self.gamerule("healRandom"):
                        cards = player.get_grave_cards(playable_only=True)
                        if not cards:
                            targets = []
                        else:
                            target = self.rng.choice(cards).id
                            targets = [target]

                    if len(targets) == 0:
                        continue

                    grave = self.players[player_id].grave
                    target_id = targets.pop(0)
                    target = grave.find_card_by_id(target_id)
                    if target is None:
                        return None

                    actions.append(lambda p=player, t=target: p.grave.remove_card(t))
                    actions.append(lambda p=player_id, c=target, r=target.rows[0]: self.play_extra_card(p, c, r, targets))

        return actions

    def handle_commander(self, player, commander, targets, returning_list):
        if not commander.active:
            return False

        ability = commander.ability()
        match ability:
            case "findFrost" | "findFog" | "findRain" | "findStorm":
                card_id = db.get_find(commander.id)
                card = player.get_from_deck(card_id)
                if card is not None:
                    self.play_extra_card(player.id, card, "any")
            case "clear":
                self.board.clear_weather()
            case "hornClose" | "hornRanged"| "hornSiege":
                row_type = RowType[ability[4:].upper()]
                row, _ = self.board.get_row(row_type, player.id)
                if not row.add_horn(commander):
                    return False
            case "scorchClose" | "scorchRanged"| "scorchSiege":
                row_type = RowType[ability[6:].upper()]
                self.grave_cards(self.board.scorch_row(row_type, 1 - player.id))
            case "show3Enemy":
                returning_list.extend(self.peek_cards(1 - player.id, 3))
            case "chooseEnemyGrave":
                if len(targets) == 0:
                    return True

                grave = self.players[1 - player.id].grave
                target_id = targets.pop(0)
                target = grave.find_card_by_id(target_id)
                if target is None:
                    return False

                self.players[1 - player.id].grave.remove_card(target)
                player.hand.add_card(target)

        return True

    def pass_round(self, player_id):
        if self.current_player_id != player_id:
            print("wrong player")
            return False

        self.players[player_id].passed = True
        self.next_turn()

        return True

    def redraw_cards(self, player_id, targets):
        player = self.players[player_id]
        if not targets:
            player.redraws = 0
            return True

        if len(targets) > player.redraws:
            print("Illegal redraw")
            return False

        for card_id in targets:
            card = player.hand.find_card_by_id(card_id)
            if card is None:
                print("No card in hand")
                return False

            player.hand.remove_card(card)
            player.deck.add_card(card)
            player.draw_card()
            player.redraws -= 1

        return True

    def end_redraws(self):
        for player in self.players:
            player.redraws = 0
            player.shuffle_deck(self.rng)

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
            opponent = self.players[1 - player.id]
            match player.commander.ability():
                case "blockAbility":
                    player.commander.disable()
                    opponent.commander.disable()
                case "healRandom":
                    self.gamerules["healRandom"] = True
                    player.commander.disable()

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