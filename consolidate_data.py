import os
import csv
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


# Split the raw stream data into a list of dicts with the stream data in each one
def split_by_stream(raw_stream_data):
    # Pop the first field if the list length is odd
    if not len(raw_stream_data) % 2 == 0:
        raw_stream_data.pop(0)
    # for i, row in enumerate(raw_stream_data):



def store_in_stream_table(raw_stream_data):
    pass



def main():
    # For each game,
    games = [
        'ED',
        'PC'
    ]
    for game in games:
        # Get the paths of current CSVs
        csv_dir = os.path.join(os.getcwd(), 'data', game, 'csv')
        csv_files = os.listdir(csv_dir)
        # get all the data from the CSVs
        csv_data = []
        for csv_file in csv_files:
            data = read_csv(os.path.join(csv_dir, csv_file))
            csv_data.extend(data)
        # get only the streamer names from the csv data
        streamer_names = [row[0] for row in csv_data]
        # remove duplicates by converting it to a set and then back to a list
        streamer_names = list(set(streamer_names))
        # for each UNIQUE streamer name, store the raw CSV data into the next respective stream table
        for streamer in streamer_names:
            # get the data for just that streamer
            streamer_data = [row for row in csv_data if row[0] == streamer]



if __name__ == '__main__':
    main()
