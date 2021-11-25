from enum import Enum

class GameFormat(Enum, str):
    SINGLES = "1v1"
    DOUBLES = "2v2"

class ScoreSystem(Enum, str):
    TILL_5 = "till5"
    TILL_10 = "till10"
