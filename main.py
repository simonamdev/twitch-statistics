import requests
from cfg import SCP_COMMAND
from datetime import date
from time import sleep, strftime
from pysqlite import Pysqlite
from pprint import pprint
from os import system as run_command

create_statement = 'CREATE TABLE IF NOT EXISTS `{}` (`id` ' \
                   'INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,' \
                   '`viewers`	INTEGER NOT NULL,' \
                   '`followers`	INTEGER NOT NULL,' \
                   '`partner`	INTEGER NOT NULL,' \
                   '`time` TEXT NOT NULL)'


def pause(amount=5):
    for time in range(amount, 0, -1):
        print('[+] Paused for {} seconds   '.format(time), end='\r')
        sleep(1)
    print('                                    ', end='\r')


def create_streamer_table(db, streamer):
    try:
        db.execute_sql('{}'.format(create_statement.format(streamer)))
        # TODO: add some sort of feedback if the table already exists
    except Exception as e:
        print(e)


def insert_data_into_db(db, streamer, viewers, followers, partner):
    try:
        db.insert_db_data(streamer, '(NULL, ?, ?, ?, CURRENT_TIMESTAMP)', (viewers, followers, partner))
        # print('[+] Statistics successfully written to the database')
    except Exception as e:
        print(e)


def main():
    cycle_delay = 30  # seconds
    database = Pysqlite('twitch_stats', 'twitch_stats_v2.db')
    previous_day_number = date.day
    while True:
        # check if a day has passed
        current_day_number = date.day
        if not current_day_number == previous_day_number:
            print('[+] Starting up backup procedure')
            # update the previous day number
            previous_day_number = current_day_number
            print('[+] Closing the database connection')
            database.close_connection()
            print('[+] Backing up the database')
            try:
                run_command(SCP_COMMAND)
            except Exception as e:
                print('[-] Backing up error: {}'.format(e))
            pause(3)
            print('[+] Reponening database connection')
            database = Pysqlite('twitch_stats', 'twitch_stats_v2.db')
        json_url_streams = 'https://api.twitch.tv/kraken/search/streams?limit=100&q=Elite%20Dangerous'
        # initial api ping to get the first set of streamers
        try:
            data_games = requests.get(json_url_streams).json()
            stream_count = data_games['_total']
        except Exception as e:
            print('[-] Error getting JSON data for streamer list: {}'.format(e))
            sleep(10)  # delay before trying again
        else:
            # pprint(data_games)
            print('[+] Streams online: {}'.format(stream_count))
            api_offset_count = 0
            while api_offset_count <= int(stream_count) + 100:
                # print('[+] Streamers: {}/{}'.format(api_offset_count, stream_count))
                # only ping the api again if you are not on the first page
                if not api_offset_count == 0:
                    # print('[+] Accessing url: {}'.format(next_json_url))
                    try:
                        next_json_url = data_games['_links']['next']
                        data_games = requests.get(next_json_url).json()
                    except Exception as e:
                        print('[-] Error getting JSON data for streamer list: {}'.format(e))
                try:
                    streamers_data = data_games['streams']
                except KeyError as e:
                    print('[-] Error parsing JSON data: {}'.format(e))
                else:
                    # only consider the streamer if they are playing Elite: Dangerous
                    elite_streamers_data = [row for row in streamers_data if row['game'] in ['Elite: Dangerous', 'Elite Dangerous']]
                    for streamer_data in elite_streamers_data:
                        streamer_name = streamer_data['channel']['name']
                        # create a table for each streamer. The method avoids duplicates itself
                        create_streamer_table(database, streamer_name)
                        # get the data for this streamer
                        viewer_count = streamer_data['viewers']
                        follower_count = streamer_data['channel']['followers']
                        partnership = 0
                        if streamer_data['channel']['partner']:
                            partnership = 1
                        print('[+] V: {}\tF: {}\tP: {}\tN: {}'.format(
                            viewer_count,
                            follower_count,
                            partnership == 1,
                            streamer_name
                        ))
                        # api search isn't perfect despite filtering for E:D only
                        insert_data_into_db(database, streamer_name, viewer_count, follower_count, partnership)
                api_offset_count += 90
        pause(cycle_delay)

if __name__ == '__main__':
    main()
