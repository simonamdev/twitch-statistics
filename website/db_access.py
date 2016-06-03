import os
from math import ceil
from neopysqlite.neopysqlite import Pysqlite
from ocellus import convert_name


def get_streamer_names(game):
    names = os.listdir(os.path.join(os.getcwd(), 'data', game, 'streamers'))
    # remove the .db extension and return
    return [name.replace('.db', '') for name in names]


def paginate(data_list, n):
    n = max(1, n)
    return [data_list[i:i + n] for i in range(0, len(data_list), n)]


class StreamerOverviewsDataPagination:
    def __init__(self, game_name, per_page):
        self.game_name = game_name
        self.page = 1
        self.per_page = per_page
        self.max_page = 0
        self.data_list = []
        self.pages = []

    def run(self):
        # for all the streamers, get their last overview
        overview_rows = []
        streamers = get_streamer_names(game=self.game_name)
        for streamer in streamers:
            db_path = os.path.join(os.getcwd(), 'data', self.game_name, 'streamers', '{}.db'.format(streamer))
            db = Pysqlite(database_name='{} Page DB'.format(self.game_name), database_file=db_path)
            # get the latest overview row
            row = db.get_specific_rows(table='overview', filter_string='id = (SELECT MAX(id) FROM overview)')
            row = list(row[0])
            # add the name to the end of the row
            row.append(streamer)
            overview_rows.append(row)
        # point the data list to the overview rows
        self.data_list = overview_rows
        # split the data into pages according to the per page
        self.pages = paginate(overview_rows, self.per_page)

    def get_page(self, page_number):
        # do - 1 to set it as a zero index
        # print(self.pages[page_number - 1])
        return self.pages[page_number - 1]

    def get_page_count(self):
        return int(ceil(len(self.data_list) / float(self.per_page)))

    def has_previous_page(self):
        return self.page > 1

    def has_next_page(self):
        return self.page < self.get_page_count()


class GameOverviewsData:
    def __init__(self, game_url_name):
        self.game_url_name = game_url_name
        self.data_list = []

    def run(self):
        short_name = convert_name('url', self.game_url_name, 'short')
        db_path = os.path.join(
                os.getcwd(), 'data', short_name, '{}_data.db'.format(short_name)
        )
        db = Pysqlite(database_name='{} Global Overview DB'.format(self.game_url_name), database_file=db_path)
        row = db.get_specific_rows(table='global_data', filter_string='id = (SELECT MAX(id) FROM global_data)')
        # Get the latest row
        self.data_list = list(row[0])
        return self.return_data_dict()

    def return_data_dict(self):
        game_data = {
            'last_updated': self.data_list[0],
            'streamer_count': self.data_list[1],
            'stream_count': self.data_list[2],
            'stream_duration_average': self.data_list[3],
            'stream_duration_total': self.data_list[4],
            'stream_duration_max': self.data_list[5]
        }
        return game_data

