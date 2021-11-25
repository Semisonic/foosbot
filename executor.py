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

def _build_gg_message(cmd: c.GoodGameCommand, match_id: int, user_id: str) -> str:
    message = f"Good game! Game ${match_id}: ";
    message += cmd.

def _execute_gg_command(cmd: c.GoodGameCommand, ctx: RequestContext) -> t.List[ExecutionArtifact]:
    match_id = db.execute_gg_command(cmd)
    artifacts: t.List[ExecutionArtifact] = []

    for user_id in ctx.user_ids:
        if user_id == ctx.caller_id:
            continue
        artifacts.append(
            SendMessageArtifact(user_id, "Good game! ")
        )
            

def execute_command(cmd: c.Command, ctx: RequestContext) -> t.List[ExecutionArtifact]:
    pass
