import typing as t

class RequestContext:
    def __init__(self, caller_id: str) -> None:
        self.caller_id = caller_id