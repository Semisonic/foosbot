import typing as t

import db

def is_match_id_valid(match_id: int) -> bool:
    return True

def execute_wp_command(cmd) -> t.Set[str]:
    """
    Return the list of ids for users who'll be playing.
    """

    db.WP(db.db_conn, (cmd.owner, cmd.game_format))

def execute_gg_command(cmd) -> int:
    """
    Return the game id.
    """

    db.GG(db.db_conn, (cmd.side_1, cmd.side_2, cmd.score_1, cmd.score_2, None, cmd.match_id))
    
def execute_out_command(command: c.OutCommand) -> t.Set[str]:
    """
    Out the current player and do re-matching
    """
