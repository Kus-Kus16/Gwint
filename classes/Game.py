from classes.Board import Board
import random

class Game:
    def __init__(self, id):
        self.ready = False
        self.id = id
        self.board = Board()
        self.players = []
        self.current_player_id = None
        self.first_player_id = None
        self.current_round = 0
        self.round_history = []

    def play_card(self, player_id, card_id, row_type):
        if self.current_player_id != player_id:
            print("wrong player")
            return False

        player = self.players[player_id]
        card = player.hand.find_card_by_id(card_id)

        if card is None:
            print("wrong card")
            return False

        if not card.is_row_playable(row_type):
            print("wrong row")
            return False

        player.play_to_board(card)

        if card.is_special():
            #TODO special logic here
            self.handle_special(card)
        else:
            self.board.play_card(card, row_type, player_id)
            self.handle_abilities(card)

        self.update_points()
        self.next_turn()

        return True

    def handle_special(self, card):
        for ability in card.abilities:
            match ability:
                case "decoy":
                    pass
                case "horn":
                    pass
                case "scorch":
                    pass
                case "clear" | "frost" | "fog" | "rain" | "storm":
                    if self.board.is_weather_active(ability):
                        card.send_to_owner_grave()
                        return

                    self.board.add_weather(card, ability)
                case "mardroeme":
                    pass
                case "sangreal":
                    pass

    def handle_abilities(self, card):
        for ability in card.abilities:
            match ability:
                case "hero":
                    pass
                case "muster":
                    pass
                case "recall":
                    pass
                case "agile":
                    pass
                case "morale":
                    pass
                case "spy":
                    pass
                case "scorchRow":
                    pass
                case "medic":
                    pass
                case "bond":
                    pass
                case "berserk":
                    pass
                case "thirsty":
                    pass

    def pass_round(self, player_id):
        if self.current_player_id != player_id:
            print("wrong player")
            return  False

        self.players[player_id].passed = True

        self.next_turn()

        return True

    def next_turn(self):
        current_player = self.players[self.current_player_id]
        next_player = self.players[1 - self.current_player_id]

        if not next_player.passed:
            self.current_player_id = next_player.id
            return

        if current_player.passed:
            self.end_round()
            return

    def update_points(self):
        player0_pts, player1_pts = self.board.rows_sum()

        self.players[0].points = player0_pts
        self.players[1].points = player1_pts

    def start_game(self):
        #TODO game start
        self.first_player_id = random.randint(0, 1)
        self.ready = True

        for player in self.players:
            player.draw_cards(10)

        self.start_round()

    def end_game(self):
        pass

    def end_round(self):
        #TODO round end
        self.current_player_id = None
        player0, player1 = self.players[0], self.players[1]

        player0.passed = False
        player1.passed = False

        player0_pts, player1_pts = player0.points, player1.points
        self.round_history.append((player0_pts, player1_pts))

        if player0_pts > player1_pts:
            is_any_dead = player0.lower_hp()
        elif player1_pts > player0_pts:
            is_any_dead = player1.lower_hp()
        else:
            is_any_dead = player0.lower_hp()
            is_any_dead = player1.lower_hp() or is_any_dead

        if is_any_dead or self.current_round == 3:
            self.end_game()
            return

        self.board.clear_rows(self.players)
        self.board.clear_weather()
        self.update_points()

        self.start_round()

    def start_round(self):
        self.current_round += 1
        self.current_player_id = (self.first_player_id + self.current_round) % 2

    def game_tostring(self, player_id):
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