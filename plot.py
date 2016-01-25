from matplotlib import pyplot
from numpy import arange
from pysqlite import Pysqlite
from pprint import pprint
import time

print('Opening database connection')
database = Pysqlite('twitch_stats', 'twitch_stats_v2.db')
streamers = dict()
table_names = database.get_db_data('sqlite_sequence')
table_names = [row[0] for row in table_names]
"""
for table in table_names:
    print('Accessing table for: {}'.format(table))
"""
print(len(table_names))
streamer = table_names[1]
streamer_data = database.get_db_data(streamer)
# pprint(streamer_data)
streamer_viewers = [data[1] for data in streamer_data]
streamer_times = [data[4] for data in streamer_data]
# take the first and last times as strings to put in the axis label
min_time_string = streamer_times[0]
max_time_string = streamer_times[-1]
# convert the times to epoch seconds
# pattern: 2016-01-25 10:46:18
pattern = '%Y-%m-%d %H:%M:%S'
streamer_times = [int(time.mktime(time.strptime(str(stamp), pattern))) for stamp in streamer_times]
# setup the plot
pyplot.title('Elite: Dangerous Twitch Streamer: {}'.format(streamer))
pyplot.xlabel('Time {} to {}'.format(min_time_string, max_time_string))
pyplot.xlim(min(streamer_times), max(streamer_times))
pyplot.ylabel('Viewers')
pyplot.ylim(min(streamer_viewers), max(streamer_viewers) + 5)
pyplot.plot(streamer_times, streamer_viewers)
pyplot.gca().xaxis.set_major_locator(pyplot.NullLocator())
pyplot.show()
