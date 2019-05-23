#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from re import findall, search, match
from csv import writer
from sqlite3 import connect as sqliteconnect, Error as sqliteError
from psycopg2 import connect as postgreconnect, Error as postgreError


"""EMOJI CONSTANTS"""
CAR = "🚙"
GRENADE = "💣"
GUN = "🔫"
ROCKET = "🚀"
KNIFE = "🔪"
BOAT = "🚤"
SMILEYFACE = "😛"
SADFACE = "😦"
SKULL = "☠"

"""WEAPON CODE TO EMOJI DICTIONARY"""
WEAPON_DICT = {
    "Vehicle": CAR,
    "Falcon": GUN,
    "Shotgun": GUN,
    "P90": GUN,
    "MP5": GUN,
    "M4": GUN,
    "AG36": GUN,
    "OICW": GUN,
    "SniperRifle": GUN,
    "M249": GUN,
    "VehicleMountedAutoMG": GUN,
    "VehicleMountedMG": GUN,
    "HandGrenade": GRENADE,
    "AG36Grenade": GRENADE,
    "OICWGrenade": GRENADE,
    "StickyExplosive": GRENADE,
    "Rocket": ROCKET,
    "VehicleMountedRocketMG": ROCKET,
    "VehicleRocket": ROCKET,
    "Machete": KNIFE,
    "Boat": BOAT
}


# Waypoint 1: Read the data
def read_log_file(log_file_pathname):
    """
    Read the data from the log file.
    Returning the content of the log file.
    @param log_file_pathname: The path to the log file
    """
    try:
        with open(log_file_pathname, 'r') as file:
            return file.read()
    except Exception:
        print("Please check the file permission or format!")


# Waypoint 2, 3: Get the log starting time and timezone
def parse_log_start_time(log_data):
    """
    Get the start time and timezone of the session from the log data
    Returning a datetime.datetime object of the starting log time.
    @param log_data: The data from the log file
    """
    try:
        # Get the log starting time
        time_match = search(
            r"Log Started at (\w+, \w+ \d{2}, \d{4} \d{2}:\d{2}:\d{2})",
            log_data)
        log_start_time = datetime.strptime(
            time_match.group(1), "%A, %B %d, %Y %H:%M:%S")

        # Get the timezone of the log
        timezone_match = search(
            r"<\d{2}:\d{2}> \w+ \w+: [(]g_timezone,([^)]*)[)]", log_data)
        timezone_info = timezone(timedelta(hours=int(timezone_match.group(1))))

        return log_start_time.replace(tzinfo=timezone_info)
    except Exception:
        print("Something is wrong with the log file!")


# Waypoint 4: Get the Mode and Map of the session
def parse_session_mode_and_map(log_data):
    """
    Get the mode and map from the log data.
    Returning a tuple of mode and map of the session.
    @param log_data: The data from the log file
    """
    try:
        match = search(
            r"<\d{2}:\d{2}> [^d]* Loading level \w+\/(\w+), \w+ (\w+)",
            log_data)
        line_map, line_mode = match.groups()
        return (line_mode, line_map)
    except Exception:
        print("Something is wrong with the log file!")


# Waypoint 5, 6: Get the frags list and modify the frag time format
def parse_frags(log_data):
    """
    Get the frags list from the log data.
    Returning a list of frags.
    @param log_data: The data from the log file
    """
    try:
        frags = []
        frag_time = parse_log_start_time(log_data)
        matches = findall(
            r"<(\d{2}):(\d{2})> <\w+> ([a-zA-Z0-9_ ]*)" +
            r" killed (?:itself|([a-zA-Z0-9_ ]*) with (\w+))",
            log_data)

        for i, frag in enumerate(matches):

            frag_min = int(frag[0])
            frag_sec = int(frag[1])
            if (i == 0 and frag_min < frag_time.minute
                    or i > 0 and frag_min < int(matches[i-1][0])):
                frag_time += timedelta(hours=1)

            frag_time = frag_time.replace(minute=frag_min, second=frag_sec)

            if frag[3] == "":
                frags.append((frag_time, frag[2]))
            else:
                frags.append((frag_time, frag[2], frag[3], frag[4]))

        return frags
    except Exception:
        print("Something is wrong with the log file!")


# Waypoint 7: Make the fraglist looks prettier with emojis
def prettify_frags(frags):
    """
    Make the frags list looks prettier with the use of emojis.
    Return a new list of frags with emojis.
    @param frags: A list of frags tuples parsed from the log data
    """
    try:
        prettier_frags = []
        for frag in frags:

            # If the player did not kill itself
            if len(frag) > 2:
                frag_line = "[{time}] {killer} {weapon} {victim}".format(
                    time=frag[0].isoformat(),
                    killer=SMILEYFACE + " " + frag[1],
                    weapon=WEAPON_DICT.get(frag[3]),
                    victim=SADFACE + " " + frag[2])

            else:
                frag_line = "[{}] ".format(frag[0].isoformat()) + \
                            SADFACE + " " + frag[1] + " " + SKULL

            prettier_frags.append(frag_line)

        return prettier_frags
    except Exception:
        print("Something is wrong with the log file!")


