from enum import Enum

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
            cls.NEUTRAL: "Neutralne",
            cls.NORTH: "Królestwa Północy",
            cls.NILFGAARD: "Cesarstwo Nilfgaardu",
            cls.MONSTERS: "Potwory",
            cls.SCOIATAEL: "Scoia'tael",
            cls.SKELLIGE: "Skellige",
            cls.TOUSSAINT: "Księstwo Toussaint",
            cls.FIRE: "Kult Wiecznego Ognia",
        }