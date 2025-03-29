from unittest import case

from classes.Board import Board


class Game:
    def __init__(self, id):
        self.ready = False
        self.id = id
        self.board = Board()
        self.players = []
        self.current_player = None

    def play_card(self, player, card_id, row_type):
        if self.current_player.id != player.id:
            print("wrong player")
            return

        card = player.hand.find_card_by_id(card_id)

        if card is None:
            print("wrong card")
            return

        if not card.is_row_playable(row_type):
            print("wrong row")
            return

        if card.is_special():
            #TODO special logic here
            self.handle_special(card)

            return

        self.handle_abilities(card)

        player.play_to_board(card)

        player0_pts, player1_pts = self.board.play_card(card, row_type, player.id)
        self.players[0].points = player0_pts
        self.players[1].points = player1_pts

        self.next_turn()

    def handle_special(self, card):
        for ability in card.abilities:
            match ability:
                case "decoy":
                    pass
                case "horn":
                    pass
                case "scorch":
                    pass
                case "clear":
                    pass
                case "frost":
                    pass
                case "rain":
                    pass
                case "storm":
                    pass
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

    def pass_round(self, player):
        if self.current_player.id != player.id:
            print("wrong player")
            return

        player.passed = True

        self.next_turn()

    def next_turn(self):
        next_player = self.players[1 - self.current_player.id]

        if not next_player.passed:
            self.current_player = next_player
            return

        if self.current_player.passed:
            self.end_round()
            return

    def start_game(self):
        #TODO game start
        self.current_player = self.players[0]

    def end_round(self):
        #TODO
        self.current_player = None

    def game_tostring(self, player_id):
        return self.board.rows_tostring(player_id) + "\n\n" + str(self.players[player_id])

    def add_player(self, player):
        player_count = len(self.players)

        if player_count > 1:
            return None

        self.players.append(player)
        return player_count
