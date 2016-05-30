import os
import csv
import time
import datetime
from shutil import copy2 as copy_file
from pprint import pprint
from neopysqlite.neopysqlite import Pysqlite


class StreamerDB:
    def __init__(self, game, streamer_name, data):
        self.path = os.path.join(os.getcwd(), 'data', game, 'streamers', '{}.db'.format(streamer_name))
        self.game = game
        self.streamer_name = streamer_name
        self.stream_data = data
        if self.db_exists():
            self.db = Pysqlite('{} {} Stream Database'.format(game, streamer_name), self.path, verbose=True)
        else:
            self.create_db()
            self.db = Pysqlite('{} {} Stream Database'.format(game, streamer_name), self.path, verbose=True)

    def db_exists(self):
        return os.path.isfile(self.path)

    def create_db(self):
        if not self.db_exists():
            print('Database for {} does not exist. Creating DB now.'.format(self.streamer_name))
            copy_file(
                src=os.path.join(os.getcwd(), 'data', self.game, 'streamers', 'base', 'test_streamer.db'),
                dst=self.path
            )
        else:
            print('Database for {} already exists'.format(self.streamer_name))

    def create_stream_table(self):
        create_statement = 'CREATE TABLE "stream_" (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,' \
                           '`timestamp`	TEXT NOT NULL, `viewers` INTEGER NOT NULL, `followers` INTEGER NOT NULL, ' \
                           '`partnership`INTEGER NOT NULL DEFAULT 0)'


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
            # print('New stream detected, storing old one')
            print('[{}] Streamer {} held stream of duration {} seconds has {} rows and started at {}'.format(
                    len(stream_data),
                    raw_data[0][0],
                    calculate_time_delta(raw_data[0][4], raw_data[-1][4]).seconds,
                    len(raw_data),
                    raw_data[0][4]))
            data = {
                'id': len(stream_data),  # assign it an ID according to how many streams have been found
                'raw_data': raw_data,  # the list of raw CSV rows
                'duration': calculate_time_delta(raw_data[0][4], raw_data[-1][4]).seconds,
                'start_timestamp': raw_data[0][4]
            }
            # add the dict to the list
            stream_data.append(data)
            # reset the raw data
            raw_data = []
            # reset the duration
            continue  # continue to the next field to find the next stream
    return stream_data


def store_in_stream_table(game, streamer, streams_data):
    s_db = StreamerDB(game=game, streamer_name=streamer, data=streams_data)


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
            store_in_stream_table(game=game, streamer=streamer, streams_data=streams_data)
            break  # temporary break


if __name__ == '__main__':
    main()
