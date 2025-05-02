import queue
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
        self.game_state = "menu"
        self.actions = queue.Queue()

        self.deck = deck
        self.commander = commander

        self.one_passed = False

    def connect(self, deck, commander):
        try:
            self.n.connect()
            response, data = self.n.send(("register", [deck, commander]))
        except Exception:
            print("Server not responding")
            return False

        if response != "ok":
            raise ValueError("No response")

        self.my_id, self.seed = data
        self.me = Player(deck, commander)

        return True

    def disconnect(self):
        if self.n.is_connected():
            self.n.disconnect()

    def run(self):
        while True:
            time.sleep(0.01)
            self.process_actions()
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
                    pass
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
        notif = "start" if self.game.first_player_id == self.my_id else "op_start"
        self.notification(notif)
        # Redraw here
        self.start_round()
        self.notification("round_start")
        self.turn_switch()

    def start_round(self):
        self.game.start_round()

    def end_round(self):
        self.game.end_round()

        if self.game.current_round == 3 or self.me.is_dead() or self.opponent.is_dead():
            self.end_game()
            return True

        return False

    def end_game(self):
        self.game_state = "game-over"

        if self.me.is_dead() and self.opponent.is_dead():
            result = "draw"
        elif self.opponent.is_dead():
            result = "win"
        else:
            result = "lose"

        self.view.current_scene.end_game(result, self.game.get_round_history(self.my_id))

    def play_card(self, player_id, card_id, row):
        return self.game.play_card(player_id, card_id, row)

    def pass_round(self, player_id):
        if not self.game.pass_round(player_id):
            return False

        if not self.one_passed:
            self.one_passed = True
            if self.game_state != "game-over":
                self.notification("waiting" if player_id == self.my_id else "playing")
        else:
            self.one_passed = False
            notif = (
                "win_round" if self.game.winning_round(self.my_id)
                else "lose_round" if self.game.winning_round(1 - self.my_id)
                else "draw_round"
            )
            self.notification(notif)

            game_ended = self.end_round()
            if game_ended:
                self.end_game()
                return True

            self.start_round()
            self.notification("round_start")

        return True

    def handle_opponentturn(self):
        response, data = self.n.send(("waiting", []))

        #Still waiting
        if response == "ok":
            return

        #Opponent disconnected
        if response == "error":
            self.return_to_menu()
            return

        valid = False
        match data[0]:
            case "card":
                valid = self.play_card(1 - self.my_id, data[1], data[2])
            case "pass":
                self.notification("pass_op")
                valid = self.pass_round(1 - self.my_id)

        if not valid:
            raise ValueError("Illegal opponent move")

        self.turn_switch()

    def handle_waitingforendgame(self):
        response, data = self.n.send(("waiting-for-endgame", []))

        #Still waiting
        if response == "ok":
            return

        #Opponent disconnected
        if response == "error" or not data[0]:
            self.return_to_menu()
            return

        self.seed = data[1]
        self.game.set_seed(data[1])
        self.game_state = 'start-game'

    def is_waiting_for_player(self):
        return self.game_state == "waiting-for-game"

    # Called by view after user input
    def notify(self, action):
        self.actions.put(action)

    def process_actions(self):
        while not self.actions.empty():
            action = self.actions.get()
            print(action)
            match action["type"]:
                case "mode_change":
                    self.handle_mode_change(action)
                case "play":
                    self.handle_play(action)
                case "game-over":
                    self.handle_gameover(action)
                case _:
                    pass
                    self.view.unlock()

    def handle_mode_change(self, action):
        match action["mode"]:
            case "start_game":
                if self.connect(self.deck, self.commander):
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
                pass
                # self.game_state = "deck"
                # self.disconnect()
                # self.view.change_scene(self.view.deck)
            case "exit":
                self.game_state = "exit"
                self.disconnect()
                self.view.running = False

        self.view.unlock()

    def handle_play(self, action):
        if action["card_id"] is None:
            self.view.current_scene.deselect()
            self.notification("pass")

            if not self.pass_round(self.my_id):
                self.turn_switch()
                return

            response, data = self.n.send(("play", ["pass"]))
            # Opponent disconnected
            if response == "error":
                self.return_to_menu()
                return

            self.turn_switch()
            return

        card_id = action["card_id"]
        row = action["row"]
        if not self.play_card(self.my_id, card_id, row):
            self.turn_switch()
            return

        response, data = self.n.send(("play", ["card", card_id, row]))
        # Opponent disconnected
        if response == "error":
            self.return_to_menu()
            return

        self.view.current_scene.deselect()
        self.turn_switch()

    def handle_gameover(self, action):
        rematch = action["rematch"]
        self.game.end_game()

        response, data = self.n.send(("rematch", [rematch]))
        # Opponent disconnected
        if response == "error":
            self.return_to_menu()
            return

        if rematch:
            self.game_state = "waiting-for-endgame"
            self.view.current_scene.reset()
        else:
            self.return_to_menu()

    def turn_switch(self):
        if self.game.current_player_id == self.my_id:
            self.game_state = "playing"
            self.view.unlock()
            if not self.one_passed:
                self.notification("playing")
        elif self.game.current_player_id == 1 - self.my_id:
            self.game_state = "waiting"
            self.view.lock()
            if not self.one_passed:
                self.notification("waiting")
        else:
            self.view.unlock()

    def notification(self, name, seconds=1.5):
        return
        self.view.run_later(lambda: self.view.notification(name, seconds=seconds))

    def return_to_menu(self):
        self.game_state = "menu"
        self.disconnect()
        scene = self.view.current_scene
        self.view.change_scene(self.view.menu)
        scene.reset_all()