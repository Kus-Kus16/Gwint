from enum import Enum


class RowType(Enum):
    CLOSE = 0
    RANGED = 1
    SIEGE = 2
    CLOSE_OPP = 3
    RANGED_OPP = 4
    SIEGE_OPP = 5
    ANY = 6