# Waypoint 8: Get the session start and end time from the log file
def parse_game_session_start_and_end_times(log_data, frags):
    """
    Get the start and end time from the log data.
    This function will return a tuple of start and end time.
    @param log_data: The data from log file
    @frags: Frag list is passed in to get the ending frag
    """
    try:
        log_start_time = parse_log_start_time(log_data)

        # Get the match starting time
        start_match = search(
            r"<(\d{2}):(\d{2})> [^d]* Loading level \w+\/\w+, \w+ \w+",
            log_data)
        start_time = log_start_time.replace(
            minute=int(start_match.group(1)), second=int(start_match.group(2)))

        # If the minute is smaller than the starting log's minute
        # -> increase 1 hour
        if start_time.minute < log_start_time.minute:
            start_time += timedelta(hours=1)

        # Get the match ending time
        # If frags is not empty
        if frags:
            last_frag = frags[-1]
            last_frag_time = last_frag[0].strftime("%M:%S")
            end_match = findall(
                "<{}> ".format(last_frag_time) +
                r"<\w+> [a-zA-Z0-9_ ]* killed " +
                r"(?:itself|[a-zA-Z0-9_ ]* with \w+)",
                log_data)

            # Get the index of the beginning of the line
            # after the last frag in log data
            i = log_data.index(end_match[-1]) + len(end_match[-1]) + 1
            end_time = last_frag[0].replace(
                minute=int(log_data[i+1:i+3]), second=int(log_data[i+4:i+6]))

            # If the minute is smaller than the ending frag's minute
            # -> increase 1 hour
            if end_time.minute < last_frag[0].minute:
                end_time += timedelta(hours=1)
        else:
            end_match = findall(r"<(\d+):(\d+)>", log_data)
            end_time = start_time.replace(
                minute=int(end_match[-1][0]), second=int(end_match[-1][1]))

            if end_time.minute < start_time.minute:
                end_time += timedelta(hours=1)

        return (start_time.isoformat(), end_time.isoformat())

    except Exception:
        print("Something is wrong with the log file!")


# Waypoint 9: Create frag CSV file
def write_frag_csv_file(log_file_pathname, frags):
    """Create a new CSV file and write each frag to each row
    @param log_file_pathname: The path to the CSV file
    @param frags: The list of frag
    """
    try:
        with open(log_file_pathname, "w+") as file:
            log_writer = writer(file, delimiter=",")
            for frag in frags:
                if len(frag) > 2:
                    log_writer.writerow([frag[0], frag[1], frag[2], frag[3]])
                else:
                    log_writer.writerow([frag[0], frag[1]])
    except Exception:
        print("Failed to write to csv. Please try again!")


# Waypoint 26: Insert frag data to database
def insert_frags_to_sqlite(connection, match_id, frags):
    """
    This function insert frag data to the data base and is
    integrated into the insert_match_to_sqlite function.
    @param connection: A connection object
    @param match_id: The id of the match
    @param frags: The list of frags
    """
    current_row = connection.cursor()
    for frag in frags:
        if len(frag) > 2:
            current_row.execute("INSERT INTO match_frag(match_id, " +
                                "frag_time, killer_name, victim_name," +
                                " weapon_code) VALUES (?,?,?,?,?)",
                                (match_id, frag[0], frag[1], frag[2], frag[3]))
        else:
            current_row.execute("INSERT INTO match_frag(match_id, " +
                                "frag_time, killer_name) VALUES (?,?,?)",
                                (match_id, frag[0], frag[1]))


def get_sqlitedb_connection(file_pathname):
    """
    Establish connection to SQLite database.
    Return a connection object.
    @param file_pathname: The path to database file
    """
    try:
        return sqliteconnect(file_pathname)
    except sqliteError as error:
        print("Error while connecting to SQLite Database", error)


# Waypoint 25: Insert match data to database
def insert_match_to_sqlite(file_pathname, start_time, end_time,
                           game_mode, map_name, frags):
    """
    Insert the match data to the database. This function
    return the id of the match.
    @param file_pathname: Path and name of the database
    @param start_time: A datetime.datetime object indicates the start
    of the game session.
    @param end_time: A datetime.datetime object indicates the end of
    the game session.
    @param game_mode: The mode of the game session
    @param map_name: The name of the map that was played
    @param frags: The list of frag
    """
    try:
        connection = get_sqlitedb_connection(file_pathname)
        current_row = connection.cursor()
        current_row.execute("INSERT INTO match(start_time, end_time, " +
                            "game_mode, map_name) VALUES (?,?,?,?)",
                            (start_time, end_time, game_mode, map_name))
        insert_frags_to_sqlite(connection, current_row.lastrowid, frags)
    except (Exception, sqliteError) as error:
        print("Error while connecting to SQLite Database", error)

    finally:
        if not connection:
            return
        connection.commit()
        connection.close()
        print("Connection to SQLite is closed")
        return current_row.lastrowid


