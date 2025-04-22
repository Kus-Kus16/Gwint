import threading
import time

from classes.Game import Game
from classes.Player import Player
from network.network import Network


class GamePresenter:
    def __init__(self, deck, commander,view):
        self.view = view
        self.n = Network()
        self.my_id = None
        self.seed = None
        self.me = None
        self.opponent = None
        self.game = None
        self.game_state = None

        self.register(deck, commander)

        threading.Thread(target=self.view.run, daemon=True).start()



    def register(self, deck, commander):
        response, data = self.n.send(("register", [deck, commander]))

        if response != "ok":
            raise ValueError("No response")

        self.my_id, self.seed = data
        self.me = Player(deck, commander)
        self.game_state = "waiting-for-game"
        self.view.player_id = self.my_id

    def run(self):
        while True:
            time.sleep(0.05)
            self.game_state = self.view.mode
            self.view.game = self.game

            match self.game_state:
                case "menu":
                    pass
                case "credits":
                    pass
                case "deck":
                    pass

                case "register":
                    #TODO registering with data from view
                    pass
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

            self.game_state = "start-game"
            self.view.mode = "start-game"


    def handle_startgame(self):
        # Scoia'tael choosing here
        self.game.start_game()
        self.game_state = "playing" if self.game.current_player_id == self.my_id else "waiting"
        self.view.mode = "playing" if self.game.current_player_id == self.my_id else "waiting"

    def play_card(self, player_id, card_id, row):
        return self.game.play_card(player_id, card_id, row)

    def pass_round(self, player_id):
        return self.game.pass_round(player_id)

    def handle_ownturn(self):
        self.view.unlock()
        event = self.view.get_event()

        if event is None:
            return True

        match event["type"]:
            case "card":
                card_id = event["card_id"]
                row = event["row"]

                if not self.play_card(self.my_id, card_id, row):
                    return False

                self.n.send(("play", ["card", card_id, row]))

            case "pass":
                if not self.pass_round(self.my_id):
                    return False

                self.n.send(("play", ["pass"]))

            case "commander":
                # TODO
                pass

        return True

    def handle_opponentturn(self):
        response, data = self.n.send(("waiting", []))

        if response == "ok":
            return True

        match data[0]:
            case "card":
                return self.play_card(1 - self.my_id, data[1], data[2])
            case "pass":
                return self.pass_round(1 - self.my_id)



    def handle_turn(self, player_id):
        own_turn = player_id == self.my_id
        valid = self.handle_ownturn() if own_turn else self.handle_opponentturn()

        if not valid:
            return False

        if self.game.current_player_id == self.my_id:
            self.game_state = "playing"
            self.view.mode = "playing"
        elif self.game.current_player_id == 1 - self.my_id:
            self.game_state = "waiting"
            self.view.mode = "waiting"
        else:
            self.view.show_game_history(self.game)
            self.game_state = "game-over"

        return True

    def handle_gameover(self):
        event = self.view.get_event()

        if event is None:
            return True

        if event.type == "rematch":
            rematch = event.rematch
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

    def is_waiting_for_player(self):
        return self.game_state == "waiting-for-game"
