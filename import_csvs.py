import csv
import os
from tqdm import tqdm
from pysqlite import Pysqlite
from os import remove as delete_file


def sort_files_by_date(file_list):
    # quick and dirty natural sort algorithm for timestamps
    temp_list = [file.replace('.csv', '').split('_') for file in file_list]
    return_list = []
    if len(temp_list) == 0:
        return return_list
    # game_day_month_year.csv
    game = temp_list[0][0]
    months = [int(month[2]) for month in temp_list]
    # Do it per month
    for month in range(min(months), max(months) + 1):  # exclusive range, hence + 1
        current_month = [stamp for stamp in temp_list if int(stamp[2]) == month]
        # determine min and max numbers for that month
        least_day = min([int(stamp[1]) for stamp in current_month])
        largest_day = max([int(stamp[1]) for stamp in current_month])
        # rebuild the filenames in order for the returning list
        for day in range(least_day, largest_day + 1):
            return_list.append('{}_{}_{}_2016.csv'.format(game, day, month))
    return return_list


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
    games = ['ED', 'PC']
    for game in games:
        print('Consolidating data for: {}'.format(game))
        database = Pysqlite('{}_stats'.format(game), '{}_stats.db'.format(game))
        existing_tables = database.get_db_data('sqlite_sequence')
        existing_tables = [name[0] for name in existing_tables]
        directory = os.getcwd() + '/data/' + game + '/'
        data_files = os.listdir(directory)
        print('Starting import of {} CSVs'.format(len(data_files)))
        sorted_files = sort_files_by_date(data_files)
        for file_name in sorted_files:
            csv_data = []
            print('Importing file: {}'.format(file_name))
            with open(directory + file_name, newline='') as csvfile:
                csvreader = csv.reader(csvfile, quotechar='"')
                for row in csvreader:
                    csv_data.append(row)
            for row in tqdm(csv_data):
                # Create a table in the DB according to the name in the row of data
                # Add an underscore to table names that start with a number, as sqlite complains about them
                if row[0][0].isdigit():
                    row[0] = '_' + row[0]
                create_streamer_table(database, row[0], existing_tables)
                # Insert the values into the database
                try:
                    database.dbcur.execute('INSERT INTO {} VALUES (NULL, ?, ?, ?, ?)'.format(row[0]), (row[1], row[2], row[3], row[4]))
                except Exception as e:
                    print(e)
            # Commit the data to the db before moving onto the next set of data
            database.dbcon.commit()
            print('Deleting file: {}, {}/{}'.format(file_name, sorted_files.index(file_name) + 1, len(data_files)))
            delete_file(directory + file_name)
    print('All done :)')

if __name__ == '__main__':
    main()
