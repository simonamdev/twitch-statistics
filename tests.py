import os
import unittest
from neopysqlite.neopysqlite import Pysqlite
from get_info import TwitchStatisticsOutput
from filecmp import cmp as compare_files
from twitchapi import twitchapi


# Test whether the configuration file is valid
class TestConfigFile(unittest.TestCase):
    def test_config_exists(self):
        self.assertTrue(expr=os.path.isfile('games.txt'), msg='Config file games.txt does not exists')

    def test_config_not_empty(self):
        with open('games.txt', 'r') as config:
            self.assertNotEqual(first=len(config.readlines()), second=0, msg='Config file is empty')

    def test_config_contents_amount(self):
        with open('games.txt', 'r') as config:
            self.assertEqual(first=len(config.readlines()) % 4, second=0, msg='Config file lines not multiple of 4')


# Test the twitch API module
class TestTwitchAPIModule(unittest.TestCase):
    def test_module_present(self):
        self.assertTrue(os.path.isdir(os.path.join(os.getcwd(), 'twitchapi')))
        self.assertTrue(os.path.isfile(os.path.join(os.getcwd(), 'twitchapi', 'twitchapi.py')))

    def test_passing_no_game_names(self):
        with self.assertRaises(twitchapi.IllegalArgumentError):
            twitchapi.APIStreamsRequest()
        with self.assertRaises(twitchapi.IllegalArgumentError):
            twitchapi.APIStreamsRequest(game_proper_name='some game')
        with self.assertRaises(twitchapi.IllegalArgumentError):
            twitchapi.APIStreamsRequest(game_url_name='some%20game')

    def test_initial_conditions(self):
        api_request = twitchapi.APIStreamsRequest(game_url_name='Elite:%20Dangerous', game_proper_name='Elite: Dangerous')
        self.assertEquals(first=api_request.last_status_code, second=0)
        self.assertEquals(first=api_request.streams_data, second=[])
        self.assertEquals(first=api_request.json_url, second='https://api.twitch.tv/kraken/streams')



"""
class TestCSVImport(unittest.TestCase):
    def test_import_csv(self):
        c = CSVimport(games=['TEST'], db_mid_dir='data', delete_file=True, verbose=True)
        c.run()
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
"""


class TestStatisticsOutput(unittest.TestCase):
    def test_output_stats(self):
        out = TwitchStatisticsOutput(game_name='Test',
                                     game_shorthand='TEST',
                                     db_mid_directory='data',
                                     db_name_format='{}_stats_complete.db',
                                     verbose=True)
        out.run()
        self.assertTrue(os.path.isfile(os.path.join(os.getcwd(), 'data', 'TEST_Twitch_Stats.txt')))
        self.assertTrue(compare_files(
                f1=os.path.join(os.getcwd(), 'data', 'TEST_Twitch_Stats.txt'),
                f2=os.path.join(os.getcwd(), 'data', 'TEST_Twitch_Stats_complete.txt')))

if __name__ == '__main__':
    unittest.main()
