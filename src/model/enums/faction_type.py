from enum import Enum


class FactionType(Enum):
    NEUTRAL = 0
    NORTH = 1
    NEUTRAL = 0
    NORTH = 1
    NILFGAARD = 2
    MONSTERS = 3
    MONSTERS = 3
    SCOIATAEL = 4
    SKELLIGE = 5
    TOUSSAINT = 6
    FIRE = 7

    @classmethod
    def faction_to_fullname(cls, faction_type):
        return cls._get_fullname_map().get(faction_type)

    @classmethod
    def faction_to_filename(cls, faction_type):
        return cls._get_filename_map().get(faction_type)

    @classmethod
    def _get_fullname_map(cls):
        return {
            cls.NEUTRAL: "Neutral",
            cls.NORTH: "Northern Realms",
            cls.NILFGAARD: "Nilfgaardian Empire",
            cls.MONSTERS: "Monsters",
            cls.SCOIATAEL: "Scoia'tael",
            cls.SKELLIGE: "Skellige",
            cls.TOUSSAINT: "Duchy of Toussaint",
            cls.FIRE: "Cult of Eternal Fire",
        }

    @classmethod
    def _get_filename_map(cls):
        return {
            cls.NEUTRAL: "neutral",
            cls.NORTH: "north",
            cls.NILFGAARD: "nilfgaard",
            cls.MONSTERS: "monsters",
            cls.SCOIATAEL: "scoiatael",
            cls.SKELLIGE: "skellige",
            cls.TOUSSAINT: "toussaint",
            cls.FIRE: "fire",
        }