import typing as t
from common import ScoreSystem, GameFormat, ParseException, RequestContext

def build_token_map(tokens: t.List[str]) -> t.MutableMapping[str, int]:
    return {tokens[i]: i for i in range(len(tokens))}

class Command:
    pass

class WannaPlayCommand(Command):
    def __init__(
        self, owner: str, preferred_coplayers: t.Optional[t.List[str]] = None,
        score_system: t.Optional[ScoreSystem] = None, game_format: t.Optional[GameFormat] = None
    ) -> None:
        super().__init__()

        self.owner = owner
        self.preferred_coplayers = preferred_coplayers
        self.score_system = score_system
        self.game_format = game_format

    @classmethod
    def generate(cls, tokens: t.List[str], ctx: RequestContext) -> "WannaPlayCommand":
        coplayers = []
        
        for i in range(len(tokens)):
            if tokens[i][0] == "@":
                coplayers.append(tokens[i])
        
        assert tokens[0].lower() == "wp" or tokens[0].lower() == "wannaplay"

        token_map = build_token_map(tokens)

        score_system: t.Optional[ScoreSystem] = None

        if "till" in token_map:
            limit_index = token_map["till"] + 1

            try:
                score_limit = int(tokens[limit_index])

                if score_limit != 5 and score_limit != 10:
                    raise ParseException(f"unsupported score limit: {score_limit}")
                
                score_system = ScoreSystem[f"TILL_{score_limit}"]
            except ParseException as e:
                raise e
            except:
                raise ParseException(f"malformatted score limit")


        game_format: t.Optional[GameFormat] = None

        if "1v1" in token_map or "singles" in token_map:
            game_format = GameFormat.SINGLES
        elif "2v2" in token_map or "doubles" in token_map:
            game_format = GameFormat.DOUBLES

        return WannaPlayCommand(ctx.caller_id, coplayers, score_system, game_format)

class GoodGameCommand(Command):
    def __init__(
        self,
        winner_1: str, winner_2: t.Optional[str],
        loser_1: str, loser_2: t.Optional[str],
        score_1: int, score_2: int,
        player_out: t.Optional[str]
    ) -> None:
        super().__init__()

        self.winner_1 = winner_1
        self.winner_2 = winner_2
        self.loser_1 = loser_1
        self.loser_2 = loser_2
        self.score_1 = score_1
        self.score_2 = score_2
        self.player_out = player_out

    @classmethod
    def _extract_side_and_score(cls, tokens: t.Iterable[str], ctx: RequestContext) -> t.Tuple(t.List[str], int):
        side = []
        side_score = 0

        for t in tokens:
            if t[0] == "@":
                side.append(t)
            elif t == "me":
                side.append(ctx.caller_id)
            elif t == "out":
                continue
            else:
                try:
                    score = int(t)
                    
                    if score < 0 or score > 10:
                        raise ParseException(f"Incorrect score value: {score}")
                    
                    side_score = score
                except ParseException as e:
                    raise e
                except:
                    raise ParseException(f"Unsupported score format: {t}")

        if not side:
            raise ParseException(f"Empty list of players for one of the sides")

        if len(side) > 2:
            raise ParseException(f"Too many players on one of the sides: {side}")

        return (side, side_score)
    
    @classmethod
    def generate(cls, tokens: t.List[str], ctx: RequestContext) -> "GoodGameCommand":
        assert tokens[0].lower() == "gg" or tokens[0].lower() == "goodgame"

        token_map = build_token_map(tokens)

        assert "vs" in token_map

        vs_index = token_map["vs"]

        side_1, side_1_score = cls._extract_side_and_score(tokens[1:vs_index], ctx)
        side_2, side_2_score = cls._extract_side_and_score(tokens[vs_index+1:], ctx)

        player_out: t.Optional[str] = None
        
        if "out" in token_map:
            player_out = ctx.caller_id
        
        return GoodGameCommand(
            side_1[0], side_1[1] if len(side_1) == 2 else None,
            side_2[0], side_2[1] if len(side_2) == 2 else None,
            side_1_score, side_2_score,
            player_out
        )
        
class OutCommand(Command):
    def __init__(self, user_id: str) -> None:
        super().__init__()