import datetime
import os
from neopysqlite.neopysqlite import Pysqlite, PysqliteCouldNotRetrieveData
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


class TwitchStatisticsOutput:
    # bounds for the tiers of streamers
    tier_one_bounds = {'upper': 999999, 'lower': 100}
    tier_two_bounds = {'upper': 99, 'lower': 50}
    tier_three_bounds = {'upper': 49, 'lower': 15}
    tier_four_bounds = {'upper': 14, 'lower': 0}

    def __init__(self, game_name, game_shorthand, verbose=False):
        self.name = game_name
        self.shorthand = game_shorthand
        self.db_file_path = os.path.join(os.getcwd(), 'data', '{}_stats.db'.format(game_shorthand))
        self.db = Pysqlite(database_name='twitch_stats', database_file=self.db_file_path)
        self.verbose = verbose

    def run(self):
        if self.verbose:
            print('Processing data for game: {}'.format(self.name))
        tables = self.db.get_table_names()
        tables = [table for table in tables if table not in ['test', 'sqlite_sequence']]
        # get the table names which do not start with a number
        valid_named_tables = [table for table in tables if not table[0][0].isdigit()]
        # get the table names which start with a number
        number_start_tables = [table for table in tables if table[0][0].isdigit()]
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
            all_streamer_data.append(self.get_streamer_dict(streamer))
        # write the data to the text file
        self.write_text_file(streamer_data=all_streamer_data)

    def return_streamer_tier(self, average_viewers):
        if self.tier_one_bounds['upper'] >= average_viewers >= self.tier_one_bounds['lower']:
            return 1
        if self.tier_two_bounds['upper'] >= average_viewers >= self.tier_two_bounds['lower']:
            return 2
        if self.tier_three_bounds['upper'] >= average_viewers >= self.tier_three_bounds['lower']:
            return 3
        if self.tier_four_bounds['upper'] >= average_viewers >= self.tier_four_bounds['lower']:
            return 4
        return 0

    def get_streamer_dict(self, streamer):
        streamer_dict = dict()
        streamer_dict['name'] = streamer
        # catch an exception where the table cannot be found and return an empty dictionary instead
        try:
            data = self.db.get_all_rows(table=streamer)
        except PysqliteCouldNotRetrieveData:
            streamer_dict['partnership'] = False
            streamer_dict['tier'] = 4
            streamer_dict['viewers'] = []
            streamer_dict['viewers_max'] = 0
            streamer_dict['viewers_average'] = 0.0
            streamer_dict['followers'] = []
            streamer_dict['followers_max'] = 0
            streamer_dict['times'] = []
            streamer_dict['durations'] = []
            streamer_dict['durations_max'] = 0
            streamer_dict['durations_average'] = 0.0
            streamer_dict['durations_total'] = 0.0
            streamer_dict['stream_count'] = 0
            return streamer_dict
        streamer_dict['partnership'] = data[-1][3] == 1
        viewers = [field[1] for field in data]
        streamer_dict['viewers'] = [field[1] for field in data]
        streamer_dict['viewers_max'] = max(viewers)
        streamer_dict['viewers_average'] = sum(viewers) // len(viewers)
        streamer_dict['tier'] = self.return_streamer_tier(streamer_dict['viewers_average'])
        followers = [field[2] for field in data]
        streamer_dict['followers'] = followers
        streamer_dict['followers_max'] = followers[-1]
        streamer_dict['times'] = [field[4] for field in data]  # times
        streamer_dict['durations'] = get_stream_durations(streamer_dict['times'])
        streamer_dict['durations_max'] = max(streamer_dict['durations'])
        streamer_dict['durations_average'] = round(sum(streamer_dict['durations']), 2)
        streamer_dict['durations_total'] = round(sum(streamer_dict['durations']), 2)
        streamer_dict['stream_count'] = len(streamer_dict['durations'])
        return streamer_dict

    def write_text_file(self, streamer_data):
        durations = [streamer['durations'] for streamer in streamer_data]
        # get the longest consecutive stream
        non_empty_durations = [duration for duration in durations if not duration == []]
        longest_stream = max([max(duration_set) for duration_set in non_empty_durations])
        # calculate total time streamed over all streamers
        total_duration_sums = sum([sum(duration_set) for duration_set in non_empty_durations])
        total_duration = round(total_duration_sums, 2)
        total_streams = 0
        # calculate the total number of discrete streams
        for streamer in streamer_data:
            total_streams += streamer['stream_count']
        text_file_path = os.path.join(os.getcwd(), 'data', '{}_Twitch_Stats.txt'.format(self.shorthand))
        with open(text_file_path, mode='w', encoding='utf-8') as file:
            file.write('{} Twitch Streamer Statistics\n'.format(self.name))
            file.write('Data recorded 24/7 via twitch\'s public API every ~20 seconds\n')
            file.write('Script written by Simon Agius Muscat / CMDR Purrcat\n')
            file.write('More information can be found at: https://github.com/purrcat259/twitch-statistics\n')
            file.write('Total streamers recorded: {}\n'.format(len(streamer_data)))
            file.write('Total streams recorded: {}\n'.format(total_streams))
            file.write('Total time streamed: {} hours\n'.format(total_duration))
            file.write('Longest single stream: {} hours\n'.format(round(longest_stream, 2)))
            file.write('Tier One Bounds: {} >= Average Viewers >= {}\n'.format(self.tier_one_bounds['upper'], self.tier_one_bounds['lower']))
            file.write('Tier One Streamers: {}\n'.format(len([s for s in streamer_data if self.return_streamer_tier(s['viewers_average']) == 1])))
            file.write('Tier Two Bounds: {} >= Average Viewers >= {}\n'.format(self.tier_two_bounds['upper'], self.tier_two_bounds['lower']))
            file.write('Tier Two Streamers: {}\n'.format(len([s for s in streamer_data if self.return_streamer_tier(s['viewers_average']) == 2])))
            file.write('Tier Three Bounds: {} >= Average Viewers >= {}\n'.format(self.tier_three_bounds['upper'], self.tier_three_bounds['lower']))
            file.write('Tier Three Streamers: {}\n'.format(len([s for s in streamer_data if self.return_streamer_tier(s['viewers_average']) == 3])))
            file.write('Tier Four Bounds: {} >= Average Viewers >= {}\n'.format(self.tier_four_bounds['upper'], self.tier_four_bounds['lower']))
            file.write('Tier Four Streamers: {}\n'.format(len([s for s in streamer_data if self.return_streamer_tier(s['viewers_average']) == 4])))
            for streamer in streamer_data:
                # skip streamers with total durations less than 10 minutes
                if streamer['durations_total'] < 0.2:
                    continue
                file.write('\nStreamer: {} (T{})\n'.format(streamer['name'], streamer['tier']))
                file.write('Partnered: {} \n'.format(streamer['partnership']))
                file.write('Average Viewers: {}\n'.format(streamer['viewers_average']))
                file.write('Peak Viewers: {}\n'.format(streamer['viewers_max']))
                file.write('Followers: {}\n'.format(streamer['followers_max']))
                file.write('Stream count: {}\n'.format(streamer['stream_count']))
                file.write('Average Stream duration: {} hours\n'.format(streamer['durations_average']))
                file.write('Longest Stream duration: {} hours\n'.format(streamer['durations_max']))
                file.write('Total time streamed: {} hours\n'.format(streamer['durations_total']))
                time_percentage = round((streamer['durations_total'] / total_duration) * 100, 3)
                file.write('Percentage streamed of total duration: {}%\n'.format(time_percentage))
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
        out = TwitchStatisticsOutput(game_name=game['name'], game_shorthand=game['shorthand'], verbose=True)
        out.run()

if __name__ == '__main__':
    main()
