import os
import csv
import time
from tqdm import tqdm


def read_csv(file_path):
    data = []
    with open(file_path, mode='r', newline='') as csvfile:
        csvreader = csv.reader(csvfile, quotechar='"')
        for row in csvreader:
            data.append(row)
    # remove the first row
    if not len(data) == 0:
        data.pop(0)
    return data


def write_to_csv(rows):
    with open('old_data.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, quotechar='"')
        for row in rows:
            writer.writerow(row)
        csvfile.flush()


def main():
    # Exported schema:
    # ID, VIEWERS, FOLLOWERS, PARTNER, TIMESTAMP
    # Name is the file name, appeneded at the end
    print('Reading CSV data')
    csv_files = os.listdir(os.getcwd())
    csv_files.remove('convert_to_new_format.py')
    all_data = []
    for file in tqdm(csv_files):
        data = read_csv(os.path.join(os.getcwd(), file))
        if len(data) <= 1:
            continue
        # add the streamer name at the end
        data.append(file.replace('.csv', ''))
        all_data.append(data)
    print('Writing CSV data')
    # New Schema is:
    # NAME, VIEWERS, FOLLOWERS, PARTNER, TIMESTAMP
    time.sleep(0.1)
    for streamer_data in tqdm(all_data):
        # print(streamer_data)
        # the name is stored last
        name = streamer_data.pop(-1)
        new_schema_data_rows = [[name, row[1], row[2], row[3], row[4]] for row in streamer_data]
        for row in streamer_data:
            if not len(row) == 5:
                print(row)
        write_to_csv(new_schema_data_rows)


if __name__ == '__main__':
    main()
