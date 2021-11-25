import typing as t

class RequestContext:
    def __init__(self, caller_id: str, user_ids: t.List[str]) -> None:
        self.caller_id = caller_id
        self.user_ids = user_ids