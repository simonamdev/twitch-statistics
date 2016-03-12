import requests
import pynma
import csv
from cfg import SCP_COMMAND, pynma_api
from datetime import datetime
from time import sleep
from os import remove as remove_file
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
    p = pynma.PyNMA(pynma_api)
    cycle_delay = 30  # seconds
    previous_day, previous_month, previous_year = datetime.now().day, datetime.now().month, datetime.now().year
    previous_date_string = '{}_{}_{}'.format(previous_day, previous_month, previous_year)
    while True:
        # check if a day has passed
        day, month, year = datetime.now().day, datetime.now().month, datetime.now().year
        current_date_string = '{}_{}_{}'.format(day, month, year)
        if not day == previous_day:
            print('[+] Starting up backup procedure')
            # update the previous day number. No need to compare the month/year too
            previous_day = day
            try:
                print('[+] Sending data to backup location')
                run_command(SCP_COMMAND.format(previous_date_string + '.csv'))
                # gather information for backup notification
                p.push('Twitch-stats', 'Twitch-stats', 'Backup of {}.csv successful. File size: {} MB'.format(
                    previous_date_string,
                    round(get_file_size(previous_date_string + '.csv') / (1024 * 1024), 2)
                ))
                print('[+] Deleting old data')
                remove_file(previous_date_string + '.csv')
            except Exception as e:
                print('[-] Backing up error: {}'.format(e))
                p.push('Twitch-stats', 'Twitch-stats', 'Twitch stats backup did not finish correctly!')
            pause(3)
            # update the date string
            previous_date_string = current_date_string
        json_url_streams = r'https://api.twitch.tv/kraken/streams?game=Elite:%20Dangerous'
        # initial api ping to get the first set of streamers
        try:
            data_games = requests.get(json_url_streams).json()
            total_viewer_count = data_games['_total']
        except Exception as e:
            print('[-] Error getting JSON data for streamer list: {}'.format(e))
            pause(10)  # delay before trying again
        else:
            # pprint(data_games)
            print('[+] Total viewers watching: {}'.format(total_viewer_count))
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
                # only consider the streamer if they are playing Elite: Dangerous
                elite_streamers_data = [row for row in streams_data if row['game'] in ['Elite: Dangerous', 'Elite Dangerous']]
                current_stream_data = []  # store all current stream data in a list
                for streamer_data in elite_streamers_data:
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
                    print('[+] V: {}\tF: {}\tP: {}\tN: {}'.format(
                        viewer_count,
                        follower_count,
                        partnership == 1,
                        streamer_name))
                    sleep(0.1)  # allows reading the names when checking top streamer
                    # api search isn't perfect despite filtering for E:D only
                    timestamp = '{}-{}-{} {}:{}:{}'.format(year, month, day, datetime.now().hour, datetime.now().minute, datetime.now().second)
                    # add the data to the list
                    current_stream_data.append([streamer_name, viewer_count, follower_count, partnership, timestamp])
                # Write only if rows have been added
                if len(current_stream_data) > 0:
                    insert_data_rows_into_csv(
                        file_name=current_date_string,
                        data_rows=current_stream_data,
                        verbose=True)
                api_offset_count += 90
        pause(cycle_delay)

if __name__ == '__main__':
    main()
