import threading
import time

class GameStates:
    def __init__(self):
        self.states = [[], []]
        self.seed = int(time.time())
        self.reseeded = False
        self.lock = threading.Lock()

    def add_state(self, player_id, state):
        with self.lock:
            self.states[player_id].append(state)

    def get_state(self, player_id):
        with self.lock:
            return self.states[player_id].pop(0) if self.states[player_id] else None

    def reseed(self):
        with self.lock:
            self.reseeded = not self.reseeded
            if self.reseeded:
                self.seed = int(time.time())

            return self.seed
