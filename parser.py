import typing as t
from constants import ScoreSystem, GameFormat
from context import RequestContext

def build_token_map(tokens: t.List[str]) -> t.MutableMapping[str, int]:
    return {tokens[i]: i for i in range(len(tokens))}


class Command:
    pass

class WannaPlayCommand(Command):
    def __init__(
        self, side_1: t.List[str], side_2: t.Optional[t.List[str]] = None,
        score_system: t.Optional[ScoreSystem] = None, game_format: t.Optional[GameFormat] = None
    ) -> None:
        super().__init__()

        self.side_1 = side_1
        self.side_2 = side_2
        self.score_system = score_system
        self.game_format = game_format

    @classmethod
    def generate(cls, tokens: t.List[str], ctx: RequestContext) -> "WannaPlayCommand":
        assert tokens[0].lower() == "wp" or tokens[0].lower() == "wannaplay"

        token_map = build_token_map(tokens)



        



class GoodGameCommand(Command):
    def __init__(
        self, side_1: t.List[str], side_2: t.List[str],
        score_1: int, score_2: int
    ) -> None:
        super().__init__()

        self.side_1 = side_1
        self.side_2 = side_2
        self.score_1 = score_1
        self.score_2 = score_2

def parse_query(query: str) -> Command:
    tokens = query.split()

