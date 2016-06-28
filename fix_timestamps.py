import os
import datetime
from neopysqlite.neopysqlite import Pysqlite
from tqdm import tqdm


fix_stream_tables = True
fix_game_tables = True

games = ['ED',  'PC']
for game in games:
    streamers = os.listdir(os.path.join(os.getcwd(), 'data', game, 'streamers'))
    streamers.remove('base')
    print('Processing timestamps for streamers of game: {}'.format(game))
    if fix_stream_tables:
        for streamer in tqdm(streamers):
            streamer_db_path = os.path.join(os.getcwd(), 'data', game, 'streamers', streamer)
            db = Pysqlite(database_name='{} DB'.format(streamer), database_file=streamer_db_path)
            table_count = len(db.get_table_names()) - 3
            # print('{} has {} stream tables'.format(streamer, table_count))
            table_names = ['stream_{}'.format(number) for number in range(0, table_count)]
            table_names.append('overview')
            table_names.append('streams')
            for table_name in table_names:
                rows = db.get_all_rows(table=table_name)
                for row in tqdm(rows):
                    # convert anything in DD_MM_YYYY HH:MM:SS to YYYY_MM_DD HH:MM:SS
                    old_timestamp = row[1]
                    split_string = old_timestamp.split(' ')
                    date_part = split_string[0].split('-')
                    time_part = split_string[1].split(':')
                    year, month, day = int(date_part[0]), int(date_part[1]), int(date_part[2])
                    hour, minute, second = int(time_part[0]), int(time_part[1]), int(time_part[2])
                    if day == 2016:
                        day, month, year = int(date_part[0]), int(date_part[1]), int(date_part[2])
                        new_timestamp = '{}-{}-{} {}:{}:{}'.format(year, month, day, hour, minute, second)
                        # print(new_timestamp)
                        db.dbcur.execute('UPDATE {} SET timestamp = ? WHERE timestamp = ?'.format(table_name),
                                         (new_timestamp, old_timestamp))
            db.dbcon.commit()
            db.execute_sql('VACUUM')
            db.dbcon.commit()
    if fix_game_tables:
        game_db_path = os.path.join(os.getcwd(), 'data', game, '{}_data.db'.format(game))
        db = Pysqlite(database_name='{} DB'.format(game), database_file=game_db_path)
        rows = db.get_all_rows(table='global_data')
        print('Processing timestamps for global data')
        for row in tqdm(rows):
            # convert anything in DD_MM_YYYY HH:MM:SS to YYYY_MM_DD HH:MM:SS
            old_timestamp = row[1]
            split_string = old_timestamp.split(' ')
            date_part = split_string[0].split('-')
            time_part = split_string[1].split(':')
            year, month, day = int(date_part[0]), int(date_part[1]), int(date_part[2])
            hour, minute, second = int(time_part[0]), int(time_part[1]), int(time_part[2])
            if day == 2016:
                day, month, year = int(date_part[0]), int(date_part[1]), int(date_part[2])
                new_timestamp = '{}-{}-{} {}:{}:{}'.format(year, month, day, hour, minute, second)
                # print(new_timestamp)
                db.dbcur.execute('UPDATE global_data SET timestamp = ? WHERE timestamp = ?',
                                 (new_timestamp, old_timestamp))
        print('Processing timestamps for streamers data')
        rows = db.get_all_rows(table='streamers_data')
        for row in tqdm(rows):
            # convert anything in DD_MM_YYYY HH:MM:SS to YYYY_MM_DD HH:MM:SS
            old_timestamp = row[2]
            split_string = old_timestamp.split(' ')
            date_part = split_string[0].split('-')
            time_part = split_string[1].split(':')
            year, month, day = int(date_part[0]), int(date_part[1]), int(date_part[2])
            hour, minute, second = int(time_part[0]), int(time_part[1]), int(time_part[2])
            if day == 2016:
                day, month, year = int(date_part[0]), int(date_part[1]), int(date_part[2])
                new_timestamp = '{}-{}-{} {}:{}:{}'.format(year, month, day, hour, minute, second)
                # print(new_timestamp)
                db.dbcur.execute('UPDATE streamers_data SET timestamp = ? WHERE timestamp = ?',
                                 (new_timestamp, old_timestamp))
        db.dbcon.commit()
        db.execute_sql('VACUUM')
        db.dbcon.commit()
