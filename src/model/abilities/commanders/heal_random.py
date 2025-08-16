from src.model.abilities.commanders.gamerule_base import GameruleBase


class HealRandom(GameruleBase):
    def __init__(self, card):
        super().__init__(card, "heal_random")