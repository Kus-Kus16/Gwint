from enum import Enum

from src.presenter.settings import locale as l


class FactionType(Enum):
    NEUTRAL = 0
    NORTH = 1
    NILFGAARD = 2
    MONSTERS = 3
    SCOIATAEL = 4
    SKELLIGE = 5
    TOUSSAINT = 6
    FIRE = 7

    @classmethod
    def faction_to_fullname(cls, faction):
        return cls._get_fullname_map().get(faction)

    @classmethod
    def _get_fullname_map(cls):
        return {
            cls.NEUTRAL: l("Neutral"),
            cls.NORTH: l("Northern Realms"),
            cls.NILFGAARD: l("Nilfgaardian Empire"),
            cls.MONSTERS: l("Monsters"),
            cls.SCOIATAEL: l("Scoia'tael"),
            cls.SKELLIGE: l("Skellige"),
            cls.TOUSSAINT: l("Duchy of Toussaint"),
            cls.FIRE: l("Cult of Eternal Fire"),
        }