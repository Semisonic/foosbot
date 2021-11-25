import sqlite3
from sqlite3 import Error
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn
def create_league(conn, league):
    """
    Create a new league into the league table
    :param conn:
    :param league: (league_name)
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"insert into league (name) values ('{ league }')")
    conn.commit()
    return cur.lastrowid
def create_player(conn, player):
    """
    Create a new player into the player table
    :param conn:
    :param player: (player_name)
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"insert into player (name) values ('{ player }')")
    conn.commit()
    return cur.lastrowid
def create_waitlist(conn, waitlist):
    """
    Create a new match request into the waitlist table
    :param conn:
    :param match: (player_id, start_time, score_limit, format)
    :return:
    """
    sql = ''' INSERT INTO wait_list(player_id, start_time, format)
              VALUES(?,datetime('now'),?) '''
    cur = conn.cursor()
    cur.execute(sql, waitlist)
    conn.commit()
    return cur.lastrowid
def create_match(conn, match):
    """
    Create a new match into the match table
    :param conn:
    :param match: (winner_1, winner_2, loser_1, loser_2, winning_score, losing_score, league_id, created)
    :return:
    """
    sql = ''' INSERT INTO match(winner_1, winner_2, loser_1, loser_2, winning_score, losing_score, league_id, created)
              VALUES(?,?,?,?,?,?,?,datetime('now')) '''
    cur = conn.cursor()
    cur.execute(sql, match)
    conn.commit()
    # Code to send out slack messages here
    return cur.lastrowid
def player_name_to_id(conn, player_name):
    """
    Helper function that converts a player to their player_id
    : param player_name
    : return player_id
    """
    cur = conn.cursor()
    player_id = cur.execute(f"SELECT player_id FROM player where name = '{player_name}'")
    rows = cur.fetchall()
    if len(rows) ==0:
        create_player(conn, player_name)
    player_id = cur.execute(f"SELECT player_id FROM player where name = '{player_name}'")
    rows = cur.fetchall()
    player_id = rows[0][0]
    return player_id
def player_id_to_name(conn, player_id):
    """
    Helper function that converts a player_id to their name
    : param player_id
    : return player_name
    """
    cur = conn.cursor()
    player_id = cur.execute(f"SELECT name FROM player where player_id = {player_id}")
    rows = cur.fetchall()
    name = rows[0][0]
    return name
def league_name_to_id(conn, league_name):
    """
    Helper function that converts a league to their league_id
    : param league_name
    : return league_id
    """
    cur = conn.cursor()
    league_id = cur.execute(f"SELECT league_id FROM league where name = '{league_name}'")
    rows = cur.fetchall()
    if len(rows) ==0:
        create_league(conn, league_name)
    league_id = cur.execute(f"SELECT league_id FROM league where name = '{league_name}'")
    rows = cur.fetchall()
    league_id = rows[0][0]
    return league_id
def out(conn, player_name):
    """
    Delete from waitlist
    """
    player_id = player_name_to_id(conn, player_name)
    sql = f"DELETE FROM wait_list WHERE player_id='{ player_id }'"
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
def set_match(conn):
    """
    Return players where format and score_line matches my request, or is null (they don't mind) based on earliest person's preference
    Get the earliest row in waitlist
    Check their preferred formats
    Match rows based on that
    If 2/4 players available, return player names
    """
    sql = f"SELECT * FROM wait_list Order By start_time asc limit 1"
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    earliest_entry = rows[0]
    # 1v1, 2v2 or null
    type_of_game = earliest_entry[3]
    # 5, 10 or null
    score_count = earliest_entry[4]
    output = []
    if type_of_game == '1v1':
        players = cur.execute("SELECT * FROM wait_list where format != '2v2' order by start_time asc limit 2")
        rows = cur.fetchall()
        if len(rows) == 2:
            for row in rows:
                output += player_id_to_name(conn, row[0])
            return output
        else:
            players = cur.execute("SELECT * FROM wait_list where format != '1v1' order by start_time asc limit 4")
            rows = cur.fetchall()
            if len(rows) == 4:
                for row in rows:
                    output += player_id_to_name(conn, row[0])
                return output
            else:
                return []
    elif type_of_game == '2v2':
        players = cur.execute("SELECT * FROM wait_list where format != '1v1' order by start_time asc limit 4")
        rows = cur.fetchall()
        if len(rows) == 4:
            for row in rows:
                output += player_id_to_name(conn, row[0])
            return output
        else:
            players = cur.execute("SELECT * FROM wait_list where format != '2v2' order by start_time asc limit 2")
            rows = cur.fetchall()
            if len(rows) == 2:
                for row in rows:
                    output += player_id_to_name(conn, row[0])
                return output
    else:
        players = cur.execute("SELECT * FROM wait_list where format != '1v1' order by start_time asc limit 4")
        rows = cur.fetchall()
        if len(rows) == 4:
            for row in rows:
                output += player_id_to_name(conn, row[0])
            return output
        else:
            players = cur.execute("SELECT * FROM wait_list where format != '2v2' order by start_time asc limit 2")
            rows = cur.fetchall()
            if len(rows) == 2:
                for row in rows:
                    output += player_id_to_name(conn, row[0])
                return output
            else:
                return []

def WP(conn, match_request):
    """
    Create a spot on the waitlist for person who calls WP which stores their preferences
    : param match_request: [name, format]
    : return: "Successfuly in waitlist or some type of message
    """
    name = match_request[0]
    player_id = player_name_to_id(conn, name)
    create_waitlist(conn, (player_id, match_request[1]))
    return set_match(conn)
def update_match(conn, match):
    """
    Alter the match score
    : param match: (winner_1, winner_2, loser_1, loser_2, winning_score, losing_score, league_id, created, match_id)
    : return:
    """
    name = match_request[0]
    sql = ''' UPDATE match SET winner_1 = ? , winner_2 = ? , loser_1 = ?, loser_2 = ?, winning_score = ?, losing_score = ?, league_id= ? WHERE match_id = ?'''
    cur = conn.cursor()
    cur.execute(sql, match)
    conn.commit()
    return 'Successfuly updated score'

def GG(conn, result):
    """
    Create a record in the match table with the completed game result
    : param result: [winner_1, winner_2, loser_1, loser_2, winner_score, loser_score,league_name, match_id]
    : return: "Succesfully recorded score of:"
    """
    if result[4] != None:
        league_id = league_name_to_id(result[4])
    else:
        league_id = None
    if match_id:
        update_match(conn, (result[0], result[1], result[2], result[3], result[4], result[5], league_id, match_id))
    else:
        create_match(conn, (result[0], result[1], result[2], result[3], result[4], result[5], league_id))
    return set_match(conn)
