#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from csv import writer
from sqlite3 import connect


# Waypoint 1: Read the data
def read_log_file(log_file_pathname):
	"""
	Read the data from the log file.
	Returning the content of the log file.
	@param log_file_pathname: The path to the log file
	"""
	with open(log_file_pathname, 'r') as file:
		return file.read()


# Waypoint 2, 3: Get the log starting time and timezone
def parse_log_start_time(log_data):
	"""
	Get the start time and timezone of the session from the log data
	Returning a datetime.datetime object of the starting log time.
	@param log_data: The data from the log file
	"""
	data_list = log_data.split("\n")
	raw_time = data_list[0][15:].strip()
	log_start_time = datetime.strptime(raw_time, "%A, %B %d, %Y %H:%M:%S")

	for line in data_list:
		if line.find("g_timezone") != -1:
			hour_delta = int(line.split('(')[1][:-1].split(",")[1].strip())
			break

	timezone_info = timezone(timedelta(hours=hour_delta))

	return log_start_time.replace(tzinfo=timezone_info)


# Waypoint 4: Get the Mode and Map of the session  
def parse_session_mode_and_map(log_data):
	"""
	Get the mode and map from the log data.
	Returning a tuple of mode and map of the session.
	@param log_data: The data from the log file
	"""
	data_list = log_data.split("\n")
	for line in data_list:
		if line.find("Loading level") != -1:
			line_map = line.split(",")[0].split("/")[1].strip()
			line_mode = line.split(",")[1].split("-")[0].strip().split(" ")[1].strip()
			return (line_mode, line_map)


# Waypoint 5, 6: Get the frags list and modify the frag time format
def handle_frag_time(i, line, data_list, line_fragtime, prevLine_minute):
	"""
	Handle the frag time separately for the hour case: If 
	the minute of a line is smaller than its previous line, increase
	the hour by 1.
	Returning the time of a frag as a datetime.datetime object.
	@param i: The line index
	@param line: The line itself in string
	@data_list: The data in list
	@line_fragtime: Initial log starting time
	@prevLine_minute: The minute from the previous killing event
	"""
	frag_minute = int(line[1:3])
	frag_second = int(line[4:6])

	# If the current minute is smaller than last line, increase hour by 1
	if frag_minute < prevLine_minute:
		line_fragtime += timedelta(hours=1)

	# Update the time
	line_fragtime = line_fragtime.replace(
		minute=frag_minute, second=frag_second)
	
	return line_fragtime


def parse_frags(log_data):
	"""
	Get the frags list from the log data.
	Returning a list of frags.
	@param log_data: The data from the log file
	"""
	frags_list = []
	data_list = log_data.split("\n")
	line_fragtime = parse_log_start_time(log_data)

	# Scan through each line in the data
	for i, line in enumerate(data_list):

		# Set the initial min to 0, the prevLine_minute var is to indicate the minute of the previous killing event
		prevLine_minute = line_fragtime.minute

		# If the letter "killed" is in the line
		if line.find("killed") != -1:
			
			line_fragtime = handle_frag_time(i, line, data_list, line_fragtime, prevLine_minute)

			line_killer_name = line.split("<Lua>")[1].split("killed")[0].strip()
			
			# If the player did not kill itself (no "itself" in the line)
			if line.split("<Lua>")[1].split("killed")[1].strip().find("itself") == -1:
				line_victim_name = line.split("<Lua>")[1].split(
					"killed")[1].strip().split("with")[0].strip()
				line_weapon_code = line.split("<Lua>")[1].split(
					"killed")[1].strip().split("with")[1].strip()
				frags_list.append((line_fragtime, line_killer_name, line_victim_name, line_weapon_code))
			else:
				frags_list.append((line_fragtime, line_killer_name))
	
	return frags_list


# Waypoint 7: Make the fraglist looks prettier with emojis
def weapon_code_converter(weapon):
	"""A separate function to handle the emojis go 
	with each weapon category.
	Returning an emoji that suits the weapon code.
	@param weapon: The weapon code in the frag line
	"""
	weapon_dict = {
		"🚙": "Vehicle",
		"🔫": "Falcon, Shotgun, P90, MP5, M4,AG36, OICW, SniperRifle, M249, VehicleMountedAutoMG, VehicleMountedMG",
		"💣": "HandGrenade, AG36Grenade, OICWGrenade, StickyExplosive",
		"🚀": "Rocket, VehicleMountedRocketMG, VehicleRocket",
		"🔪": "Machete",
		"🚤": "Boat"
	}

	for key, value in weapon_dict.items():
		if weapon in value:
			return key


