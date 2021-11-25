import typing as t
import commands as c
from common import RequestContext
import db_interface as db

class ExecutionArtifact:
    pass

class SendMessageArtifact(ExecutionArtifact):
    def __init__(self, user_id: str, message: str) -> None:
        super().__init__()

        self.user_id = user_id
        self.message = message

def _execute_wp_command(cmd: c.WannaPlayCommand, ctx: RequestContext) -> t.List[ExecutionArtifact]:
    player_ids = db.execute_wp_command(cmd)
    
    artifacts: t.List[ExecutionArtifact] = []

    if not player_ids:
        artifacts.append(
            SendMessageArtifact(ctx.caller_id, "Your request has been accepted, please wait until someone matches it")
        )
    else:
        for player_id in player_ids:
            artifacts.append(
                SendMessageArtifact(player_id, "Get ready, your match is coming! 🔥")
            )

    return artifacts

def _wrap_user_id(user_id: str) -> str:
    return f"<{user_id}>"

def _build_gg_message(cmd: c.GoodGameCommand, match_id: int, user_id: str) -> str:
    message = f"Good game! Game ${match_id}: ";
    
    message += _wrap_user_id(cmd.side_1[0])
    if len(cmd.side_1) == 2:
        message += f" and {_wrap_user_id(cmd.side_1[1])}"
    message += f"vs {_wrap_user_id(cmd.side_2[0])}"
    if len(cmd.side_2) == 2:
        message += f" and {_wrap_user_id(cmd.side_2[1])}."

    message += f": {cmd.score_1}:{cmd.score_2}"

    if user_id in cmd.side_1 and cmd.score_1 > cmd.score_2:
        message += " Congrats! 😎"
    else:
        message += " Better luck next time ✊"

    return message

def _execute_gg_command(cmd: c.GoodGameCommand, ctx: RequestContext) -> t.List[ExecutionArtifact]:
    match_id = db.execute_gg_command(cmd)
    artifacts: t.List[ExecutionArtifact] = []

    for user_id in ctx.user_ids:
        if user_id == ctx.caller_id:
            continue
        artifacts.append(
            SendMessageArtifact(user_id, _build_gg_message(cmd, match_id, user_id))
        )
    
    return artifacts

def _execute_out_command(cmd: c.OutCommand, ctx: RequestContext) -> t.List[ExecutionArtifact]:
    player_ids = db.execute_out_command(cmd)
    
    artifacts: t.List[ExecutionArtifact] = []

    if not player_ids:
        artifacts.append(
            SendMessageArtifact(ctx.caller_id, "See ya around soon!")
        )
    else:
        for player_id in player_ids:
            artifacts.append(
                SendMessageArtifact(player_id, "Get ready, your match is coming! 🔥")
            )

    return artifacts
            

def execute_command(cmd: c.Command, ctx: RequestContext) -> t.List[ExecutionArtifact]:
    if isinstance(cmd, c.WannaPlayCommand):
        return _execute_wp_command(c, ctx)
    elif isinstance(cmd, c.GoodGameCommand):
        return _execute_gg_command(cmd, ctx)
    elif isinstance(cmd, c.OutCommand):
        return _execute_out_command(cmd, ctx)
    
    raise Exception("Unsupported command type")
