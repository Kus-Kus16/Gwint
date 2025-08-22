import logging
import queue
import time

from src.model.cards import cards_database as db
from src.model.enums.cards_area import CardsArea
from src.model.enums.faction_type import FactionType
from src.model.game import Game
from src.model.player import Player
from src.network.network import Network
from src.presenter import loader, settings
from src.presenter.settings import locale as l
from src.view.constants import ui_constants as u


class GamePresenter:
    def __init__(self, view):
        self.view = view
        self.net = Network()
        self.my_id = None
        self.seed = None
        self.me = None
        self.opponent = None
        self.first_player = None
        self.game = None
        self.game_state = "menu"
        self.actions = queue.Queue()
        self.carousel_dict = {}

        self.quick_play = None
        self.on_setting_update()
        settings.register_observer(self, "quick_play")

    def connect(self, deck, commander):
        try:
            self.net.connect()
            response, data = self.net.send(("register", [deck, commander]))
        except ConnectionError as e:
            self.return_to_menu((f"{l("error.server_not_responding")}:", str(e)))
            return False

        if response != "ok":
            raise ConnectionError(f"{l("error.server_responded")}: {response}")

        self.my_id, self.seed = data

        return True

    def disconnect(self):
        if self.net.connected:
            self.net.disconnect()

    def run(self):
        sleep_time = 1 / u.FRAMERATE
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
        response, data = self.net.send(("waiting", []))

        if not self.continue_with_response(response):
            return

        cards, commander_id = data[0], data[1]
        try:
            deck, commander = db.create_verified_deck(cards, commander_id)
            self.opponent = Player(deck, commander)
        except ValueError:
            self.return_to_menu((l("error.deck.opponent"),), seconds=3)

        self.game = Game(self, self.seed)

        players = [self.me, self.opponent] if self.my_id == 0 else [self.opponent, self.me]
        for p in players:
            self.game.add_player(p)

        self.game_state = "setup-game"
        self.view.game.set_game(self.game, self.my_id)
        self.view.change_scene(self.view.game)
        self.view.lock()

    def handle_setupgame(self):
        # First time
        if self.first_player is None:
            has_scoia = self.game.compare_for_faction(FactionType.SCOIATAEL)
            if has_scoia == self.my_id:
                self.first_player = "choose"
                self.view.current_scene.choose_first_player()
                return
            elif has_scoia == (1 - self.my_id):
                self.first_player = "wait"
                self.notification_waiting()
                return
            else:
                first_player = None

        elif self.first_player == "choose":
            return

        elif self.first_player == "wait":
            response, data = self.net.send(("waiting", []))

            if not self.continue_with_response(response):
                return

            self.notification_discard()
            first_player = data[0]

        else:
            first_player = self.first_player

        self.game.start_game(first_player, self.my_id)

        self.game_state = "redraw"
        self.carousel_dict["targets"] = []
        player = self.game.get_player(self.my_id)
        cards = player.hand.cards
        self.show_carousel(cards, choose_count=player.redraws, cancelable=True, label=True, redraw_label=True)

    def handle_opponentredraw(self):
        response, data = self.net.send(("waiting", []))

        if not self.continue_with_response(response):
            return

        try:
            self.redraw_cards(1 - self.my_id, data)
        except ValueError as e:
            raise ValueError(f"Illegal opponent redraw: {str(e)}")

        self.game.end_redraws(self.my_id)
        self.notification_discard()
        self.turn_switch()

    def handle_opponentturn(self):
        response, data = self.net.send(("waiting", []))

        if not self.continue_with_response(response):
            return

        try:
            if data[0] == "card":
                self.play_card(1 - self.my_id, data[1], data[2], data[3])
            else: # pass
                self.pass_round(1 - self.my_id)
        except ValueError as e:
            raise ValueError(f"Illegal opponent turn: {str(e)}")

        self.turn_switch()

    def handle_waitingforendgame(self):
        response, data = self.net.send(("waiting", []))

        if not self.continue_with_response(response):
            return

        self.notification_discard()
        self.first_player = None
        self.game_state = 'setup-game'

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
        self.game.play_card(player_id, self.my_id, card_id, row_type, list(targets))

    def pass_round(self, player_id):
        self.game.pass_round(player_id, self.my_id)

    def redraw_cards(self, player_id, targets):
        self.game.redraw_cards(player_id, targets)

    # Called by view after userdata input
    def notify(self, action):
        self.actions.put(action)

    def process_actions(self):
        while not self.actions.empty():
            action = self.actions.get()
            match action["type"]:
                case "mode_change":
                    self.handle_mode_change(action)
                case "play":
                    self.handle_play(action)
                case "show_carousel":
                    self.handle_show_carousel(action) if action["carousel"] != "zoom" else self.handle_show_zoom(action)
                case "carousel":
                    self.handle_carousel(action)
                case "game-over":
                    self.handle_gameover(action)
                case "first-player":
                    self.handle_firstplayer(action)

    def handle_mode_change(self, action):
        match action["mode"]:
            case "new_game":
                self.handle_newgame(action)
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
            case "settings":
                self.game_state = "settings"
                self.disconnect()
                self.view.change_scene(self.view.settings)
            case "exit":
                self.game_state = "exit"
                self.disconnect()
                self.view.running = False

        self.view.unlock()

    def handle_newgame(self, action):
        load = action.get("load")
        if load is None:
            load = self.quick_play

        if not load:
            self.notify({"type": "mode_change", "mode": "deck"})
            return

        userdata = loader.load_data("user_decks", is_userdata=True)
        i = userdata["last_used_index"]
        deck_data = userdata["decks"][i]

        commander_id = deck_data["commander_id"]
        cards = deck_data["cards"]

        try:
            deck, commander = db.create_verified_deck(cards, commander_id)
            if self.connect(cards, commander_id):
                self.me = Player(deck, commander)
                self.game_state = "waiting-for-game"
                self.view.change_scene(self.view.waiting)
        except ValueError as e:
            self.return_to_menu((f"{l("error.deck.own")}:", str(e)), seconds=3)

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
            self.play_card(self.my_id, card_id, row_type, targets)
        except ValueError as e:
            logging.info(f"Play card exception: {str(e)}")
            self.relock()
            return

        response, data = self.net.send(("play", ["card", card_id, row_type, targets]))
        if not self.continue_with_response(response, is_ok_blocking=False):
            return

        self.view.current_scene.deselect()
        self.turn_switch()

    def handle_play_pass(self):
        self.view.current_scene.deselect()

        try:
            self.pass_round(self.my_id)
        except ValueError as e:
            logging.info(f"Pass round exception: {str(e)}")
            self.relock()
            return

        response, data = self.net.send(("play", ["pass"]))
        if not self.continue_with_response(response, is_ok_blocking=False):
            return

        self.turn_switch()

    def handle_gameover(self, action):
        want_rematch = action["rematch"]
        self.game.clear_game()

        response, data = self.net.send(("rematch", [want_rematch]))
        if not self.continue_with_response(response, is_ok_blocking=False, should_notify=want_rematch):
            return

        if want_rematch:
            self.seed = data[0]
            self.game.set_seed(data[0])
            self.game_state = "waiting-for-endgame"
            self.view.current_scene.reset()
            self.notification_waiting()
        else:
            self.return_to_menu(None)

    def handle_firstplayer(self, action):
        first_player = self.my_id if action["me"] else 1 - self.my_id
        self.first_player = first_player

        response, data = self.net.send(("play", [first_player]))
        self.continue_with_response(response, is_ok_blocking=False)
        self.view.current_scene.discard_temporary()
        self.relock()

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
            response, data = self.net.send(("play", self.carousel_dict["targets"]))
            if not self.continue_with_response(response, is_ok_blocking=False):
                return

            self.carousel_dict.clear()
            self.game_state = "waiting-for-redraw"
            self.view.current_scene.discard_temporary()
            self.notification_waiting()
            self.view.lock()
        else:
            self.view.unlock()

    def handle_playcarousel(self, action):
        if action["card_id"] is None:
            self.view.current_scene.discard_temporary()
            return

        self.carousel_dict["targets"].append(action["card_id"])
        if action["end"]:
            if action["allow_play"]:
                self.notify({
                    "type": "play",
                    "card_id": self.carousel_dict["card_id"],
                    "row_type": self.carousel_dict["row_type"],
                    "targets": self.carousel_dict["targets"]
                })
                self.carousel_dict.clear()
            self.view.current_scene.discard_temporary()
        else:
            self.view.unlock()

    def show_carousel(self, cards, choose_count=0, cancelable=False, label=False, redraw_label=False, allow_ending=True):
        if not cards:
            return

        self.view.run_later(lambda: self.view.current_scene.show_card_carousel(cards, choose_count,
               cancelable, label, redraw_label, allow_ending))

    def turn_switch(self):
        if self.game.current_player_id == self.my_id:
            self.game_state = "playing"
        elif self.game.current_player_id == 1 - self.my_id:
            self.game_state = "waiting"

        self.relock()

    def relock(self):
        if self.game.current_player_id == 1 - self.my_id:
            self.view.lock()
        else:
            self.view.unlock()

    def notification(self, name, seconds=1.5):
        self.view.notification(name, seconds=seconds)

    def notification_waiting(self):
        self.view.notification("waiting", frames=-1)

    def notification_discard(self):
        self.view.current_scene.pop_temporary()

    def return_to_menu(self, reasons, seconds=1.5):
        self.game_state = "menu"
        self.me = None
        self.disconnect()

        if self.game:
            self.game.clear_game()

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
            reasons = (l("error.disconnect.opponent"),) if should_notify else None
            self.return_to_menu(reasons)
            return False

        return True

    def on_setting_update(self):
        self.quick_play = settings.load_setting("quick_play")