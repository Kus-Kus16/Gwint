import json
import logging
import queue
import time

from model import cards_database as db
from model.enums.cards_area import CardsArea
from model.game import Game
from model.player import Player
from network.network import Network
from view import constants as c


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
        except ConnectionError as e:
            self.return_to_menu(["Serwer nie odpowiada:", str(e)])
            return False

        if response != "ok":
            raise ConnectionError(f"Server responded with: {response}")

        self.my_id, self.seed = data
        self.me = Player(deck, commander)

        return True

    def disconnect(self):
        if self.n.connected:
            self.n.disconnect()

    def run(self):
        sleep_time = 1 / c.FRAMERATE
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

        if not self.continue_with_response(response):
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
        self.game.start_game()
        # Scoia'tael choosing here
        notif = "start" if self.game.first_player_id == self.my_id else "op_start"
        self.notification(notif)

        self.game_state = "redraw"
        self.carousel_dict["targets"] = []
        player = self.game.get_player(self.my_id)
        cards = player.hand.cards
        self.show_carousel(cards, choose_count=player.redraws, cancelable=True, label=True)

    def handle_opponentredraw(self):
        response, data = self.n.send(("waiting", []))

        if not self.continue_with_response(response):
            return

        try:
            self.redraw_cards(1 - self.my_id, data)
        except ValueError as e:
            raise ValueError(f"Illegal opponent redraw: {str(e)}")

        self.game.end_redraws()
        self.start_round()
        self.notification("round_start")
        self.turn_switch()

    def handle_opponentturn(self):
        response, data = self.n.send(("waiting", []))

        if not self.continue_with_response(response):
            return

        try:
            if data[0] == "card":
                self.play_card(1 - self.my_id, data[1], data[2], data[3])
            else: # pass
                self.notification("pass_op")
                self.pass_round(1 - self.my_id)
        except ValueError as e:
            raise ValueError(f"Illegal opponent turn: {str(e)}")

        self.turn_switch()

    def handle_waitingforendgame(self):
        response, data = self.n.send(("waiting", []))

        if not self.continue_with_response(response):
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

    def play_card(self, player_id, card_id, row_type, targets):
        return self.game.play_card(player_id, card_id, row_type, list(targets))

    def pass_round(self, player_id):
        self.game.pass_round(player_id)

        if not self.one_passed:
            self.one_passed = True
            if self.game_state != "game-over":
                self.notification("waiting" if player_id == self.my_id else "playing")

            return

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
            return

        self.start_round()
        self.notification("round_start")

    def redraw_cards(self, player_id, targets):
        self.game.redraw_cards(player_id, targets)

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
                self.game_state = "deck"
                self.disconnect()
                self.view.change_scene(self.view.deck)
            case "load_deck":
                self.handle_load_deck(action)
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

        self.view.unlock()

    def handle_load_deck(self, action):
        with open("./user/user_decks.json", "r", encoding="utf-8") as file:
            decks = json.load(file)

        deck_data = decks[action["deck_id"]]
        commander_id = deck_data["commander_id"]
        cards = deck_data["cards"]

        try:
            deck, commander = db.create_verified_deck(cards, commander_id)
            if self.connect(deck, commander):
                self.game_state = "waiting-for-game"
                self.view.change_scene(self.view.waiting)
        except ValueError as e:
            self.return_to_menu(["Niepoprawna talia:", str(e)], seconds=3)

    def handle_play(self, action):
        if action["card_id"] is None:
            self.handle_play_pass()
            return

        self.handle_play_card(action)

    def handle_play_card(self, action):
        card_id = action["card_id"]
        row_type = action["row_type"]
        targets = action.get("targets", [])

        try:
            to_show = self.play_card(self.my_id, card_id, row_type, targets)
            self.show_carousel(to_show, cancelable=True)
        except ValueError as e:
            logging.info(f"Play card exception: {str(e)}")
            self.relock()
            return

        response, data = self.n.send(("play", ["card", card_id, row_type, targets]))
        if not self.continue_with_response(response, is_ok_blocking=False):
            return

        self.view.current_scene.deselect()
        self.turn_switch()

    def handle_play_pass(self):
        self.view.current_scene.deselect()
        self.notification("pass")

        try:
            self.pass_round(self.my_id)
        except ValueError as e:
            logging.info(f"Pass round exception: {str(e)}")
            self.relock()
            return

        response, data = self.n.send(("play", ["pass"]))
        if not self.continue_with_response(response, is_ok_blocking=False):
            return

        self.turn_switch()

    def handle_gameover(self, action):
        rematch = action["rematch"]
        self.game.end_game()

        response, data = self.n.send(("rematch", [rematch]))
        if not self.continue_with_response(response, is_ok_blocking=False, should_notify=rematch):
            return

        if rematch:
            self.seed = data[0]
            self.game.set_seed(data[0])
            self.game_state = "waiting-for-endgame"
            self.view.current_scene.reset()
        else:
            self.return_to_menu(None)

    def handle_show_zoom(self, action):
        row_type = action["row_type"]

        if row_type in {CardsArea.GRAVE_OPP, CardsArea.COMMANDER_OPP}:
            player_id = 1 - self.my_id
        else:
            player_id = self.my_id

        match row_type:
            case CardsArea.GRAVE | CardsArea.GRAVE_OPP:
                cards = self.game.get_player(player_id).get_grave_cards(playable_only=False)

            case CardsArea.COMMANDER | CardsArea.COMMANDER_OPP:
                cards = [self.game.get_player(player_id).commander]

            case CardsArea.WEATHER:
                cards = self.game.board.weather.cards

            case _:
                row, _ = self.game.board.get_row(row_type, self.my_id)
                cards = row.cards

        if len(cards) > 0:
            self.show_carousel(cards, choose_count=0, cancelable=True)
        else:
            self.relock()

    def handle_show_carousel(self, action):
        self.carousel_dict["card_id"] = action["card"].id
        self.carousel_dict["row_type"] = action["row_type"]
        self.carousel_dict["targets"] = []
        self.view.current_scene.deselect()

        additional_actions = []
        for ability in action["card"].abilities:
            actions = ability.on_carousel_request(self)
            additional_actions.extend(actions)

        for additional in additional_actions:
            additional()

        if not additional_actions:
            self.notify({
                "type": "play",
                "card_id": action["card"].id,
                "row_type": action["row_type"]
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
            self.redraw_cards(self.my_id, [card_id])

            self.carousel_dict["targets"].append(card_id)
            new_cards = self.game.get_player(self.my_id).hand.cards
            self.view.current_scene.set_card_carousel(list(new_cards))

        if action["end"]:
            response, data = self.n.send(("play", self.carousel_dict["targets"]))
            if not self.continue_with_response(response, is_ok_blocking=False):
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
                "row_type": self.carousel_dict["row_type"],
                "targets": self.carousel_dict["targets"]
            })
            self.carousel_dict.clear()
            self.view.current_scene.discard_card_carousel()
        else:
            self.view.unlock()

    def show_carousel(self, cards, choose_count=0, cancelable=False, label=False):
        if not cards:
            return

        self.view.run_later(lambda: self.view.current_scene.show_card_carousel(cards, choose_count, cancelable, label))

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
        if self.game.current_player_id == 1 - self.my_id or self.game_state == "waiting-for-redraw":
            self.view.lock()
        else:
            self.view.unlock()

    def notification(self, name, seconds=1.5):
        # return
        self.view.run_later(lambda: self.view.notification(name, seconds=seconds))

    def return_to_menu(self, reasons, seconds=1.5):
        self.game_state = "menu"
        self.disconnect()

        if self.game:
            self.game.end_game()

        scene = self.view.current_scene
        self.view.change_scene(self.view.menu)
        scene.reset_all()

        if reasons is not None:
            self.notification(reasons, seconds=seconds)

    # Returns True if calling function should continue
    def continue_with_response(self, server_response, is_ok_blocking=True, should_notify=True):
        #Still waiting
        if is_ok_blocking and server_response == "ok":
            return False

        #Opponent disconnected
        if server_response == "error":
            reasons = ["Przeciwnik rozłączył się."] if should_notify else None
            self.return_to_menu(reasons)
            return False

        return True