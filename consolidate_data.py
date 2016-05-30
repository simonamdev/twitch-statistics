import os
import csv
import time
import datetime
from pprint import pprint
from neopysqlite.neopysqlite import Pysqlite

# CSV SCHEMA:
# NAME, VIEWERS, FOLLOWERS, PARTNERSHIP, TIMESTAMP


def read_csv(file_path):
    data = []
    with open(file_path, newline='') as csvfile:
        csvreader = csv.reader(csvfile, quotechar='"')
        for row in csvreader:
            data.append(row)
    return data


def convert_timestamp_to_datetime(timestamp):
    # timestamp format: '2016-01-25 10:46:18'
    split_string = timestamp.split(' ')
    date_part = split_string[0].split('-')
    time_part = split_string[1].split(':')
    year, month, day = int(date_part[0]), int(date_part[1]), int(date_part[2])
    hour, minute, second = int(time_part[0]), int(time_part[1]), int(time_part[2])
    return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)


def calculate_time_delta(timestamp_one, timestamp_two):
    time_delta = convert_timestamp_to_datetime(timestamp_two) - convert_timestamp_to_datetime(timestamp_one)
    # pprint(time_delta)
    return time_delta


# Split the raw stream data into a list of dicts with the stream data in each one
def split_by_stream(raw_stream_data):
    # Pop the first field if the list length is odd
    if not len(raw_stream_data) % 2 == 0:
        raw_stream_data.pop(0)
    print('Raw stream rows: {}'.format(len(raw_stream_data)))
    # the list to store the dictionaries in
    stream_data = []
    # a list to store the raw csv data in for that particular stream
    raw_data = []
    # a rolling number to store the duration in seconds of the stream
    current_duration = 0
    for i, row in enumerate(raw_stream_data):
        raw_data.append(row)
        time_field = row[4]
        if i+1 == len(raw_stream_data):  # avoid out of index exception
            print('End of CSV data found')
            break
        # get the next time field in the list
        next_time_field = raw_stream_data[i+1][4]
        # if the difference between the next time and the current time is greater than one hour,
        # then we will assume that it is a new stream
        time_delta = calculate_time_delta(time_field, next_time_field)
        if time_delta.seconds / (60 * 60) > 1:
            print('New stream detected, storing old one')
            print('[{}] Streamer {} held stream of duration {} seconds has {} rows and started at {}'.format(
                    len(stream_data),
                    raw_data[0][0],
                    current_duration,
                    len(raw_data),
                    raw_data[0][4]))
            data = {
                'id': len(stream_data),  # assign it an ID according to how many streams have been found
                'raw_data': raw_data,  # the list of raw CSV rows
                'duration': current_duration,
                'start_timestamp': raw_data[0][4]
            }

            # add the dict to the list
            stream_data.append(data)
            # reset the raw data
            raw_data = []
            # reset the duration
            current_duration = 0
            continue  # continue to the next field to find the next stream
        else:
            # otherwise, if we're still in the same stream, store the delta to the duration
            # print(current_duration)
            current_duration += time_delta.seconds


def store_in_stream_table(raw_stream_data):
    pass


def main():
    start_time = time.time()
    print('Starting consolidation script at {}'.format(datetime.datetime.fromtimestamp(start_time)))
    # For each game,
    games = [
        # 'ED',
        'PC'
    ]
    for game in games:
        print('Consolidation data for: {}'.format(game))
        # Get the paths of current CSVs
        csv_dir = os.path.join(os.getcwd(), 'data', game, 'csv')
        csv_files = os.listdir(csv_dir)
        # get all the data from the CSVs
        csv_data = []
        for csv_file in csv_files:
            print('Opening file: {}'.format(csv_file))
            data = read_csv(os.path.join(csv_dir, csv_file))
            csv_data.extend(data)
        # get only the streamer names from the csv data
        streamer_names = [row[0] for row in csv_data]
        # remove duplicates by converting it to a set and then back to a list
        streamer_names = list(set(streamer_names))
        # for each UNIQUE streamer name, store the raw CSV data into the next respective stream table
        for streamer in streamer_names:
            # temporary skip through to find a streamer with a good set of data to test
            if not streamer == 'fireytoad':
                continue
            print('Processing data for: {}'.format(streamer))
            # get the data for just that streamer
            streamer_data = [row for row in csv_data if row[0] == streamer]
            streams_data = split_by_stream(streamer_data)
            break  # temporary break


if __name__ == '__main__':
    main()
