from enum import Enum

class FactionType(Enum):
    NEUTRALNE = 0
    POLNOC = 1
    NILFGAARD = 2
    POTWORY = 3
    SCOIATAEL = 4
    SKELLIGE = 5
    TOUSSAINT = 6
    OGIEN = 7

    @classmethod
    def fullname_to_faction(cls, fullname):
        return cls._get_fullname_map().get(fullname)

    @classmethod
    def faction_to_fullname(cls, faction):
        rev_map = {value: key for key, value in cls._get_fullname_map().items()}
        return rev_map.get(faction)

    @classmethod
    def _get_fullname_map(cls):
        return {
            "Neutralne": cls.NEUTRALNE,
            "Królestwa Północy": cls.POLNOC,
            "Cesarstwo Nilfgaardu": cls.NILFGAARD,
            "Potwory": cls.POTWORY,
            "Scoia'tael": cls.SCOIATAEL,
            "Skellige": cls.SKELLIGE,
            "Księstwo Toussaint": cls.TOUSSAINT,
            "Kult Wiecznego Ognia": cls.OGIEN
        }
