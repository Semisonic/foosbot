import typing as t
from common import RequestContext, ParseException
import commands as c


def process_user_ids(tokens: t.List[str], ctx: RequestContext) -> t.List[str]:
    for i in range(len(tokens)):
        t = tokens[i]

        if t[0] != "<":
            tokens[i] = t.lower()

        if t[-1] != ">":
            raise ParseException("Please don't use '<' and '>' in your queries")
        
        user_id = t[1:-1]

        if user_id not in ctx.user_ids:
            raise ParseException(f"Invalid user id: {user_id}")
        
        tokens[i] = user_id

    return tokens


def parse_query(query: str, ctx: RequestContext) -> c.Command:
    tokens = process_user_ids(query.split(), ctx)

    if tokens[0] == "wp":
        return c.WannaPlayCommand.generate(tokens, ctx)
    elif tokens[0] == "gg":
        return c.GoodGameCommand.generate(tokens, ctx)
    else:
        raise ParseException(f"Unrecornised command type: {tokens[0]}")

