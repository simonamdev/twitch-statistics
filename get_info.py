from pysqlite import Pysqlite
from pprint import pprint
from tqdm import tqdm

# bounds for the tiers of streamers
tier_one_bounds = {'upper': 9999, 'lower': 100}
tier_two_bounds = {'upper': 99, 'lower': 50}
tier_three_bounds = {'upper': 49, 'lower': 15}
tier_four_bounds = {'upper': 14, 'lower': 0}


def get_streamer_dict(db, streamer):
    data = db.get_db_data(streamer)
    streamer_dict = dict()
    streamer_dict['name'] = streamer
    viewers = [field[1] for field in data]
    streamer_dict['viewers'] = [field[1] for field in data]
    streamer_dict['viewers_max'] = max(viewers)
    streamer_dict['viewers_average'] = calculate_average(viewers)
    followers = [field[2] for field in data]
    streamer_dict['followers'] = followers
    streamer_dict['followers_max'] = followers[-1]
    streamer_dict['times'] = [field[4] for field in data]  # times
    return streamer_dict


def calculate_average(number_list):
    average = 0
    for number in number_list:
        average += number
    average /= len(number_list)
    return int(average)


def main():
    database_file = 'PC_stats.db'
    # initialise the DB object
    database = Pysqlite('twitch_stats', database_file)
    table_names = database.get_db_data('sqlite_sequence')
    # get the table names. Ignore it if it is called test
    table_names = [row[0] for row in table_names if not row[0] == 'test']
    # initialise list for all the data
    all_streamer_data = []
    # list any streamers to ignore
    streamers_to_ignore = ['legenddolby1986']
    print('Processing Streamer Data')
    for streamer in tqdm(table_names):
        if streamer in streamers_to_ignore:
            # skip if its on the ignore list
            continue
        # get the db data from the table of the same name as the streamer and put it in the list^TM
        all_streamer_data.append(get_streamer_dict(database, streamer))

    print('Filtering streamer data by tier')
    tier_one_streamers = [streamer for streamer in all_streamer_data if tier_one_bounds['upper'] >= streamer['viewers_average'] >= tier_one_bounds['lower']]
    tier_two_streamers = [streamer for streamer in all_streamer_data if tier_two_bounds['upper'] >= streamer['viewers_average'] >= tier_two_bounds['lower']]
    tier_three_streamers = [streamer for streamer in all_streamer_data if tier_three_bounds['upper'] >= streamer['viewers_average'] >= tier_three_bounds['lower']]
    tier_four_streamers = [streamer for streamer in all_streamer_data if tier_four_bounds['upper'] >= streamer['viewers_average'] >= tier_four_bounds['lower']]

    print('Tier One: {} Tier Two: {} Tier Three: {} Tier Four: {} Total: {}'.format(
        len(tier_one_streamers),
        len(tier_two_streamers),
        len(tier_three_streamers),
        len(tier_four_streamers),
        len(table_names)
    ))

    # assign which tier to sort here. If all, just set all_streamer_data
    # streamers_to_sort = all_streamer_data
    streamers_to_sort = tier_one_streamers

    print('Unsorted:')
    print('Name : Average Viewers : Max Viewers : Followers')
    for streamer in streamers_to_sort:
        print('{} : {} : {} : {}'.format(
            streamer['name'],
            streamer['viewers_average'],
            streamer['viewers_max'],
            streamer['followers_max']
        ))

    print('Sorted by average viewership:')
    for streamer in sorted(streamers_to_sort, key=lambda streamer: streamer['viewers_average'], reverse=True):
        print('{} : {}'.format(streamer['name'], streamer['viewers_average']))

    print('Sorted by peak viewership:')
    for streamer in sorted(streamers_to_sort, key=lambda streamer: streamer['viewers_max'], reverse=True):
        print('{} : {}'.format(streamer['name'], streamer['viewers_max']))

    print('Sorted by followers:')
    for streamer in sorted(streamers_to_sort, key=lambda streamer: streamer['viewers_max'], reverse=True):
        print('{} : {}'.format(streamer['name'], streamer['followers_max']))

    """
    print('Tier One Streamers: (Average >=100 viewers)')
    print('Index : Name : Peak Viewership : Average Viewership : Followers')
    for streamer_dict in tier_one_streamers:
        print('{} : {} : {} : {} : {}'.format(
            tier_one_streamers.index(streamer_dict),
            streamer_dict['name'], max(streamer_dict['viewers']),
            calculate_average(streamer_dict['viewers']),
            streamer_dict['followers'][-1]))
    print('Tier Two Streamers: (100 > Average >= 50 viewers)')
    print('Index : Name : Peak Viewership : Average Viewership : Followers')
    for streamer_dict in tier_two_streamers:
        print('{} : {} : {} : {} : {}'.format(
            tier_two_streamers.index(streamer_dict),
            streamer_dict['name'], max(streamer_dict['viewers']),
            calculate_average(streamer_dict['viewers']),
            streamer_dict['followers'][-1]))
    print('Tier Three Streamers: (50 > Average >= 15 viewers)')
    print('Index : Name : Peak Viewership : Average Viewership : Followers')
    for streamer_dict in tier_three_streamers:
        print('{} : {} : {} : {} : {}'.format(
            tier_three_streamers.index(streamer_dict),
            streamer_dict['name'], max(streamer_dict['viewers']),
            calculate_average(streamer_dict['viewers']),
            streamer_dict['followers'][-1]))
    """

    """
    # take the first and last times as strings to put in the axis label
    min_time_string = streamer_times[0]
    max_time_string = streamer_times[-1]
    # convert the times to epoch seconds
    # pattern: 2016-01-25 10:46:18
    # pattern = '%Y-%m-%d %H:%M:%S'
    # streamer_times = [int(time.mktime(time.strptime(str(stamp), pattern))) for stamp in streamer_times]
    """

if __name__ == '__main__':
    main()
