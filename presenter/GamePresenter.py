import json
import queue
import time

from classes import CardsDatabase
from classes.Game import Game
from classes.Player import Player
from network.network import Network
from view import Constants as C


class GamePresenter:
    def __init__(self, view):
        self.view = view
        self.n = Network()
        self.my_id = None
        self.seed = None
        self.me = None
        self.opponent = None
        self.game = None
        self.game_state = "menu"
        self.actions = queue.Queue()
        self.carousel_dict = {}

        self.deck = None
        self.commander = None

        self.one_passed = False

    def connect(self, deck, commander):
        try:
            self.n.connect()
            response, data = self.n.send(("register", [deck, commander]))
        except ConnectionError:
            self.return_to_menu("Serwer nie odpowiada")
            return False

        if response != "ok":
            raise ConnectionError("Server responded with '%s'" % response)

        self.my_id, self.seed = data
        self.me = Player(deck, commander)

        return True

    def disconnect(self):
        if self.n.connected:
            self.n.disconnect()

    def run(self):
        sleep_time = 1 / C.FRAMERATE
        while True:
            time.sleep(sleep_time)
            self.process_actions()
            match self.game_state:
                case "waiting-for-game":
                    self.handle_waitingforgame()
                case "setup-game":
                    self.handle_setupgame()
                case "waiting-for-redraw":
                    self.handle_opponentredraw()
                case "waiting":
                    self.handle_opponentturn()
                case "waiting-for-endgame":
                    self.handle_waitingforendgame()
                case "exit":
                    return

    def handle_waitingforgame(self):
        response, data = self.n.send(("waiting", []))

        # Still waiting
        if response == "ok":
            return

        # Opponent disconnected
        if response == "error":
            self.return_to_menu("Przeciwnik rozłączył się")
            return

        self.opponent = Player(data[0], data[1])
        self.game = Game(self.seed)

        players = [self.me, self.opponent] if self.my_id == 0 else [self.opponent, self.me]
        for p in players:
            self.game.add_player(p)

        self.game_state = "setup-game"
        self.view.game.set_game(self.game, self.my_id)
        self.view.change_scene(self.view.game)
        self.view.lock()

    def handle_setupgame(self):
        self.game.start_game()  # Commanders!
        # Scoia'tael choosing here
        notif = "start" if self.game.first_player_id == self.my_id else "op_start"
        self.notification(notif)

        self.game_state = "redraw"
        self.carousel_dict["targets"] = []
        player = self.game.get_player(self.my_id)
        cards = player.hand.cards
        self.show_carousel(cards, choose_count=player.redraws, cancelable=True)

    def handle_opponentredraw(self):
        response, data = self.n.send(("waiting", []))

        #Still waiting
        if response == "ok":
            return

        #Opponent disconnected
        if response == "error":
            self.return_to_menu("Przeciwnik rozłączył się.")
            return

        if not self.redraw_cards(1 - self.my_id, data):
            raise ValueError("Illegal opponent redraw")

        self.game.end_redraws()
        self.start_round()
        self.notification("round_start")
        self.turn_switch()

    def handle_opponentturn(self):
        response, data = self.n.send(("waiting", []))

        #Still waiting
        if response == "ok":
            return

        #Opponent disconnected
        if response == "error":
            self.return_to_menu("Przeciwnik rozłączył się.")
            return

        print("RECEIVED:", data)
        valid = False
        match data[0]:
            case "card":
                valid = self.play_card(1 - self.my_id, data[1], data[2], data[3])
            case "pass":
                self.notification("pass_op")
                valid = self.pass_round(1 - self.my_id)

        if not valid:
            raise ValueError("Illegal opponent move", data)

        self.turn_switch()

    def handle_waitingforendgame(self):
        response, data = self.n.send(("waiting", []))

        #Still waiting
        if response == "ok":
            return

        #Opponent disconnected
        if response == "error" or not data[0]:
            self.return_to_menu("Przeciwnik rozłączył się.")
            return

        self.game_state = 'setup-game'

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

    def play_card(self, player_id, card_id, row, targets):
        return self.game.play_card(player_id, card_id, row, list(targets))

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
                "win_round" if self.game.is_winning_round(self.my_id)
                else "lose_round" if self.game.is_winning_round(1 - self.my_id)
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

    def redraw_cards(self, player_id, targets):
        return self.game.redraw_cards(player_id, targets)

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
                case "show_carousel":
                    self.handle_show_carousel(action) if action["carousel"] != "zoom" else self.handle_show_zoom(action)
                case "carousel":
                    self.handle_carousel(action)

    def handle_mode_change(self, action):
        match action["mode"]:
            case "start_game":
                self.game_state = "load_deck"
                self.disconnect()
                self.view.change_scene(self.view.deck, mode="start")
            case "load_deck":
                with open("./user/user_decks.json", "r", encoding="utf-8") as file:
                    decks = json.load(file)

                deck_data = decks[action["deck_id"]]
                commander_id = deck_data["commander_id"]
                cards = deck_data["cards"]

                valid, payload = CardsDatabase.create_verified_deck(cards, commander_id)
                if not valid:
                    raise ValueError(f"Illegal deck, problem with card or commander: {payload}")

                deck, commander = payload
                if self.connect(deck, commander):
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
                self.view.change_scene(self.view.deck, mode="menu")
            case "exit":
                self.game_state = "exit"
                self.disconnect()
                self.view.running = False

        self.view.unlock()

    def set_deck_and_commander(self, deck, commander):
        self.deck = deck
        self.commander = commander

    def handle_play(self, action):
        if action["card_id"] is None:
            self.view.current_scene.deselect()
            self.notification("pass")

            if not self.pass_round(self.my_id):
                self.relock()
                return

            response, data = self.n.send(("play", ["pass"]))
            # Opponent disconnected
            if response == "error":
                self.return_to_menu("Przeciwnik rozłączył się.")
                return

            self.turn_switch()
            return

        card_id = action["card_id"]
        row = action["row"]
        targets = action.get("targets", [])
        result = self.play_card(self.my_id, card_id, row, targets)
        if not result:
            self.relock()
            return

        if not result is True:
            self.show_carousel(result)

        response, data = self.n.send(("play", ["card", card_id, row, targets]))
        # Opponent disconnected
        if response == "error":
            self.return_to_menu("Przeciwnik rozłączył się.")
            return

        self.view.current_scene.deselect()
        self.turn_switch()

    def handle_gameover(self, action):
        rematch = action["rematch"]
        self.game.end_game()

        response, data = self.n.send(("rematch", [rematch]))
        # Opponent disconnected
        if response == "error":
            self.return_to_menu("Przeciwnik rozłączył się.")
            return

        if rematch:
            self.seed = data[0]
            self.game.set_seed(data[0])
            self.game_state = "waiting-for-endgame"
            self.view.current_scene.reset()
        else:
            self.return_to_menu(None)

    def handle_show_zoom(self, action):
        row = action["row"]
        if row in ["GRAVE", "GRAVE_OPP"]:
            player_id = self.my_id if row == "GRAVE" else 1 - self.my_id
            cards = self.game.get_player(player_id).get_grave_cards(playable_only=False)
        elif row in ["COMMANDER", "COMMANDER_OPP"]:
            player_id = self.my_id if row == "COMMANDER" else 1 - self.my_id
            cards = [self.game.get_player(player_id).commander]
        elif row == "WEATHER":
            cards = self.game.board.weather.cards
        else:
            cards = self.game.board.get_row_by_name(row, self.my_id).cards

        if len(cards) > 0:
            self.show_carousel(cards, choose_count=0, cancelable=True)
        else:
            self.relock()

    def handle_show_carousel(self, action):
        self.carousel_dict["card_id"] = action["card_id"]
        self.carousel_dict["row"] = action["row"]
        self.carousel_dict["targets"] = []
        self.view.current_scene.deselect()

        cards = []
        match action["ability"]:
            case "medic":
                if not self.game.gamerule("healRandom"):
                    cards = self.game.get_player(self.my_id).get_grave_cards(playable_only=True)
                    if cards:
                        self.show_carousel(cards, choose_count=-1, cancelable=False)
            case "chooseEnemyGrave":
                cards = self.game.get_player(1 - self.my_id).get_grave_cards(playable_only=True)
                if cards:
                    self.show_carousel(cards, choose_count=1, cancelable=False)

        if len(cards) == 0:
            self.notify({
                "type": "play",
                "card_id": action["card_id"],
                "row": action["row"]
            })

    def handle_carousel(self, action):
        if self.game_state == "redraw":
            self.handle_redrawcarousel(action)
        else:
            self.handle_playcarousel(action)
            self.relock()

    def handle_redrawcarousel(self, action):
        if action["card_id"] is not None:
            card_id = action["card_id"]
            if not self.redraw_cards(self.my_id, [card_id]):
                raise ValueError("Illegal self redraw")

            self.carousel_dict["targets"].append(card_id)
            new_cards = self.game.get_player(self.my_id).hand.cards
            self.view.current_scene.set_card_carousel(list(new_cards))

        if action["end"]:
            response, data = self.n.send(("play", self.carousel_dict["targets"]))

            # Opponent disconnected
            if response == "error":
                self.return_to_menu("Przeciwnik rozłączył się.")
                return

            self.carousel_dict.clear()
            self.game_state = "waiting-for-redraw"

            self.view.current_scene.discard_card_carousel()
            self.view.lock()
        else:
            self.view.unlock()

    def handle_playcarousel(self, action):
        if action["card_id"] is None:
            self.view.current_scene.discard_card_carousel()
            return

        self.carousel_dict["targets"].append(action["card_id"])
        if action["end"]:
            self.notify({
                "type": "play",
                "card_id": self.carousel_dict["card_id"],
                "row": self.carousel_dict["row"],
                "targets": self.carousel_dict["targets"]
            })
            self.carousel_dict.clear()
            self.view.current_scene.discard_card_carousel()
        else:
            self.view.unlock()

    def show_carousel(self, cards, choose_count=0, cancelable=False):
        self.view.run_later(lambda: self.view.current_scene.show_card_carousel(cards, choose_count, cancelable))

    def turn_switch(self):
        if self.game.current_player_id == self.my_id:
            self.game_state = "playing"
            if not self.one_passed:
                self.notification("playing")
        elif self.game.current_player_id == 1 - self.my_id:
            self.game_state = "waiting"
            if not self.one_passed:
                self.notification("waiting")

        self.relock()

    def relock(self):
        if self.game.current_player_id == 1 - self.my_id:
            self.view.lock()
        else:
            self.view.unlock()

    def notification(self, name, seconds=1.5):
        # return
        self.view.run_later(lambda: self.view.notification(name, seconds=seconds))

    def return_to_menu(self, reason):
        self.game_state = "menu"
        self.disconnect()

        if self.game:
            self.game.end_game()

        scene = self.view.current_scene
        self.view.change_scene(self.view.menu)
        scene.reset_all()

        if reason is not None:
            self.notification(reason)