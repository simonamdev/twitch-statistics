import os
from math import ceil
from neopysqlite.neopysqlite import Pysqlite
from ocellus import convert_name


def convert_to_hours(seconds):
    return round(seconds / (60 * 60), 2)


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
        page_data_dicts = []
        for page in self.pages[page_number - 1]:
            page_dict = {
                'name': page[8],
                'last_update': page[1],
                'viewers_average': page[2],
                'viewers_peak': page[3],
                'followers': page[4],
                'duration_average': convert_to_hours(page[5]),
                'duration_total': convert_to_hours(page[6]),
                'partnership': page[7]
            }
            page_data_dicts.append(page_dict)
        return page_data_dicts

    def get_page_count(self):
        return int(ceil(len(self.data_list) / float(self.per_page)))

    def has_previous_page(self):
        return self.page > 1

    def has_next_page(self):
        return self.page < self.get_page_count()


class GlobalGameData:
    def __init__(self, game_url_name):
        self.game_url_name = game_url_name
        self.global_data_list = []
        short_name = convert_name('url', self.game_url_name, 'short')
        self.db_path = os.path.join(os.getcwd(), 'data', short_name, '{}_data.db'.format(short_name))
        self.db = Pysqlite(database_name='{} Global Overview DB'.format(self.game_url_name), database_file=self.db_path)

    def return_global_overview_dict(self):
        row = self.db.get_specific_rows(table='global_data', filter_string='id = (SELECT MAX(id) FROM global_data)')
        data_list = list(row[0])
        game_dict = {
            'last_updated': data_list[0],
            'streamer_count': data_list[1],
            'stream_count': data_list[2],
            'stream_duration_average': convert_to_hours(data_list[3]),
            'stream_duration_total': convert_to_hours(data_list[4]),
            'stream_duration_max': convert_to_hours(data_list[5])
        }
        return game_dict

    def return_tier_bounds(self):
        tier_bounds = self.db.get_all_rows(table='tier_bounds')
        tier_bounds_dict = [{'tier': bound[1], 'upper': bound[2], 'lower': bound[3]} for bound in tier_bounds]
        return tier_bounds_dict

    def return_tier_streamers(self):
        streamer_tiers = self.db.get_all_rows(table='tier_data')
        streamer_tiers_dict = dict()
        for index, streamer, tier in streamer_tiers:
            streamer_tiers_dict[streamer] = tier
        return streamer_tiers_dict

    def return_tier_count(self, tier_number=0):
        streamer_tiers = self.db.get_all_rows(table='tier_data')
        return len([tier for tier in streamer_tiers if tier[2] == tier_number])

    def return_tier_counts(self):
        tier_count_list = []
        tier_bounds = self.db.get_all_rows(table='tier_bounds')
        for i in range(1, len(tier_bounds) + 1):
            tier_count_list.append(self.return_tier_count(tier_number=i))
        return tier_count_list

