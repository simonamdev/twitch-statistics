import os
import unittest


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
    def test_import(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
