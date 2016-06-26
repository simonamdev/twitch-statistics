import os
import datetime
from neopysqlite.neopysqlite import Pysqlite
from tqdm import tqdm


games = ['ED',  'PC']
for game in games:
    streamers = os.listdir(os.path.join(os.getcwd(), 'data', game, 'streamers'))
    streamers.remove('base')
    print('Processing timestamps for streamers of game: {}'.format(game))
    for streamer in tqdm(streamers):
        streamer_db_path = os.path.join(os.getcwd(), 'data', game, 'streamers', streamer)
        db = Pysqlite(database_name='{} DB'.format(streamer), database_file=streamer_db_path)
        table_count = len(db.get_table_names()) - 3
        # print('{} has {} stream tables'.format(streamer, table_count))
        for number in range(0, table_count):
            table_name = 'stream_{}'.format(number)
            rows = db.get_all_rows(table=table_name)
            for row in rows:
                old_timestamp = row[1]
                split_string = old_timestamp.split(' ')
                date_part = split_string[0].split('-')
                time_part = split_string[1].split(':')
                year, month, day = int(date_part[0]), int(date_part[1]), int(date_part[2])
                hour, minute, second = int(time_part[0]), int(time_part[1]), int(time_part[2])
                try:
                    datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
                except ValueError:
                    year, month, day = int(date_part[2]), int(date_part[1]), int(date_part[0])
                    datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
                new_timestamp = '{}-{}-{} {}:{}:{}'.format(day, month, year, hour, minute, second)
                # print(new_timestamp)
                db.dbcur.execute('UPDATE {} SET timestamp = ? WHERE timestamp = ?'.format(table_name), (new_timestamp, old_timestamp))
        db.dbcon.commit()
    # game_db_path = os.path.join(os.getcwd(), 'data', game, '{}_data.db'.format(game))
    # db = Pysqlite(database_name='{} DB'.format(game), database_file=game_db_path)
