import time

from classes.Game import Game
from classes.Player import Player
from network.network import Network
from view.ConsoleView import ConsoleView


class ConsoleGamePresenter:
    def __init__(self, deck, commander):
        self.view = ConsoleView()
        self.n = Network()
        self.my_id = None
        self.seed = None
        self.me = None
        self.opponent = None
        self.game = None
        self.game_state = None

        self.register(deck, commander)

    def register(self, deck, commander):
        response, data = self.n.send(("register", [deck, commander]))

        if response != "ok":
            raise ValueError("No response")

        self.my_id, self.seed = data
        self.me = Player(deck, commander)
        self.game_state = "waiting-for-game"

    def run(self):
        while True:
            time.sleep(1)
            match self.game_state:
                case "waiting-for-game":
                    self.handle_waitingforgame()
                case "start-game":
                    self.handle_startgame()
                case "playing":
                    self.handle_turn(self.my_id)
                case "waiting":
                    if not self.handle_turn(1 - self.my_id):
                        raise ValueError("Illegal opponent move")
                case "game-over":
                    self.handle_gameover()
                case "waiting-for-endgame":
                    self.handle_waitingforendgame()
                case _:
                    return


    def handle_waitingforgame(self):
        response, data = self.n.send(("waiting-for-game", []))

        if response == "start-game":
            self.opponent = Player(data[0], data[1])
            self.game = Game(self.seed)

            players = [self.me, self.opponent] if self.my_id == 0 else [self.opponent, self.me]
            for p in players:
                self.game.add_player(p)

            self.game_state = 'start-game'

    def handle_startgame(self):
        # Scoia'tael choosing here
        self.game.start_game()
        self.game_state = 'playing' if self.game.current_player_id == self.my_id else "waiting"

    def handle_turn(self, player_id):
        self.view.show_game(self.game, self.my_id)

        own_turn = player_id == self.my_id
        if own_turn:
            card_id, row = self.view.get_card_input()
            move = "pass" if row == "pass" else "card"

        else:
            response, data = self.n.send(("waiting", []))
            if response == "ok":
                return True

            move, card_id, row = data

        if move == "pass":
            valid = self.game.pass_round(player_id)
        else:
            valid = self.game.play_card(player_id, card_id, row)

        if not valid:
            return False

        if own_turn:
            self.n.send(("play", [move, card_id, row]))

        if self.game.current_player_id == self.my_id:
            self.game_state = "playing"
        elif self.game.current_player_id == 1 - self.my_id:
            self.game_state = "waiting"
        else:
            self.view.show_game_history(self.game)
            self.game_state = "game-over"

        return True

    def handle_gameover(self):
        rematch = self.view.get_rematch()
        self.n.send(("rematch", [rematch]))

        self.game_state = "waiting-for-endgame" if rematch else "exit"

    def handle_waitingforendgame(self):
        response, data = self.n.send(("waiting-for-endgame", []))

        if response == "ok":
            return

        if data[0]:
            self.seed = data[1]
            self.game.set_seed(data[1])
            self.game_state = 'start-game'
        else:
            self.game_state = 'exit'