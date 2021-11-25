import typing as t
import commands as c

class ExecutionArtifact:
    pass

class ReplyArtifact(ExecutionArtifact):
    def __init__(self, message: str) -> None:
        super().__init__()

        self.message = message

class SendMessageArtifact(ExecutionArtifact):
    def __init__(self, user_id: str, message: str) -> None:
        super().__init__()

        self.user_id = user_id
        self.message = message

def execute_command(cmd: c.Command) -> t.List[ExecutionArtifact]:
    pass
