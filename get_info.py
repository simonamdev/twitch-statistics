import datetime
import os
from neopysqlite.neopysqlite import Pysqlite
from tqdm import tqdm

games = [
    {
        'name': 'Elite: Dangerous',
        'shorthand': 'ED'
     },
    {
        'name': 'Planet Coaster',
        'shorthand': 'PC'
    }
]

# bounds for the tiers of streamers
tier_one_bounds = {'upper': 999999, 'lower': 100}
tier_two_bounds = {'upper': 99, 'lower': 50}
tier_three_bounds = {'upper': 49, 'lower': 15}
tier_four_bounds = {'upper': 14, 'lower': 0}


def get_streamer_dict(db, streamer):
    data = db.get_all_rows(table=streamer)
    streamer_dict = dict()
    streamer_dict['name'] = streamer
    streamer_dict['partnership'] = data[-1][3] == 1
    viewers = [field[1] for field in data]
    streamer_dict['viewers'] = [field[1] for field in data]
    streamer_dict['viewers_max'] = max(viewers)
    streamer_dict['viewers_average'] = calculate_average(viewers)
    streamer_dict['tier'] = return_streamer_tier(streamer_dict['viewers_average'])
    followers = [field[2] for field in data]
    streamer_dict['followers'] = followers
    streamer_dict['followers_max'] = followers[-1]
    streamer_dict['times'] = [field[4] for field in data]  # times
    streamer_dict['durations'] = get_stream_durations(streamer_dict['times'])
    streamer_dict['durations_max'] = max(streamer_dict['durations'])
    streamer_dict['durations_average'] = calculate_average(streamer_dict['durations'], return_int=False)
    streamer_dict['durations_total'] = calculate_sum(streamer_dict['durations'], return_int=False)
    streamer_dict['stream_count'] = len(streamer_dict['durations'])
    streamer_dict['exposure_index'] = return_expoure_index(streamer_dict)
    return streamer_dict


def return_streamer_tier(average_viewers):
    if tier_one_bounds['upper'] >= average_viewers >= tier_one_bounds['lower']:
        return 1
    if tier_two_bounds['upper'] >= average_viewers >= tier_two_bounds['lower']:
        return 2
    if tier_three_bounds['upper'] >= average_viewers >= tier_three_bounds['lower']:
        return 3
    if tier_four_bounds['upper'] >= average_viewers >= tier_four_bounds['lower']:
        return 4
    return 0


def return_expoure_index(streamer):
    # calculated as: average viewer count * total hours streamed
    return round(streamer['viewers_average'] * streamer['durations_total'], 2)


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


def calculate_sum(number_list, return_int=True):
    total = 0
    for number in number_list:
        total += number
    if return_int:
        return int(total)
    else:
        return round(total, 2)


def process_data(game):
    print('Processing data for: {}'.format(game['name']))
    database_path = os.path.join(os.getcwd(), 'data', '{}_stats.db'.format(game['shorthand']))
    # initialise the DB object
    database = Pysqlite(database_name='twitch_stats', database_file=database_path)
    # get the table names. Ignore it if it is called test or sqlite_sequence
    table_names = database.get_table_names()
    table_names = [table for table in table_names if table not in ['test', 'sqlite_sequence']]
    # get the table names which do not start with a number
    valid_named_tables = [table for table in table_names if not table[0][0].isdigit()]
    # get the table names which start with a number
    number_start_tables = [table for table in table_names if table[0][0].isdigit()]
    # reod the original table names
    valid_named_tables.extend(['_' + table for table in number_start_tables])
    # initialise list for all the data
    all_streamer_data = []
    # list any streamers to ignore
    streamers_to_ignore = ['legenddolby1986']
    for streamer in tqdm(valid_named_tables):
        if streamer in streamers_to_ignore:
            # skip if its on the ignore list
            continue
        # get the db data from the table of the same name as the streamer and put it in the list^TM
        all_streamer_data.append(get_streamer_dict(database, streamer))

    print('Filtering streamer data by tier')
    tier_one_streamers = [streamer for streamer in all_streamer_data if streamer['tier'] == 1]
    tier_two_streamers = [streamer for streamer in all_streamer_data if streamer['tier'] == 2]
    tier_three_streamers = [streamer for streamer in all_streamer_data if streamer['tier'] == 3]
    tier_four_streamers = [streamer for streamer in all_streamer_data if streamer['tier'] == 4]
    tier_zero_streamers = [streamer for streamer in all_streamer_data if streamer['tier'] == 0]

    if len(tier_zero_streamers) > 0:
        print(tier_zero_streamers)
        input('Detected streamer which did not fit a streamer. Press any key to continue')

    print('Tiers are set by AVERAGE viewership')
    print('Tier One (>= {}): {}'.format(tier_one_bounds['lower'], len(tier_one_streamers)))
    print('Tier Two ({} >= X >= {}): {}'.format(tier_two_bounds['upper'], tier_two_bounds['lower'], len(tier_two_streamers)))
    print('Tier Three ({} >= X >= {}): {}'.format(tier_three_bounds['upper'], tier_three_bounds['lower'], len(tier_three_streamers)))
    print('Tier Four ({} >= X >= {}): {}'.format(tier_four_bounds['upper'], tier_four_bounds['lower'], len(tier_four_streamers)))

    # assign which tier to sort here. If all, just set all_streamer_data
    streamers_to_sort = all_streamer_data
    # streamers_to_sort = tier_one_streamers
    # streamers_to_sort = tier_two_streamers
    # streamers_to_sort = tier_three_streamers
    # streamers_to_sort = tier_four_streamers
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
    write_to_text_file(game_dict=game, streamer_list=streamers_to_sort)


