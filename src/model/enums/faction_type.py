from enum import Enum

from src.presenter.settings import locale


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
    def fullname_to_faction(cls, fullname):
        rev_map = {value: key for key, value in cls._get_fullname_map().items()}
        return rev_map.get(fullname)

    @classmethod
    def faction_to_fullname(cls, faction):
        return cls._get_fullname_map().get(faction)

    @classmethod
    def _get_fullname_map(cls):
        return {
            cls.NEUTRAL: locale("faction.neutral"),
            cls.NORTH: locale("faction.north"),
            cls.NILFGAARD: locale("faction.nilfgaard"),
            cls.MONSTERS: locale("faction.monsters"),
            cls.SCOIATAEL: locale("faction.scoiatael"),
            cls.SKELLIGE: locale("faction.skellige"),
            cls.TOUSSAINT: locale("faction.toussaint"),
            cls.FIRE: locale("faction.fire"),
        }