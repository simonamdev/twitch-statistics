from pysqlite import Pysqlite
from pprint import pprint
import time
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

print('Opening database connection')
database = Pysqlite('twitch_stats', 'twitch_stats_v2.db')
streamers = dict()
table_names = database.get_db_data('sqlite_sequence')
table_names = [row[0] for row in table_names]
print('Streamer count: {}'.format(len(table_names)))
streamer = table_names[1]  # using hughmann as a basepoint
print('Streamer: {}'.format(streamer))
streamer_data = database.get_db_data(streamer)
# pprint(streamer_data)
streamer_viewers = [data[1] for data in streamer_data]
streamer_times = [data[4] for data in streamer_data]
# take the first and last times as strings to put in the axis label
min_time_string = streamer_times[0]
max_time_string = streamer_times[-1]

"""
# convert the times to epoch seconds
# pattern: 2016-01-25 10:46:18
# pattern = '%Y-%m-%d %H:%M:%S'
# streamer_times = [int(time.mktime(time.strptime(str(stamp), pattern))) for stamp in streamer_times]
"""


py.plot(
    {
        "data": [{
            "type": 'bar',
            "x": streamer_times,
            "y": streamer_viewers
        }],
        "layout": {
            "title": "{} Viewers over time".format(streamer),
            "barmode": "group"
        }
    }, filename='{} views over time'.format(streamer),
    sharing='public')
