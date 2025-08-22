from abc import abstractmethod


class TemporaryDrawable:
    def __init__(self, locking, frames):
        self.frames = frames
        self.locking = locking
        self.starting_lock = None

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def can_be_handled(self):
        pass