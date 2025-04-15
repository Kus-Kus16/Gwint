import threading
import time

class GameStates:
    def __init__(self):
        self.states = [[], []]
        self.seed = int(time.time())
        self.lock = threading.Lock()

    def add_state(self, player_id, state):
        with self.lock:
            self.states[player_id].append(state)

    def get_state(self, player_id):
        with self.lock:
            return self.states[player_id].pop(0) if self.states[player_id] else None

    def reseed(self):
        self.seed = int(time.time())