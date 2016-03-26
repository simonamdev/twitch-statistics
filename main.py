import requests
import pynma
import csv
from cfg import SCP_COMMAND, pynma_api
from datetime import datetime
from time import sleep
# from os import remove as remove_file
from os import system as run_command
from os.path import getsize as get_file_size


def pause(amount=5):
    for time in range(amount, 0, -1):
        print('[+] Paused for {} seconds   '.format(time), end='\r')
        sleep(1)
    print('                                    ', end='\r')


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


def main():
    games = [
        {
            'url_name': 'Elite:%20Dangerous',
            'name': 'Elite: Dangerous',
            'game_names': ['Elite: Dangerous', 'Elite Dangerous'],
            'shorthand_name': 'ED'
        },
        {
            'url_name': 'Planet%20Coaster',
            'name': 'Planet Coaster',
            'game_names': ['Planet: Coaster', 'Planet Coaster'],
            'shorthand_name': 'PC'
        }
    ]
    p = pynma.PyNMA(pynma_api)
    cycle_delay = 20  # seconds
    previous_day, previous_month, previous_year = datetime.now().day, datetime.now().month, datetime.now().year
    previous_date_string = '{}_{}_{}'.format(previous_day, previous_month, previous_year)
    while True:
        # check if a day has passed
        day, month, year = datetime.now().day, datetime.now().month, datetime.now().year
        current_date_string = '{}_{}_{}'.format(day, month, year)
        # if a day has finished, then make a backup
        if not day == previous_day:
            print('[+] Starting up backup procedure')
            # update the previous day number. No need to compare the month/year too
            previous_day = day
            for game in games:
                try:
                    file_name = game['shorthand_name'] + '_' + previous_date_string + '.csv'
                    notification_string = '{}: {}MB successful'.format(
                        file_name,
                        round(get_file_size(file_name) / (1024 * 1024), 2))
                    run_command(SCP_COMMAND.format(file_name, game['shorthand_name']))
                    # gather information for backup notification
                    p.push(application='Twitch-stats', event='Stats: {}'.format(game['shorthand']), description=notification_string)
                    # remove the file
                    # remove_file(previous_date_string + '.csv')
                except Exception as e:
                    print('[-] Backing up error: {}'.format(e))
                    p.push('Twitch-stats', 'Twitch-stats', 'Backup for {} did not finish correctly'.format(game['name']))
            pause(5)
            # update the date string
            previous_date_string = current_date_string
        # for each game, get the data
        for game in games:
            json_url_streams = r'https://api.twitch.tv/kraken/streams?game={}'.format(game['url_name'])
            # initial api ping to get the first set of streamers
            try:
                data_games = requests.get(json_url_streams).json()
                total_stream_count = data_games['_total']
            except Exception as e:
                print('[-] Error getting JSON data for streamer list: {}'.format(e))
                pause(10)  # delay before trying again
            else:
                # pprint(data_games)
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
                            data_games = requests.get(next_json_url).json()
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
                    current_stream_data = []  # store all current stream data in a list
                    streamer_index = 0
                    for streamer_data in game_streamers_data:
                        streamer_name = streamer_data['channel']['name']
                        # get the data for this streamer
                        viewer_count = streamer_data['viewers']
                        if viewer_count == 0:
                            # skip this streamer if they have no viewers
                            continue
                        streamer_index += 1
                        follower_count = streamer_data['channel']['followers']
                        partnership = 0
                        if streamer_data['channel']['partner']:
                            partnership = 1
                        print('[{}] {}\t\t({}, {}, {})'.format(
                            streamer_index,
                            streamer_name,
                            viewer_count,
                            follower_count,
                            partnership
                        ))
                        # sleep(0.1)  # allows reading the names when checking top streamer
                        timestamp = '{}-{}-{} {}:{}:{}'.format(year, month, day, datetime.now().hour, datetime.now().minute, datetime.now().second)
                        # add the data to the list
                        current_stream_data.append([streamer_name, viewer_count, follower_count, partnership, timestamp])
                    # Write only if rows have been added
                    if len(current_stream_data) > 0:
                        insert_data_rows_into_csv(
                            file_name=game['shorthand_name'] + '_' + current_date_string,
                            data_rows=current_stream_data,
                            verbose=True)
                    api_offset_count += 90
        pause(cycle_delay)

if __name__ == '__main__':
    main()
