def read_log_file(log_file_pathname):
    with open(log_file_pathname, 'r') as file:
        return file.read()


log_data = read_log_file("./logs/log00.txt")
print(len(log_data))

