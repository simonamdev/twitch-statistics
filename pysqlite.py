import sqlite3
import os

version = '0.1'


class PysqliteError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Pysqlite:
    def __init__(self, database_name='', database_file=''):
        self.dbname = database_name
        if os.path.isfile(database_file) and os.access(database_file, os.R_OK):
            self.dbcon = sqlite3.connect(database_file)
            self.dbcur = self.dbcon.cursor()
        else:
            raise PysqliteError('{} could not be found or cannot be accessed!'.format(self.dbname))

    def execute_sql(self, execution_string):
        try:
            self.dbcur.execute(execution_string)
        except Exception as e:
            raise PysqliteError('Pysqlite exception: {}'.format(e))

    def get_db_data(self, table):
        try:
            db_data = self.dbcur.execute('SELECT * FROM {}'.format(table))
        except Exception as e:
            raise PysqliteError('Pysqlite experienced the following exception: {}'.format(e))
        data_list = []
        for row in db_data:
            data_list.append(row)
        if len(data_list) == 0:
            raise PysqliteError('Pysqlite found no data in the table: {} in the DB: {}'.format(table, self.dbname))
        return data_list

    def get_specific_db_data(self, table, filter_string=''):
        try:
            db_data = self.dbcur.execute('SELECT * FROM {} WHERE {}'.format(table, filter_string))
        except Exception as e:
            raise PysqliteError('Pysqlite experienced the following exception: {}'.format(e))
        data_list = []
        for row in db_data:
            data_list.append(row)
        if len(data_list) == 0:
            raise PysqliteError('Pysqlite found no data in the table: {} in the DB: {} using the filter: {}'.format(
                table,
                self.dbname,
                filter_string
            ))
        return data_list

    def insert_db_data(self, table, row_string, db_data):
        try:
            self.dbcur.execute('INSERT INTO {} VALUES {}'.format(table, row_string), db_data)
            self.dbcon.commit()
        except Exception as e:
            raise PysqliteError('Pysqlite experienced the following exception: {}'.format(e))

    def insert_rows_to_db(self, table, row_string, db_data_list):
        if len(db_data_list) == 0:
            raise PysqliteError('Pysqlite received no data to input')
        if len(db_data_list) == 1:
            self.insert_db_data(table, row_string, db_data_list[0])
        else:
            for data_row in db_data_list:
                try:
                    self.dbcur.execute('INSERT INTO {} VALUES {}'.format(table, row_string), data_row)
                except Exception as e:
                    raise PysqliteError('Pysqlite could not insert a row: {}'.format(e))
                try:
                    self.dbcon.commit()
                except Exception as e:
                    raise PysqliteError('Pysqlite could not commit the data: {}'.format(e))

if __name__ == '__main__':
    ggforcharity_db = Pysqlite('GGforCharity', 'ggforcharity.db')
    data = ggforcharity_db.get_db_data('testing')
    for row in data:
        print(row)
    ggforcharity_db.insert_db_data('testing', '(NULL, ?, ?, ?, ?, ?)', ('Day String', 100, 20, 'Event', 'purrcat259'))
    for row in data:
        print(row)
