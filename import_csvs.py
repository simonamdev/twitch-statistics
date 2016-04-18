import csv
import os
from tqdm import tqdm
from pysqlite import Pysqlite


def create_streamer_table(self, db, streamer, ignore_list):
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


class CSVimport:
    def __init__(self, games=None, delete_file=False):
        self.games = games
        self.delete_file = delete_file

    def run(self):
        for game in self.games:
            print('Consolidating data for: {}'.format(game))
            db = Pysqlite(database_name='{} DB'.format(game), database_file='{}_stats.db'.format(game))
            existing_tables = db.get_db_data('sqlite_master')
            # existing_tables = [name[0] for name in existing_tables]
            data_directory = os.path.join(os.getcwd(), 'data', game)
            data_files = os.listdir(data_directory)
            sorted_files = sort_files_by_date(data_files)
            print('Starting import of {} CSVs'.format(len(data_files)))
            for i, file_name in enumerate(sorted_files):
                print('Importing from file: {}'.format(file_name))
                csv_data = []
                file_path = os.path.join(data_directory, file_name)
                # open the file in read mode and place the data in a list
                with open(file_path, newline='') as csvfile:
                    csvreader = csv.reader(csvfile, quotechar='"')
                    for row in csvreader:
                        csv_data.append(row)
                for row in tqdm(csv_data):
                    # Create a table in the DB according to the name in the row of data
                    # Add an underscore to table names that start with a number, as sqlite complains about them
                    if row[0][0].isdigit():
                        row[0] = '_' + row[0]
                    create_streamer_table(db=db, streamer=row[0], ignore_list=existing_tables)
                    # insert the values into a database row
                    try:
                        db.dbcur.execute('INSERT INTO {} VALUES (NULL, ?, ?, ?, ?)'.format(row[0]), (row[1], row[2], row[3], row[4]))
                    except Exception as e:
                        print(e)
                # Commit the data to the db before moving onto the next set of data
                db.dbcon.commit()
                if self.delete_file:
                    # Remove the CSV file after import the data into the DB
                    print('Deleting file: {}, {}/{}'.format(file_name, i + 1, len(data_files)))
                    os.remove(file_path)
        print('Import complete')

"""
def main():
    pass

if __name__ == '__main__':
    main()
"""
