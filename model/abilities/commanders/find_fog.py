from model.abilities.commanders.find_base import FindBase


class FindFog(FindBase):
    def __init__(self, card):
        super().__init__(card, 4)