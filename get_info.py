import datetime
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
    streamer_dict['durations'] = get_stream_durations(streamer_dict['times'])
    streamer_dict['durations_max'] = max(streamer_dict['durations'])
    streamer_dict['durations_average'] = calculate_average(streamer_dict['durations'], return_int=False)
    return streamer_dict


def get_stream_durations(stream_times):
    # pop one field out to avoid odd numbered lists
    time_deltas = []
    for i, field in enumerate(stream_times):
        # if i == 0 or i % 2 == 0:
        # current field
        # timestamp format: '2016-01-25 10:46:18'
        date_part = field.split(' ')[0].split('-')
        time_part = field.split(' ')[1].split(':')
        year, month, day = int(date_part[0]), int(date_part[1]), int(date_part[2])
        hour, minute, second = int(time_part[0]), int(time_part[1]), int(time_part[2])
        time1 = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
        # caclulate a delta between the current and the next field
        if i+1 == len(stream_times):
            break
        next_field = stream_times[i+1]
        date_part = next_field.split(' ')[0].split('-')
        time_part = next_field.split(' ')[1].split(':')
        year, month, day = int(date_part[0]), int(date_part[1]), int(date_part[2])
        hour, minute, second = int(time_part[0]), int(time_part[1]), int(time_part[2])
        time2 = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
        time_deltas.append([time1, time2])
    stream_durations = []
    current_stream_duration = 0
    for time_one, time_two in time_deltas:
        delta = time_two - time_one
        # operate on the assumption that different streams are a minimum of 1 hour away from each other
        if delta.seconds / (60 * 60) > 1:
            # print('DIFFERENT STREAM FOUND')
            stream_durations.append(current_stream_duration)
            current_stream_duration = 0
        else:
            # print('{} {}\n{} {}\n\t{}\t{}s'.format(i, time_one, i, time_two, delta, delta.seconds))
            current_stream_duration += delta.seconds
    else:
        # if the data ends then the last recorded stream will not be recorded, so add the deltas list anyway
        stream_durations.append(current_stream_duration)
    # change it from seconds to hours
    stream_durations = [round(stream / (60 * 60), 2) for stream in stream_durations]
    return stream_durations


def calculate_average(number_list, return_int=True):
    average = 0
    for number in number_list:
        average += number
    average /= len(number_list)
    if return_int:
        return int(average)
    else:
        return round(average, 2)


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

    print('Tiers are set by AVERAGE viewership')
    print('Tier One (>= {}): {}'.format(tier_one_bounds['lower'], len(tier_one_streamers)))
    print('Tier Two ({} >= X >= {}): {}'.format(tier_two_bounds['upper'], tier_two_bounds['lower'], len(tier_two_streamers)))
    print('Tier Three ({} >= X >= {}): {}'.format(tier_three_bounds['upper'], tier_three_bounds['lower'], len(tier_three_streamers)))
    print('Tier Four ({} >= X >= {}): {}'.format(tier_four_bounds['upper'], tier_four_bounds['lower'], len(tier_four_streamers)))

    # assign which tier to sort here. If all, just set all_streamer_data
    # streamers_to_sort = all_streamer_data
    streamers_to_sort = tier_two_streamers
    print('Unsorted:')
    print('Name : Average Viewers : Max Viewers : Followers')
    for streamer in streamers_to_sort:
        print('{} : {} : {} : {}'.format(
            streamer['name'],
            streamer['viewers_average'],
            streamer['viewers_max'],
            streamer['followers_max']
        ))
    print('\nSorted by average viewership:')
    for streamer in sorted(streamers_to_sort, key=lambda streamer: streamer['viewers_average'], reverse=True):
        print('{} : {}'.format(streamer['name'], streamer['viewers_average']))
    print('\nSorted by peak viewership:')
    for streamer in sorted(streamers_to_sort, key=lambda streamer: streamer['viewers_max'], reverse=True):
        print('{} : {}'.format(streamer['name'], streamer['viewers_max']))
    print('\nSorted by followers:')
    for streamer in sorted(streamers_to_sort, key=lambda streamer: streamer['viewers_max'], reverse=True):
        print('{} : {}'.format(streamer['name'], streamer['followers_max']))
    print('\nStream durations:')
    for streamer in streamers_to_sort:
        print('{} held {} stream/s of:'.format(streamer['name'], len(streamer['durations'])))
        durations_string = '\t'
        for duration in streamer['durations']:
            if duration < 1.0:
                duration = round(duration * 60, 2)
                durations_string += '{} minutes\t'.format(duration)
            else:
                durations_string += '{} hours\t'.format(duration)
        print(durations_string)
        print('\tLongest Stream: {} hours\tAverage Stream length: {} hours'.format(streamer['durations_max'], streamer['durations_average']))


if __name__ == '__main__':
    main()
