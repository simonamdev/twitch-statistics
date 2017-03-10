import csv
import os
import time
from datetime import datetime
from shutil import move as move_file

import twitchapi

cycle_delay = 30  # seconds

game_configurations = [
    {
        'url_name': 'Elite:%20Dangerous',
        'full_name': ['Elite: Dangerous', 'Elite Dangerous'],
        'shorthand': 'ED'
    },
    {
        'url_name': 'Planet%20Coaster',
        'full_name': ['Planet Coaster', 'Planet: Coaster'],
        'shorthand': 'PC'
    },
]


def pause(amount=5):
    for pause_tick in range(amount, 0, -1):
        print('Paused for {} seconds   '.format(pause_tick), end='\r')
        time.sleep(1)
    print('                                    ', end='\r')


def write_to_file(file_name, rows):
    with open(file_name, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, quotechar='"')
        for row in rows:
            writer.writerow(row)
        csvfile.flush()
        print('Written {} rows to {}'.format(len(rows), file_name))


def get_current_date_string():
    previous_day, previous_month, previous_year = datetime.now().day, datetime.now().month, datetime.now().year
    return '{}_{}_{}'.format(previous_day, previous_month, previous_year)


def get_twitch_client_id():
    with open('client_id.txt', 'r') as id_file:
        return id_file.readline().strip()


def main():
    client_id = get_twitch_client_id()
    current_date_string = get_current_date_string()
    while True:
        # Scrape the data for each game
        for game_configuration in game_configurations:
            # if a new day has started, move the completed data to its respective subfolder
            new_date_string = get_current_date_string()
            if not current_date_string == new_date_string:
                data_folder = os.path.join(os.getcwd(), 'data', game_configuration['shorthand'], file_name)
                print('Moving {} to: {}'.format(file_name, data_folder))
                move_file(src=file_name, dst=data_folder)
                current_date_string = new_date_string
            print('Scraping data for: {}'.format(game_configuration['full_name'][0]))
            # Get the data for the current game by invoking the twitchapi module
            api = twitchapi.APIStreamsRequest(
                game_url_name=game_configuration['url_name'],
                game_full_names=game_configuration['full_name'],
                client_id=client_id)
            try:
                api.request_all_game_data()
            except Exception as e:
                print(e)
                time.sleep(5)
                # move onto the next game
                continue
            returned_data = api.return_required_data()
            # if any returned data is available, then write to to the CSV
            file_name = game_configuration['shorthand'] + '_' + current_date_string + '.csv'
            if returned_data is not None and len(returned_data) > 0:
                write_to_file(
                    file_name=file_name,
                    rows=returned_data)
            else:
                print('No rows written for: {}'.format(game_configuration['full_name']))

        pause(cycle_delay)


if __name__ == '__main__':
    main()
