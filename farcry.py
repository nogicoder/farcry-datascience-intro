#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from re import findall


def read_log_file(log_file_pathname):
	with open(log_file_pathname, 'r') as file:
		return file.read()


def parse_log_start_time(log_data):

	data_list = log_data.split("\n")
	raw_time = data_list[0][15:].strip()
	log_start_time = datetime.strptime(raw_time, "%A, %B %d, %Y %H:%M:%S")

	for line in data_list:
		if line.find("g_timezone") != -1:
			time_delta = int(line.split('(')[1][:-1].split(",")[1].strip())
			break

	timezone_info = timezone(timedelta(hours=time_delta))

	return log_start_time.replace(tzinfo=timezone_info)


def parse_session_mode_and_map(log_data):
	data_list = log_data.split("\n")
	for line in data_list:
		if line.find("Loading level") != -1:
			line_map = line.split(",")[0].split("/")[1].strip()
			line_mode = line.split(",")[1].split("-")[0].strip().split(" ")[1].strip()
			return (line_mode, line_map)


def parse_frags(log_data):

	data_list = log_data.split("\n")
	frags_list = []

	for line in data_list:

		if line.find("killed") != -1:
			# <26:32> <Lua> papazark killed lamonthe with AG36
			line_fragtime = line.split("<Lua>")[0].strip()[1:-1]
			line_killer_name = line.split("<Lua>")[1].split("killed")[0].strip()
			
			if line.split("<Lua>")[1].split("killed")[1].strip().find("itself") == -1:
				line_victim_name = line.split("<Lua>")[1].split(
					"killed")[1].strip().split("with")[0].strip()
				line_weapon_code = line.split("<Lua>")[1].split(
					"killed")[1].strip().split("with")[1].strip()
				frags_list.append((line_fragtime, line_killer_name, line_victim_name, line_weapon_code))
			else:
				frags_list.append((line_fragtime, line_killer_name))
	
	return frags_list
		

log_data = read_log_file("./logs/log00.txt")
print(parse_frags(log_data))

