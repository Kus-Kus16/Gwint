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
            cls.NEUTRAL: l("faction.neutral"),
            cls.NORTH: l("faction.north"),
            cls.NILFGAARD: l("faction.nilfgaard"),
            cls.MONSTERS: l("faction.monsters"),
            cls.SCOIATAEL: l("faction.scoiatael"),
            cls.SKELLIGE: l("faction.skellige"),
            cls.TOUSSAINT: l("faction.toussaint"),
            cls.FIRE: l("faction.fire"),
        }