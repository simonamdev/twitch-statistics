import os
import json
from math import ceil
from neopysqlite.neopysqlite import Pysqlite
from pprint import pprint

game_names = [
    {
        'short': 'ED',
        'url': 'elitedangerous',
        'full': 'Elite: Dangerous'
    },
    {
        'short': 'PC',
        'url': 'planetcoaster',
        'full': 'Planet Coaster'
    }
]

def convert_name(given_type, given_name, return_type):
    for name in game_names:
        if name[given_type] == given_name:
            return name[return_type]

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
                'stream_count': streamer[6],
                'viewer_reach': int(streamer[3] * convert_to_hours(streamer[8])),
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

    def get_last_overview(self, game_short_name):
        db_con = self.db_connection_dict[game_short_name]
        latest_overview = db_con.get_specific_rows(table='overview', filter_string='id = (SELECT MAX(id) FROM overview)')
        return latest_overview

    def get_stream_count(self, game_short_name):
        db_con = self.db_connection_dict[game_short_name]
        return len(db_con.get_table_names()) - 3

    def get_follower_counts(self, game_short_name):
        db_con = self.db_connection_dict[game_short_name]
        overview_rows = db_con.get_all_rows(table='overview')
        return [
            {
                'update_time': overview[1],
                'followers': overview[4]
            } for overview in overview_rows
        ]

    def get_all_overviews(self):
        overviews_dict = dict()
        for game in game_names:
            # if the streamer has never streamed that game, skip it
            if game['short'] not in list(self.db_connection_dict.keys()):
                continue
            overview = list(self.get_last_overview(game_short_name=game['short'])[0])
            overviews_dict[game['short']] = {
                'stream_count': self.get_stream_count(game_short_name=game['short']),
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

    def check_streamed_anything(self):
        for game in game_names:
            db_path = os.path.join(os.getcwd(), 'data', game['short'], 'streamers', '{}.db'.format(self.streamer_name))
            if os.path.isfile(db_path):
                return True
        return False

    def check_for_all_games(self):
        game_exists_dict = dict()
        for game in game_names:
            db_path = os.path.join(os.getcwd(), 'data', game['short'], 'streamers', '{}.db'.format(self.streamer_name))
            game_exists_dict[game['short']] = True if os.path.isfile(db_path) else False
        return game_exists_dict

    def get_games_streamed_count(self):
        return len(self.check_for_all_games())


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

    def get_all_streams_dicts(self):
        ordered_data = self.db.get_specific_rows(
            table='streams',
            filter_string='id IS NOT NULL ORDER BY timestamp DESC')
        stream_dicts = [
            {
                'id': stream[0],
                'start_time': stream[1],
                'duration': convert_to_hours(stream[2]),
                'viewers_average': stream[3],
                'viewers_peak': stream[4],
                'follower_delta': stream[5],
            } for stream in ordered_data
        ]
        return stream_dicts

    def get_average_viewer_count_dicts(self):
        stream_dicts = self.get_all_streams_dicts()
        return [
            {
                'start_time': stream['start_time'],
                'viewers_average': stream['viewers_average']
            } for stream in stream_dicts
        ]

    def get_page_count(self):
        return int(ceil(self.data_list_length / float(self.per_page)))

    def has_previous_page(self):
        return self.page > 1

    def has_next_page(self):
        return self.page < self.get_page_count()

"""
class StreamsData:
    def __init__(self, game_short_name):
        self.game_short_name = game_short_name
        self.db_base_path = os.path.join(os.getcwd(), 'data', self.game_short_name, 'streamers')

    def open_streamer_db(self, streamer_name):
        db_path = os.path.join(self.db_base_path, '{}.db'.format(streamer_name))
        return Pysqlite(database_name='{} {} DB'.format(self.game_short_name, streamer_name), database_file=db_path)

    def get_stream_start_times(self):
        start_times = []
        streamer_db_names = os.listdir(self.db_base_path)
        streamer_db_names.remove('base')
        for streamer_db in streamer_db_names:
            db = self.open_streamer_db(streamer_name=streamer_db.replace('.db', ''))
            stream_rows = db.get_all_rows('streams')
            start_times.extend([row[1] for row in stream_rows])
        return json.dumps(start_times)
"""


class StreamData:
    def __init__(self, streamer_name, game_name, stream_id):
        self.streamer_name = streamer_name
        self.game_name = game_name
        self.stream_id = int(stream_id) - 1  # Backend is zero indexed, frontend is not
        self.max_stream_id = 0
        self.db = None

    def run(self):
        # Open a DB connection
        db_path = os.path.join(os.getcwd(), 'data', self.game_name, 'streamers', '{}.db'.format(self.streamer_name))
        self.db = Pysqlite(database_name='{} {} DB'.format(self.game_name, self.streamer_name), database_file=db_path)
        # set the max stream id
        self.max_stream_id = len(self.db.get_table_names()) - 3

    def get_stream_data(self):
        stream_overview_row = self.db.get_specific_rows(
            table='streams',
            filter_string='id IS {}'.format(self.stream_id + 1))  # the db index is also not zero indexed... an oversight I know
        stream_dict = {
            'id': self.stream_id + 1,
            'max_id': self.max_stream_id,
            'time_start': stream_overview_row[0][1],
            'duration': convert_to_hours(stream_overview_row[0][2]),
            'viewers_average': stream_overview_row[0][3],
            'viewers_peak': stream_overview_row[0][4],
            'follower_delta': stream_overview_row[0][5]
        }
        return stream_dict

    def get_stream_raw_data(self):
        raw_stream_data = self.db.get_all_rows(table='stream_{}'.format(self.stream_id))
        return raw_stream_data

    def get_stream_viewer_data_json(self):
        # Timestamp in the X axis, viewer count in the Y axis
        data = [
            [row[1], row[2]] for row in self.get_stream_raw_data()
        ]
        return json.dumps(data)


class NewsArticlesPagination:
    def __init__(self, per_page=4):
        self.page = 1
        self.per_page = per_page
        self.data_list_length = 0
        self.db = None

    def run(self):
        # Open a DB connection
        db_path = os.path.join(os.getcwd(), 'meta', 'news.db')
        self.db = Pysqlite(database_name='News DB', database_file=db_path)

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
                table='articles',
                filter_string='id IS NOT NULL ORDER BY timestamp DESC')
        self.data_list_length = len(ordered_data)
        page_data = ordered_data[page_indices['lower']:page_indices['upper']]
        # map that data to dictionaries
        article_dicts = [
            {
                'id': article[0],
                'date_written': article[1].split(' ')[0],  # pass only the date part and not the time
                'title': article[2],
                'contents': article[3][:150] + '...',  # truncate the contents string up to the first 150 characters
                'word_count': int(article[4]),
                # TODO: Implement not showing the article if it is not marked as published
                'published': True if int(article[5]) == 1 else 0
            } for article in page_data
        ]
        return article_dicts

    def get_page_count(self):
        return int(ceil(self.data_list_length / float(self.per_page)))

    def has_previous_page(self):
        return self.page > 1

    def has_next_page(self):
        return self.page < self.get_page_count()


class NewsArticle:
    def __init__(self, article_number=1):
        self.article_number = article_number
        self.db_path = os.path.join(os.getcwd(), 'meta', 'news.db')
        self.db = Pysqlite(database_name='News DB', database_file=self.db_path)

    def get_article(self):
        # get the article data by the ID
        article = self.db.get_specific_rows(
                table='articles',
                filter_string='id IS {}'.format(self.article_number))[0]
        # map that data to dictionaries
        article_dict = {
            'id': article[0],
            'date_written': article[1].split(' ')[0],  # pass only the date part and not the time
            'title': article[2],
            'contents': article[3],
            'word_count': int(article[4]),
            # TODO: Implement not showing the article if it is not marked as published
            'published': True if int(article[5]) == 1 else 0
        }
        return article_dict

