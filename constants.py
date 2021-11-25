from enum import Enum

class GameFormat(str, Enum):
    SINGLES = "1v1"
    DOUBLES = "2v2"

class ScoreSystem(str, Enum):
    TILL_5 = "till5"
    TILL_10 = "till10"
