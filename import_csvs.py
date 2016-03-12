import csv
import os
from tqdm import tqdm
from pysqlite import Pysqlite
from os import remove as delete_file


def create_streamer_table(db, streamer, ignore_list):
    if streamer not in ignore_list:
        create_statement = 'CREATE TABLE IF NOT EXISTS `{}` (`id` ' \
                       'INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,' \
                       '`viewers`	INTEGER NOT NULL,' \
                       '`followers`	INTEGER NOT NULL,' \
                       '`partner`	INTEGER NOT NULL,' \
                       '`time` TEXT NOT NULL)'
        try:
            db.execute_sql('{}'.format(create_statement.format(streamer)))
            # TODO: add some sort of feedback if the table already exists
        except Exception as e:
            print(e)


def main():
    database = Pysqlite('twitch_stats', 'twitch_stats_v2.db')
    existing_tables = database.get_db_data('sqlite_sequence')
    existing_tables = [name[0] for name in existing_tables]
    directory = os.getcwd() + '/data/'
    data_files = os.listdir(directory)
    print(data_files)
    print('Starting import of {} CSVs'.format(len(data_files)))
    for file_name in sorted(data_files):
        csv_data = []
        print('Importing file: {}'.format(file_name))
        with open(directory + file_name, newline='') as csvfile:
            csvreader = csv.reader(csvfile, quotechar='"')
            for row in csvreader:
                csv_data.append(row)
        for row in tqdm(csv_data):
            # Create a table in the DB according to the name in the row of data
            create_streamer_table(database, row[0], existing_tables)
            # Insert the values into the database
            try:
                database.dbcur.execute('INSERT INTO {} VALUES (NULL, ?, ?, ?, ?)'.format(row[0]), (row[1], row[2], row[3], row[4]))
            except Exception as e:
                print(e)
        print('Commiting data')
        database.dbcon.commit()
        print('Deleting file: {}'.format(file_name))
        delete_file(directory + file_name)
    print('All done :)')

if __name__ == '__main__':
    main()
