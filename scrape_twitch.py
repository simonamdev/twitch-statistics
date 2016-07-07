import csv
import os
from datetime import datetime
from shutil import move as move_file
from time import sleep
from cfg import SCP_COMMAND, EMAIL_COMMAND
from consolidate_data import consolidate_all_data
from collection import twitchapi

# Global values
cycle_delay = 30  # seconds


def pause(amount=5):
    for time in range(amount, 0, -1):
        print('[+] Paused for {} seconds   '.format(time), end='\r')
        sleep(1)
    print('                                    ', end='\r')


def get_config_values():
    with open('games.txt', 'r') as file:
        data = file.readlines()
    data = [data.strip() for data in data if not data.startswith('#')]
    dicts_list = []
    for i in range(0, len(data) // 4):
        return_dict = {
            'url': data.pop(0),
            'full': data.pop(0),
            'possible_full': data.pop(0).split(','),
            'short': data.pop(0)
        }
        dicts_list.append(return_dict)
    return dicts_list


def insert_data_rows_into_csv(file_name=None, data_rows=None, verbose=False):
    if file_name is None:
        if verbose:
            print('[-] No file name given to write to as a CSV file!')
    elif data_rows is None:
        if verbose:
            print('[-] No data rows provided to write to CSV!')
    else:
        file_name += '.csv'  # append the format to the file name
        with open(file_name, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, quotechar='"')
            for row in data_rows:
                writer.writerow(row)
            csvfile.flush()
            if verbose:
                print('[+] Successfully wrote {} rows to {}'.format(len(data_rows), file_name))


def consolidate_data(game_dicts, previous_date_string):
    # get the pynma object
    print('[+] Starting consolidation procedure')
    notification_string = ''
    game_shorthands = []
    for game in game_dicts:
        game_shorthands.append(game['shorthand_name'])
        try:
            # gather information for the backup notification
            file_name = game['shorthand_name'] + '_' + previous_date_string + '.csv'
            file_size = os.path.getsize(file_name)
            file_size = round(file_size / (1024 * 1024), 2)
            notification_string += '{}: {}MB. '.format(game['name'], file_size)
            # run the backup command
            os.system(SCP_COMMAND.format(file_name, game['shorthand_name']))
            # move the file to its respective data directory for consolidation
            data_folder = os.path.join(os.getcwd(), 'data', game['shorthand_name'], 'csv')
            move_file(src=file_name, dst=data_folder)
        except Exception as e:
            print('[-] Backing up error: {}'.format(e))
            notification_string += 'NOT FINISHED. '
    # perform consolidation into DB
    try:
        consolidate_all_data(game_shorthands=game_shorthands)
        notification_string += '\nConsolidation of files completed successfully'
    except Exception as e:
        print('[-] Consolidation error: {}'.format(e))
        notification_string += '\nConsolidation of files did not complete successfully'
    os.system(EMAIL_COMMAND.format(notification_string))
    # hold for two seconds
    pause(2)
    """
    # run the get info object
    # CURRENTLY DISABLED DUE TO LACK OF VPS RESOURCES
    for game in game_dicts:
        output = TwitchStatisticsOutput(game_name=game['name'],
                                        game_shorthand=game['shorthand_name'],
                                        db_mid_directory='',
                                        verbose=True)
        output.run()
    """


def get_current_date_string():
    previous_day, previous_month, previous_year = datetime.now().day, datetime.now().month, datetime.now().year
    return '{}_{}_{}'.format(previous_day, previous_month, previous_year)


def process_streamer_data(data_list=None):
    if data_list is None:
        return []
    return_data = []
    for i, streamer_data in enumerate(data_list):
        streamer_name = streamer_data['channel']['name']
        # get the data for this streamer
        viewer_count = streamer_data['viewers']
        if viewer_count == 0:
            # skip this streamer if they have no viewers
            continue
        follower_count = streamer_data['channel']['followers']
        partnership = 0
        if streamer_data['channel']['partner']:
            partnership = 1
        print('[{}] {}\t\t({}, {}, {})'.format(
            i,
            streamer_name,
            viewer_count,
            follower_count,
            partnership
        ))
        # sleep(0.1)  # allows reading the names when checking top streamer
        # replace the underscores for dashes in this timestamp
        timestamp = '{} {}:{}:{}'.format(
                get_current_date_string().replace('_', '-'),
                datetime.now().hour,
                datetime.now().minute,
                datetime.now().second
        )
        # add the data to the list
        return_data.append([streamer_name, viewer_count, follower_count, partnership, timestamp])
    return return_data


def write_tick_timestamp():
    with open('tick_timestamps.txt', mode='a') as textfile:
        textfile.write('{} {}:{}:{}\n'.format(
                get_current_date_string().replace('_', '-'),
                datetime.now().hour,
                datetime.now().minute,
                datetime.now().second
        ))


def main():
    games = get_config_values()
    previous_day = datetime.now().day
    previous_date_string = get_current_date_string()
    while True:
        # check if a day has passed
        day = datetime.now().day
        current_date_string = get_current_date_string()
        # if a day has finished, then make a backup
        if not day == previous_day:
            # update the previous day number. No need to compare the month/year too
            previous_day = day
            # run consolidation procedure
            consolidate_data(game_dicts=games, previous_date_string=previous_date_string)
            # update the date string
            previous_date_string = current_date_string
        # for each game, get the data
        for game_name in games:
            print('Starting cycle for: {}'.format(game_name['full']))
            # Get the data for the current game by invoking the twitchapi module
            api = twitchapi.APIStreamsRequest(game_url_name=game_name['url'], game_proper_name=game_name['full'], verbose=True)
            api.request_all_game_data()

            """
            json_url_streams = r'https://api.twitch.tv/kraken/streams?game={}'.format(game['url_name'])
            # initial api ping to get the first set of streamers
            try:
                data_games = requests.get(json_url_streams, timeout=10).json()
                total_stream_count = data_games['_total']
            except Exception as e:
                print('[-] Error getting JSON data for streamer list: {}'.format(e))
                pause(10)  # delay before trying again
            else:
                # write the timestamp to a text file to allow checking for uptime
                write_tick_timestamp()
                print('[+] {} ongoing streams for {}'.format(total_stream_count, game['name']))
                api_offset_count = 0
                try:
                    streams_data = data_games['streams']
                except Exception as e:
                    print('[-] Key error: {}'.format(e))
                    continue
                while not len(streams_data) == 0:
                    print('[+] Stream count: {} Offset: {}'.format(len(data_games['streams']), api_offset_count))
                    # only ping the api again if you are not on the first page
                    if not api_offset_count == 0:
                        # print('[+] Accessing url: {}'.format(next_json_url))
                        try:
                            next_json_url = data_games['_links']['next']
                            data_games = requests.get(next_json_url, timeout=10).json()
                        except Exception as e:
                            print('[-] Error getting JSON data for streamer list: {}'.format(e))
                    try:
                        streams_data = data_games['streams']
                    except Exception as e:
                        print('[-] Error parsing JSON data: {}'.format(e))
                        streams_data = []
                        continue
                    # only consider the streamer if they are playing the game
                    game_streamers_data = [row for row in streams_data if row['game'] in game['game_names']]
                    # store all current stream data in a list
                    current_stream_data = process_streamer_data(data_list=game_streamers_data)
                    # Write only if rows have been added
                    if len(current_stream_data) > 0:
                        insert_data_rows_into_csv(
                            file_name=game['shorthand_name'] + '_' + current_date_string,
                            data_rows=current_stream_data,
                            verbose=True)
                    api_offset_count += 90
                            """
        pause(cycle_delay)

if __name__ == '__main__':
    main()
