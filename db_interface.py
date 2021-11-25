import typing as t
import commands as c

def is_match_id_valid(match_id: int) -> bool:
    return True

def execute_wp_command(command: c.WannaPlayCommand) -> t.List[str]:
    """
    Return the list of ids for users who'll be playing.
    """