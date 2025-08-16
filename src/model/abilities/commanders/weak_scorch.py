from src.model.abilities.commanders.gamerule_base import GameruleBase


class WeakScorch(GameruleBase):
    def __init__(self, card):
        super().__init__(card, "weak_scorch")