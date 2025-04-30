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
        self.game_state = "menu"

        self.deck = deck
        self.commander = commander


    def connect(self, deck, commander):
        self.n.connect()
        response, data = self.n.send(("register", [deck, commander]))

        if response != "ok":
            raise ValueError("No response")

        self.my_id, self.seed = data
        self.me = Player(deck, commander)

    def disconnect(self):
        if self.n.is_connected():
            self.n.disconnect()

    def run(self):
        while True:
            # time.sleep(0.05)
            # self.view.draw()
            match self.game_state:
                case "menu":
                    pass
                case "credits":
                    pass
                case "deck":
                    pass

                case "waiting-for-game":
                    self.handle_waitingforgame()
                case "start-game":
                    self.handle_startgame()
                case "playing":
                    pass
                case "waiting":
                    self.handle_opponentturn()
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
            self.view.game.set_game(self.game, self.my_id)
            self.view.change_scene(self.view.game)

    def handle_startgame(self):
        # Scoia'tael choosing here
        self.game.start_game()
        self.turn_switch()

    def play_card(self, player_id, card_id, row):
        return self.game.play_card(player_id, card_id, row)

    def pass_round(self, player_id):
        return self.game.pass_round(player_id)

    def handle_opponentturn(self):
        response, data = self.n.send(("waiting", []))

        #Still waiting
        if response == "ok":
            return

        valid = False
        match data[0]:
            case "card":
                valid = self.play_card(1 - self.my_id, data[1], data[2])
            case "pass":
                valid = self.pass_round(1 - self.my_id)

        if not valid:
            raise ValueError("Illegal opponent move")

        self.turn_switch()

    def handle_gameover(self):
        pass
        # event = self.view.get_event()
        #
        # if event is None:
        #     return True
        #
        # if event.type == "rematch":
        #     rematch = event.rematch
        #     self.n.send(("rematch", [rematch]))
        #
        #     self.game_state = "waiting-for-endgame" if rematch else "exit"

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

    # Called by view after user input
    def notify(self, action):
        match action["type"]:
            case "mode_change":
                self.handle_mode_change(action)
            case "play":
                self.handle_play(action)

        self.view.unlock()

    def handle_mode_change(self, action):
        match action["mode"]:
            case "start_game":
                self.connect(self.deck, self.commander)
                self.game_state = "waiting-for-game"
                self.view.change_scene(self.view.waiting)
            case "menu":
                self.game_state = "menu"
                self.disconnect()
                self.view.change_scene(self.view.menu)
            case "credits":
                self.game_state = "credits"
                self.disconnect()
                self.view.change_scene(self.view.credits)
            case "deck":
                self.game_state = "deck"
                self.disconnect()
                self.view.change_scene(self.view.deck)
            case "exit":
                self.game_state = "exit"
                self.disconnect()
                self.view.running = False

    def handle_play(self, action):
        if action["card_id"] is None:
            if not self.pass_round(self.my_id):
                self.turn_switch()
                return

            self.n.send(("play", ["pass"]))
            self.turn_switch()
            return


        card_id = action["card_id"]
        row = action["row"]
        if not self.play_card(self.my_id, card_id, row):
            self.turn_switch()
            return

        self.n.send(("play", ["card", card_id, row]))
        self.turn_switch()

    def turn_switch(self):
        if self.game.current_player_id == self.my_id:
            self.game_state = "playing"
            self.view.unlock()
        elif self.game.current_player_id == 1 - self.my_id:
            self.game_state = "waiting"
            self.view.lock()
        else:
            #TODO
            self.view.show_game_history(self.game)
            self.game_state = "game-over"
            self.view.unlock()