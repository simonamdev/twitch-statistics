import os
from math import ceil
from neopysqlite.neopysqlite import Pysqlite
from ocellus import convert_name, return_name_dict, game_names
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


class AllStreamerOverviewsDataPagination:
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


class GameGlobalData:
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


class StreamerGlobalData:
    def __init__(self, streamer_name):
        self.streamer_name = streamer_name
        self.stream_count = 0
        self.db_connection_dict = dict()

    def run(self):
        # Open DB connections for a streamer for each game
        for game in game_names:
            self.open_db_connection(game_short_name=game['short'])

    def open_db_connection(self, game_short_name):
        db_path = os.path.join(os.getcwd(), 'data', game_short_name, 'streamers', '{}.db'.format(self.streamer_name))
        if not os.path.isfile(db_path):
            pass
            # print('Streamer never streamed for: {}'.format(game_short_name))
        else:
            self.db_connection_dict[game_short_name] = Pysqlite(
                                                            database_name='Streamer {} DB'.format(self.streamer_name),
                                                            database_file=db_path)

    def get_overview(self, game_short_name):
        db_con = self.db_connection_dict[game_short_name]
        latest_overview = db_con.get_specific_rows(table='overview', filter_string='id = (SELECT MAX(id) FROM overview)')
        return latest_overview

    def get_all_overviews(self):
        overviews_dict = dict()
        for game in game_names:
            # if the streamer has never streamed that game, skip it
            if game['short'] not in list(self.db_connection_dict.keys()):
                continue
            overview = list(self.get_overview(game['short'])[0])
            overviews_dict[game['short']] = {
                'game_short': game['short'],
                'game_full': game['full'],
                'last_update': overview[1],
                'viewers_average': overview[2],
                'viewers_peak': overview[3],
                'followers': overview[4],
                'duration_average': convert_to_hours(overview[5]),
                'duration_total': convert_to_hours(overview[6]),
                'partnership': overview[7]
            }
        return overviews_dict


class DetermineIfStreamed:
    def __init__(self, streamer_name):
        self.streamer_name = streamer_name

    def check_for_all_games(self):
        game_exists_dict = dict()
        for game in game_names:
            db_path = os.path.join(os.getcwd(), 'data', game['short'], 'streamers', '{}.db'.format(self.streamer_name))
            game_exists_dict[game['short']] = True if os.path.isfile(db_path) else False
        return game_exists_dict


class StreamsDataPagination:
    def __init__(self, game_name, streamer_name, per_page=10):
        self.game_name = game_name
        self.streamer_name = streamer_name
        self.page = 1
        self.per_page = per_page
        self.data_list_length = 0
        self.db = None

    def run(self):
        # Open a DB connection
        db_path = os.path.join(os.getcwd(), 'data', self.game_name, 'streamers', '{}.db'.format(self.streamer_name))
        self.db = Pysqlite(database_name='{} {} DB'.format(self.game_name, self.streamer_name), database_file=db_path)

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
        # get an ordered list of stream overviews
        ordered_data = self.db.get_specific_rows(
                table='streams',
                filter_string='id IS NOT NULL ORDER BY timestamp DESC')
        self.data_list_length = len(ordered_data)
        page_data = ordered_data[page_indices['lower']:page_indices['upper']]
        # map that data to dictionaries
        stream_dicts = [
            {
                'id': stream[0],
                'start_time': stream[1],
                'duration': convert_to_hours(stream[2]),
                'viewers_average': stream[3],
                'viewers_peak': stream[4],
                'follower_delta': stream[5],
            } for stream in page_data
        ]
        return stream_dicts

    def get_page_count(self):
        return int(ceil(self.data_list_length / float(self.per_page)))

    def has_previous_page(self):
        return self.page > 1

    def has_next_page(self):
        return self.page < self.get_page_count()


class StreamData:
    def __init__(self, streamer_name, game_name, stream_id):
        self.streamer_name = streamer_name
        self.game_name = game_name
        self.stream_id = stream_id - 1  # Backend is zero indexed, frontend is not
        self.db = None

    def run(self):
        # Open a DB connection
        db_path = os.path.join(os.getcwd(), 'data', self.game_name, 'streamers', '{}.db'.format(self.streamer_name))
        self.db = Pysqlite(database_name='{} {} DB'.format(self.game_name, self.streamer_name), database_file=db_path)

    def get_stream_data(self):
        # if the streamer has never streamed that game, skip it
        stream_overview_row = self.db.get_specific_rows(
            table='streams',
            filter_string='id IS {}'.format(self.stream_id + 1))  # the db index is also not zero indexed... an oversight I know
        stream_raw_rows = self.db.get_all_rows(table='stream_{}')
        print(stream_overview_row)
        print(stream_raw_rows)
        stream_dict = {
            'overview': {

            },
            'raw_data': []
        }
        return stream_dict
