from pysqlite import Pysqlite
from pprint import pprint
from time import sleep
from tqdm import tqdm
import plotly.plotly as py
import plotly.graph_objs as go


def calculate_average(number_list):
    average = 0
    for number in number_list:
        average += number
    average /= len(number_list)
    return int(average)

print('Opening database connection')
database = Pysqlite('twitch_stats', 'twitch_stats_v2_20.db')
table_names = database.get_db_data('sqlite_sequence')
table_names = [row[0] for row in table_names]
all_streamer_data = []
"""
tier_one_streamers = []
tier_two_streamers = []
tier_three_streamers = []
tier_four_streamers = []
"""
streamer_to_plot = ''
streamers_to_ignore = ['legenddolby1986']
print('Processing Streamer Data')
for streamer in tqdm(table_names):
    # filter out the ones on the ignore list
    if streamer in streamers_to_ignore:
        continue
    streamer_data = database.get_db_data(streamer)
    # pprint(streamer_data)
    streamer_dict = dict()
    streamer_dict['name'] = streamer
    streamer_dict['type'] = 'scatter'  # plot type
    streamer_dict['mode'] = 'markers'  # plot type
    streamer_dict['connectgaps'] = False  # plot type
    streamer_dict['viewers'] = [data[1] for data in streamer_data]  # viewers
    streamer_dict['followers'] = [data[2] for data in streamer_data]  # followers
    streamer_dict['times'] = [data[4] for data in streamer_data]  # times
    if len(streamer_to_plot) > 0 and streamer == streamer_to_plot:
        all_streamer_data = [streamer_dict]
        break
    all_streamer_data.append(streamer_dict)

print('Filtering streamer data by tier')
tier_one_streamers = [streamer for streamer in all_streamer_data if calculate_average(streamer['viewers']) >= 100]
tier_two_streamers = [streamer for streamer in all_streamer_data if 100 > calculate_average(streamer['viewers']) >= 50]
tier_three_streamers = [streamer for streamer in all_streamer_data if 50 > calculate_average(streamer['viewers']) >= 15]
tier_four_streamers = [streamer for streamer in all_streamer_data if calculate_average(streamer['viewers']) < 15]

print('Tier One: {} (>100)\nTier Two: {} (99-50)\nTier Three: {} (50-15)\nTier Four: {} (<15)\nTotal: {}'.format(
    len(tier_one_streamers),
    len(tier_two_streamers),
    len(tier_three_streamers),
    len(tier_four_streamers),
    len(table_names)
))


print('Tier One Streamers:')
print('Index : Name : Peak Viewership : Average Viewership : Followers')
for streamer_dict in tier_one_streamers:
    print('{} : {} : {} : {} : {}'.format(
        tier_one_streamers.index(streamer_dict),
        streamer_dict['name'], max(streamer_dict['viewers']),
        calculate_average(streamer_dict['viewers']),
        streamer_dict['followers'][-1]))

sleep(600)

streamers_to_plot = tier_one_streamers

"""
# take the first and last times as strings to put in the axis label
min_time_string = streamer_times[0]
max_time_string = streamer_times[-1]
# convert the times to epoch seconds
# pattern: 2016-01-25 10:46:18
# pattern = '%Y-%m-%d %H:%M:%S'
# streamer_times = [int(time.mktime(time.strptime(str(stamp), pattern))) for stamp in streamer_times]
"""


def plot_viewers_followers(streamer_dict):
    print('Plotting data for: {}'.format(streamer_dict['name']))
    viewers_trace = go.Bar(
        x=streamer_dict['times'],
        y=streamer_dict['viewers'],
        name='Viewers'
    )

    followers_trace = go.Scatter(
        x=streamer_dict['times'],
        y=streamer_dict['followers'],
        name='Followers',
        yaxis='y2'
    )

    data = [viewers_trace, followers_trace]

    layout = go.Layout(
        title='{} Viewers & Followers over time'.format(streamer_dict['name']),
        barmode='group',
        yaxis=dict(
            title='Viewers'
        ),
        yaxis2=dict(
            title='Followers',
            anchor='x',
            overlaying='y',
            side='right'
        )
    )

    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig, filename='{} E:D Twitch Stream Stats'.format(streamer_dict['name']))

print('Sending data to plot.ly ({} plots)'.format(len(streamers_to_plot)))
for streamer in streamers_to_plot:
    plot_viewers_followers(streamer)
