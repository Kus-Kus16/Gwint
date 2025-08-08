from src.model.abilities.commanders.find_base import FindBase


class FindScorch(FindBase):
    def __init__(self, card):
        super().__init__(card, 2)