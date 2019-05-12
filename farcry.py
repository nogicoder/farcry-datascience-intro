#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta
from datetime import timezone

# Waypoint 1: Read the data
def read_log_file(log_file_pathname):
	"""Read the data from the log file
	@param log_file_pathname: The path to the log file
	"""
	with open(log_file_pathname, 'r') as file:
		return file.read()


# Waypoint 2: Get the log starting time
def parse_log_start_time(log_data):
	"""Get the start time of the session from the log data
	@param log_data: The data from the log file
	"""
	data_list = log_data.split("\n")
	raw_time = data_list[0][15:].strip()
	log_start_time = datetime.strptime(raw_time, "%A, %B %d, %Y %H:%M:%S")

	for line in data_list:
		if line.find("g_timezone") != -1:
			time_delta = int(line.split('(')[1][:-1].split(",")[1].strip())
			break

	timezone_info = timezone(timedelta(hours=time_delta))

	return log_start_time.replace(tzinfo=timezone_info)


# Waypoint 3: Get the Mode and Map of the session  
def parse_session_mode_and_map(log_data):
	"""Get the mode and map from the log data
	@param log_data: The data from the log file
	"""
	data_list = log_data.split("\n")
	for line in data_list:
		if line.find("Loading level") != -1:
			line_map = line.split(",")[0].split("/")[1].strip()
			line_mode = line.split(",")[1].split("-")[0].strip().split(" ")[1].strip()
			return (line_mode, line_map)


# Waypoint 4: Get the frags list
def handle_frag_time(i, line, data_list, line_fragtime):
	"""Handle the frag time separately for the hour case: If 
	the minute of a line is smaller than its previous line, increase
	the hour by 1
	@param i: The line index
	@param line: The line itself in string
	@data_list: The data in list
	@line_fragtime: Initial log starting time
	"""

	frag_minute = int(line.split("<Lua>")[0].strip()[
		1:-1].split(":")[0].strip())
	frag_second = int(line.split("<Lua>")[0].strip()[
					1:-1].split(":")[1].strip())

	# Get the minute from the previous line
	if data_list[i-1].find("killed") != -1:
		prevLine_minute = int(data_list[i-1].split("<Lua>")[0].strip()[
							1:-1].split(":")[0].strip())
	else:
		prevLine_minute = 0

	# If the current minute is smaller than last line, increase hour by 1
	if frag_minute < prevLine_minute:
		line_fragtime += timedelta(hours=1)

	# Update the time
	line_fragtime = line_fragtime.replace(
		minute=frag_minute, second=frag_second)
	
	return line_fragtime


def parse_frags(log_data):
	"""Get the frags list from the log data
	@param log_data: The data from the log file
	"""
	frags_list = []
	data_list = log_data.split("\n")
	line_fragtime = parse_log_start_time(log_data)

	# Scan through each line in the data
	for i, line in enumerate(data_list):

		# If the letter "killed" is in the line
		if line.find("killed") != -1:

			# <26:32> <Lua> papazark killed lamonthe with AG36
			line_fragtime = handle_frag_time(i, line, data_list, line_fragtime)

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


log_data = read_log_file("./logs/log02.txt")
print(parse_frags(log_data))

