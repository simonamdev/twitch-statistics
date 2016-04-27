import os
import unittest
from import_csvs import CSVimport
from shutil import move as move_file
from time import sleep
from neopysqlite.neopysqlite import Pysqlite


class TestConfigFile(unittest.TestCase):
    def test_config_exists(self):
        self.assertTrue(expr=os.path.isfile('games.txt'), msg='Config file games.txt does not exists')

    def test_config_not_empty(self):
        with open('games.txt', 'r') as config:
            self.assertNotEqual(first=len(config.readlines()), second=0, msg='Config file is empty')

    def test_config_contents_amount(self):
        with open('games.txt', 'r') as config:
            self.assertEqual(first=len(config.readlines()) % 4, second=0, msg='Config file lines not multiple of 4')


class TestCSVImport(unittest.TestCase):
    def test_import_csv(self):
        test_csv_file = 'TEST_24_4_2016.csv'
        # first clear up the test csv if it exists
        completed_file_path = os.path.join(os.getcwd(), 'data', 'Completed', test_csv_file)
        if os.path.isfile(completed_file_path):
            os.remove(completed_file_path)
        move_dir = os.path.join(os.getcwd(), 'data', 'Completed')
        c = CSVimport(games=['TEST'], db_mid_dir='data', delete_file=False, move_file_directory=move_dir, verbose=True)
        c.run()
        # move the file back to the normal dir
        data_folder = os.path.join(os.getcwd(), 'data', 'TEST')
        sleep(2)
        move_file(src=completed_file_path, dst=data_folder)
        consolidated_db = Pysqlite(database_name='Consolidated DB', database_file=os.path.join(os.getcwd(), 'data', 'TEST_stats.db'), verbose=True)
        consolidated_streamers = consolidated_db.get_table_names()
        consolidated_data = []
        for streamer in consolidated_streamers:
            consolidated_data.append(consolidated_db.get_all_rows(table=streamer))
        complete_db = Pysqlite(database_name='Complete DB', database_file=os.path.join(os.getcwd(), 'data', 'TEST_stats_complete.db'), verbose=True)
        complete_streamers = complete_db.get_table_names()
        complete_data = []
        for streamer in complete_streamers:
            complete_data.append(complete_db.get_all_rows(table=streamer))
        self.assertEqual(first=consolidated_data, second=complete_data)

if __name__ == '__main__':
    unittest.main()