def write_to_text_file(game_dict, streamer_list):
    total_duration = 0
    total_streams = 0
    total_exposure = 0
    # calculate total time streamed over all streamers
    for streamer in streamer_list:
        for duration in streamer['durations']:
            total_duration += duration
    total_duration = round(total_duration, 2)
    # calculate the total number of discrete streams
    for streamer in streamer_list:
        total_streams += streamer['stream_count']
    # get the total exposure index from all streamers
    for streamer in streamer_list:
        total_exposure += streamer['exposure_index']
    total_exposure = round(total_exposure, 2)
    # get the longest consecutive stream
    longest_stream = 0
    for streamer in streamer_list:
        if longest_stream < streamer['durations_max']:
            longest_stream = streamer['durations_max']
    text_file_path = os.path.join(os.getcwd(), 'data', '{}_Twitch_Stats.txt'.format(game_dict['shorthand']))
    with open(text_file_path, mode='w', encoding='utf-8') as file:
        file.write('{} Twitch Streamer Statistics\n'.format(game_dict['name']))
        file.write('Data recorded 24/7 via twitch public API every ~20 seconds\n')
        file.write('Script written by Simon Agius Muscat / CMDR Purrcat\n')
        file.write('More information can be found at: https://github.com/purrcat259/twitch-statistics\n')
        file.write('Total streamers recorded: {}\n'.format(len(streamer_list)))
        file.write('Total streams recorded: {}\n'.format(total_streams))
        file.write('Total time streamed: {} hours\n'.format(total_duration))
        file.write('Total exposure value: {} average viewers per hour\n'.format(total_exposure))
        file.write('Longest single stream: {} hours\n'.format(longest_stream))
        file.write('Tier One Bounds: {} >= Average Viewers >= {}\n'.format(tier_one_bounds['upper'], tier_one_bounds['lower']))
        file.write('Tier Two Bounds: {} >= Average Viewers >= {}\n'.format(tier_two_bounds['upper'], tier_two_bounds['lower']))
        file.write('Tier Three Bounds: {} >= Average Viewers >= {}\n'.format(tier_three_bounds['upper'], tier_three_bounds['lower']))
        file.write('Tier Four Bounds: {} >= Average Viewers >= {}\n'.format(tier_four_bounds['upper'], tier_four_bounds['lower']))
        for streamer in streamer_list:
            file.write('\nStreamer: {} (T{})\n'.format(streamer['name'], streamer['tier']))
            file.write('Partnered: {} \n'.format(streamer['partnership']))
            file.write('Average Viewers: {}\n'.format(streamer['viewers_average']))
            file.write('Peak Viewers: {}\n'.format(streamer['viewers_max']))
            file.write('Followers: {}\n'.format(streamer['followers_max']))
            file.write('Stream count: {}\n'.format(streamer['stream_count']))
            file.write('Exposure index: {} average viewers per hour\n'.format(streamer['exposure_index']))
            exposure_percentage = round((streamer['exposure_index'] / total_exposure) * 100, 2)
            file.write('Exposure percentage: {}%\n'.format(exposure_percentage))
            file.write('Average Stream duration: {} hours\n'.format(streamer['durations_average']))
            file.write('Longest Stream duration: {} hours\n'.format(streamer['durations_max']))
            file.write('Total time streamed: {} hours\n'.format(streamer['durations_total']))
            time_percentage = round((streamer['durations_total'] / total_duration) * 100, 3)
            file.write('Streamer portion of total duration: {}%\n'.format(time_percentage))
            file.write('Stream durations:\n')
            for duration in streamer['durations']:
                if duration < 1.0:
                    duration = round(duration * 60, 2)
                    # skip stream durations less than 5 m inutes
                    if duration < 5.0:
                        continue
                    file.write('\t{} minutes\n'.format(duration))
                else:
                    file.write('\t{} hours\n'.format(duration))


def main():
    for game in games:
        process_data(game)


if __name__ == '__main__':
    main()
