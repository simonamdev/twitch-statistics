from pysqlite import Pysqlite
from pprint import pprint
from time import sleep
import plotly
import plotly.plotly as py
import plotly.graph_objs as go


def calculate_average(number_list):
    average = 0
    for number in number_list:
        average += number
    average /= len(number_list)
    return int(average)

print('Opening database connection')
database = Pysqlite('twitch_stats', 'twitch_stats_v2.db')
table_names = database.get_db_data('sqlite_sequence')
table_names = [row[0] for row in table_names]
all_streamer_data = []
tier_one_streamers = []
tier_two_streamers = []
tier_three_streamers = []
tier_four_streamers = []
for streamer in table_names:
    streamer_data = database.get_db_data(streamer)
    # pprint(streamer_data)
    streamer_dict = dict()
    streamer_dict['name'] = streamer
    streamer_dict['type'] = 'scatter'  # plot type
    streamer_dict['mode'] = 'markers'  # plot type
    streamer_dict['connectgaps'] = False  # plot type
    streamer_dict['viewers'] = [data[1] for data in streamer_data]  # viewers
    streamer_dict['followers'] = [data[2] for data in streamer_data]  # followers
    viewer_average = calculate_average(streamer_dict['viewers'])
    if viewer_average >= 80:
        print('Streamer: {} Average Viewer Count: {} Tier: {}'.format(streamer, viewer_average, 1))
        tier_one_streamers.append(streamer_dict)
    elif 80 > viewer_average >= 50:
        print('Streamer: {} Average Viewer Count: {} Tier: {}'.format(streamer, viewer_average, 2))
        tier_two_streamers.append(streamer_dict)
    elif 50 > viewer_average >= 15:
        print('Streamer: {} Average Viewer Count: {} Tier: {}'.format(streamer, viewer_average, 3))
        tier_three_streamers.append(streamer_dict)
    elif viewer_average < 15:
        print('Streamer: {} Average Viewer Count: {} Tier: {}'.format(streamer, viewer_average, 4))
        tier_four_streamers.append(streamer_dict)
    streamer_dict['followers'] = [data[2] for data in streamer_data]  # followers
    streamer_dict['times'] = [data[4] for data in streamer_data]  # times
    all_streamer_data.append(streamer_dict)

print('Tier One: {} (>80)\nTier Two: {} (80-50)\nTier Three: {} (50-15)\nTier Four: {} (<15)\nTotal: {}'.format(
    len(tier_one_streamers),
    len(tier_two_streamers),
    len(tier_three_streamers),
    len(tier_four_streamers),
    len(table_names)
))

for streamer_dict in tier_one_streamers:
    print('Name: {} Peak Viewers: {} Average Viewers: {} Followers: {}'.format(streamer_dict['name'], max(streamer_dict['viewers']), calculate_average(streamer_dict['viewers']), streamer_dict['followers'][-1]))

sleep(600)

"""
# take the first and last times as strings to put in the axis label
min_time_string = streamer_times[0]
max_time_string = streamer_times[-1]
# convert the times to epoch seconds
# pattern: 2016-01-25 10:46:18
# pattern = '%Y-%m-%d %H:%M:%S'
# streamer_times = [int(time.mktime(time.strptime(str(stamp), pattern))) for stamp in streamer_times]
"""

"""
streamer_to_plot = 'deejayknight'
streamer_dict = dict()
print('Searching for: {}'.format(streamer_to_plot))
for streamer_data in all_streamer_data:
    if streamer_data['name'] == streamer_to_plot:
        streamer_dict = streamer_data
        print('Found data for: {}'.format(streamer_to_plot))
        break
else:
    print('Streamer not found!')
    quit()
"""

print('Sending data to plot.ly ({} plots)'.format(len(tier_one_streamers)))
for streamer_dict in tier_one_streamers:
    print('Plotting data for: {}'.format(streamer_dict['name']))
    viewersTrace = go.Bar(
        x=streamer_dict['times'],
        y=streamer_dict['viewers'],
        name='Viewers'
    )

    followersTrace = go.Scatter(
        x=streamer_dict['times'],
        y=streamer_dict['followers'],
        name='Followers',
        yaxis='y2'
    )

    data = [viewersTrace, followersTrace]

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