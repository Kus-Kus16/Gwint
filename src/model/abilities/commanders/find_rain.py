from src.model.abilities.commanders.find_base import FindBase


class FindRain(FindBase):
    def __init__(self, card):
        super().__init__(card, 5)