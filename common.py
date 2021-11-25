import typing as t
from enum import Enum

class GameFormat(str, Enum):
    SINGLES = "1v1"
    DOUBLES = "2v2"

class ScoreSystem(str, Enum):
    TILL_5 = "till5"
    TILL_10 = "till10"

class ParseException(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)

class RequestContext:
    def __init__(self, caller_id: str, user_ids: t.Set[str]) -> None:
        self.caller_id = caller_id
        self.user_ids = user_ids
