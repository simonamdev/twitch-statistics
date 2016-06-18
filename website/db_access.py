import os
from math import ceil
from neopysqlite.neopysqlite import Pysqlite
from ocellus import convert_name
from pprint import pprint


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
    def __init__(self, game_name, per_page=10):
        self.game_name = game_name
        self.page = 1
        self.per_page = per_page
        self.max_page = 0
        self.data_list_length = 0
        self.pages = []
        self.db = None

    def run(self):
        # Open a DB connection
        db_path = os.path.join(os.getcwd(), 'data', self.game_name, '{}_data.db'.format(self.game_name))
        self.db = Pysqlite(database_name='{} Page DB'.format(self.game_name), database_file=db_path)

    def get_page(self, page_number):
        # figure out which indices relate to that page
        # page_number is NOT zero indexed, so we subtract 1 to make it zero indexed
        # lower bound: (page_number - 1) * self.per_page
        # upper bound: (page_number - 1) * self.per_page + (self.per_page - 1)
        # EXAMPLE:
        # I want page 2 (which is actually page 1, since -1) and I show 10 per page. Page 1's bounds are 10 -> 19, thus:
        # (2 - 1) * 10 = 10 for the lower bound
        # (2 - 1) * 10 + (10 - 1) = 10 + 9 = 19 for the upper bound
        page_indices = {
            'lower': (page_number - 1) * self.per_page,
            'upper': (page_number - 1) * self.per_page + (self.per_page - 1)
        }
        # get the streamer overviews, ordered by average viewership
        ordered_data = self.db.get_specific_rows(
                table='streamers_data',
                filter_string='id IS NOT NULL ORDER BY viewers_average DESC')
        self.data_list_length = len(ordered_data)
        page_data = ordered_data[page_indices['lower']:page_indices['upper']]
        # map that data to dictionaries
        streamer_dicts = [
            {
                'name': streamer[1],
                'last_update': streamer[2],
                'viewers_average': streamer[3],
                'viewers_peak': streamer[4],
                'followers': streamer[5],
                'duration_average': convert_to_hours(streamer[7]),
                'duration_total': convert_to_hours(streamer[8]),
                'partnership': streamer[10]
            } for streamer in page_data
        ]
        return streamer_dicts

    def get_page_count(self):
        return int(ceil(self.data_list_length / float(self.per_page)))

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
            'last_updated': data_list[1],
            'streamer_count': data_list[2],
            'stream_count': data_list[3],
            'stream_duration_average': convert_to_hours(data_list[4]),
            'stream_duration_total': convert_to_hours(data_list[5]),
            'stream_duration_max': convert_to_hours(data_list[6])
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

