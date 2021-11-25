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
                SendMessageArtifact(player_id, "Get ready, ")
            )
            

def execute_command(cmd: c.Command, ctx: RequestContext) -> t.List[ExecutionArtifact]:
    pass
