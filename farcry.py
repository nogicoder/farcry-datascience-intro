#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta
from datetime import timezone


def read_log_file(log_file_pathname):
	with open(log_file_pathname, 'r') as file:
		return file.read()


def parse_log_start_time(log_data):

	data_list = log_data.split("\n")
	raw_time = data_list[0][15:].strip()
	log_start_time = datetime.strptime(raw_time, "%A, %B %d, %Y %H:%M:%S")

	for item in data_list:
		if item.find("g_timezone") != -1:
			time_delta = int(item.split('(')[1][:-1].split(",")[1].strip())
			break

	timezone_info = timezone(timedelta(hours=time_delta))

	return log_start_time.replace(tzinfo=timezone_info)


def parse_session_mode_and_map(log_data):
	data_list = log_data.split("\n")
	for item in data_list:
		if item.find("Loading level") != -1:
			data_map = item.split(",")[0].split("/")[1].strip()
			data_mode = item.split(",")[1].split("-")[0].strip().split(" ")[1].strip()
			return (data_mode, data_map)
		

log_data = read_log_file("./logs/log00.txt")
print(parse_session_mode_and_map(log_data))