def prettify_frags(frags):
	"""
	Make the frags list looks prettier with the use of emojis.
	Return a new list of frags with emojis.
	@param frags: A list of frags tuples parsed from the log data
	"""
	new_frags = []
	for frag in frags:

		# If the player did not kill itself
		if len(frag) > 2:
			frag_time = frag[0].isoformat()
			killer_name = "😛  " + frag[1]
			victim_name = "😦  " + frag[2]
			weapon_icon = weapon_code_converter(frag[3])

			frag_line = "[{}] {} {}  {}".format(
				frag_time, killer_name, weapon_icon, victim_name)
		else:
			frag_time = frag[0].isoformat()
			killer_name = "😦  " + frag[1] + " ☠"

			frag_line = "[{}] {}".format(frag_time, killer_name)

		new_frags.append(frag_line)

	return new_frags 


# Waypoint 8: Get the session start and end time from the log file
def get_index_of_line(log_data, line_input):
	"""Get the position of a line in the data log.
	Returning the index of a line in the log_data.
	@param log_data: The data from log file
	@param line_input: A string contained in a line
	"""
	data_list = log_data.split("\n")
	for line in data_list:
		if line_input in line:
			return log_data.index(line)

			
def parse_game_session_start_and_end_times(log_data, frags):
	"""
	Get the start and end time from the log data.
	This function will return a tuple of start and end time.
	@param log_data: The data from log file
	@frags: Frag list is passed in to get the ending frag
	"""
	data_list = log_data.split("\n")
	log_start_time = parse_log_start_time(log_data)
	start_time = 0
	ending_frag = frags[-1]
	ending_frag_index = get_index_of_line(log_data, ending_frag[0].strftime("%M:%S"))
	
	for line in data_list:
		
		# Find the line with "Precaching level" signaling the session start time
		if line.find("Precaching level") != -1 and not start_time:
			raw_start_time = line.split("Precaching level")[0].strip("#< >").split(":")
			start_time_min = int(raw_start_time[0])
			start_time_sec = int(raw_start_time[1])
			start_time = log_start_time.replace(
				minute=start_time_min, second=start_time_sec)

			# If the minute is smaller than the log starting minute -> increase 1 hour
			if start_time_min < log_start_time.minute:
				start_time += timedelta(hours=1)
		
		# Find the line with a timestamp right after the last frag ending event
		if "<" in line:
			line_index = get_index_of_line(log_data, line)

			if line_index > ending_frag_index:
				line_minute = int(line[1:3])
				line_second = int(line[4:6])
				end_time = ending_frag[0].replace(minute=line_minute, second=line_second)

				# If the minute is smaller than the ending frag's minute -> increase 1 hour
				if line_minute < ending_frag[0].minute:
					end_time += timedelta(hours=1)
				
				return (start_time, end_time)


# Waypoint 9: Create frag CSV file
def write_frag_csv_file(log_file_pathname, frags):
	"""Create a new CSV file and write each frag to each row
	@param log_file_pathname: The path to the CSV file
	@param frags: The list of frag
	"""
	with open(log_file_pathname, "w+") as file:
		log_writer = writer(file, delimiter=",")
		for frag in frags:
			if len(frag) > 2:
				log_writer.writerow([frag[0], frag[1], frag[2], frag[3]])
			else:
				log_writer.writerow([frag[0], frag[1]])


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
			current_row.execute("INSERT INTO match_frag(match_id, frag_time, killer_name, victim_name, weapon_code) VALUES (?,?,?,?,?)",
								(match_id, frag[0], frag[1], frag[2], frag[3]))
		else:
			current_row.execute("INSERT INTO match_frag(match_id, frag_time, killer_name) VALUES (?,?,?)",
                            (match_id, frag[0], frag[1]))


# Waypoint 25: Insert match data to database
def insert_match_to_sqlite(file_pathname, start_time, end_time, game_mode, map_name, frags):
	"""
	Insert the match data to the database. This function return the id of the match
	@param file_pathname: Path and name of the database
	@param start_time: A datetime.datetime object indicates the start of the game session
	@param end_time: A datetime.datetime object indicates the end of the game session
	@param game_mode: The mode of the game session
	@param map_name: The name of the map that was played
	@param frags: The list of frag
	"""
	connection = connect(file_pathname)
	current_row = connection.cursor()
	current_row.execute("INSERT INTO match(start_time, end_time, game_mode, map_name) VALUES (?,?,?,?)", (start_time, end_time, game_mode, map_name))
	insert_frags_to_sqlite(connection, current_row.lastrowid, frags)
	connection.commit()
	connection.close()
	return current_row.lastrowid


log_data = read_log_file("./logs/log04.txt")
frags = parse_frags(log_data)
start_time, end_time = parse_game_session_start_and_end_times(log_data, frags)
game_mode, map_name = parse_session_mode_and_map(log_data)
print(insert_match_to_sqlite("./farcry.db", start_time, end_time, game_mode, map_name, frags))
