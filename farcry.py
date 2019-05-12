#!/usr/bin/env python3
from datetime import datetime


def read_log_file(log_file_pathname):
    with open(log_file_pathname, 'r') as file:
        return file.read()


def parse_log_start_time(log_data):
        log_start_time = log_data.split("\n")[0]
        return datetime.strptime(log_start_time[15:], "%A, %B %d, %Y %H:%M:%S")


log_data = read_log_file("./logs/log00.txt")
print(parse_log_start_time(log_data).isoformat())