def get_postgredb_connection(properties):
    """
    Establish connection to PostgreSQL database.
    Return a connection object.
    @param properties: The config properties
    to connect to the database
    """
    try:
        return postgreconnect(host=properties[0],
                              database=properties[1],
                              user=properties[2],
                              password=properties[3])
    except postgreError as error:
        print("Error while connecting to PostgreSQL Database", error)


# Waypoint 48: Insert Game Data to PostgreSQL Database
def insert_match_to_postgresql(properties, start_time, end_time,
                               game_mode, map_name, frags):
    """
    Insert the data from game session to the database using psycopg.
    Returning the ID of the match being inserted.
    @param properties: A tuple containing (hostname,
    database_name, username, password).
    @param start_time: A datetime.datetime object indicates the game start time
    @param end_time: A datetime.datetime object indicates the game end time
    @param game_mode: The mode game, can be ASSULT, TDM or FFA
    @param map_name: Name of the map
    @param frags: A tuple contain information about the frags
    """
    try:
        connection = get_postgredb_connection(properties)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO match (start_time, end_time," +
                       " game_mode, map_name) VALUES (%s, %s, %s, %s)" +
                       " RETURNING match_id",
                       (start_time, end_time, game_mode, map_name))
        match_id = cursor.fetchone()[0]
        for frag in frags:
            if len(frag) > 2:
                cursor.execute("INSERT INTO match_frag (match_id, " +
                               "frag_time, killer_name, victim_name, " +
                               "weapon_code) VALUES (%s, %s, %s, %s, %s)",
                               (match_id, frag[0], frag[1], frag[2], frag[3]))
            else:
                cursor.execute("INSERT INTO match_frag (match_id, " +
                               "frag_time, killer_name) VALUES (%s, %s, %s)",
                               (match_id, frag[0], frag[1]))

    except (Exception, postgreError) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
        if not connection:
            return
        connection.commit()
        cursor.close()
        connection.close()
        print("Connection to PostgreSQL is closed")
        return match_id


# Waypoint 53: Determine Serial Killers
def find_winning_streak(player_name, frags):
    """
    Find the longest streak a player is alive during the session.
    Returning a list of frags of the current player.
    @param player_name: The current player being assessed
    @param frags: List of frags
    """
    longest_streak = []
    current_streak = []
    for frag in frags:
        if len(frag) > 2 and frag[1] == player_name:
            current_streak.append((frag[0], frag[2], frag[3]))
        elif ((len(frag) == 2 and frag[1] == player_name) or
                len(frag) > 2 and frag[2] == player_name):
            if len(current_streak) > len(longest_streak):
                longest_streak = current_streak
            current_streak = []
    return longest_streak


def calculate_serial_killers(frags):
    """
    Main function used to find the longest winning streaks
    of all players in a session.
    Returning a dictionary of the winning streaks of players.
    @param frags: List of frags
    """
    killers = {}
    for frag in frags:
        if frag[1] in killers.keys():
            continue
        player_name = frag[1]
        killers[player_name] = find_winning_streak(player_name, frags)

    return killers


# Waypoint 54: Determine Serial Losers
def find_losing_streak(player_name, frags):
    """
    Find the longest streak a player is being a victim during the session.
    Returning a list of frags of the current player.
    @param player_name: The current player being assessed
    @param frags: List of frags
    """
    longest_streak = []
    current_streak = []
    for frag in frags:
        if len(frag) > 2 and frag[2] == player_name:
            current_streak.append((frag[0], frag[1], frag[3]))
        elif len(frag) == 2 and frag[1] == player_name:
            current_streak.append((frag[0], None, None))
        elif len(frag) > 2 and frag[1] == player_name:
            if len(current_streak) > len(longest_streak):
                longest_streak = current_streak

            current_streak = []

    return longest_streak


def calculate_serial_losers(frags):
    """
    Main function used to find the longest losing
    streaks of all players in a session.
    Returning a dictionary of the losing streaks of players.

    @param frags: List of frags
    """
    losers = {}
    for frag in frags:
        if len(frag) > 2 and frag[2] not in losers.keys():
            player_name = frag[2]
            losers[player_name] = find_losing_streak(player_name, frags)
        elif len(frag) == 2 and frag[1] not in losers.keys():
            player_name = frag[1]
            losers[player_name] = find_losing_streak(player_name, frags)

    return losers
