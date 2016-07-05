import db_access
import logging
import time
import json
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect
from minify import minify as minify_css

app = Flask(__name__)

app_info = {
    'debug': True,
    'version': 'Alpha 0.3'
}

game_names = [
    {
        'short': 'ED',
        'url': 'elitedangerous',
        'full': 'Elite: Dangerous'
    },
    {
        'short': 'PC',
        'url': 'planetcoaster',
        'full': 'Planet Coaster'
    }
]

game_names_dict = {
    'ED': game_names[0],
    'PC': game_names[1]
}


# Required methods to deal with the game names
def convert_name(given_type, given_name, return_type):
    for name in game_names:
        if name[given_type] == given_name:
            return name[return_type]


def return_name_dict(name):
    for name_dict in game_names:
        if name in list(name_dict.values()):
            return name_dict


"""
Catch all method to log page visits
Logs the following:
    > current time in epoch format
    > time taken to serve the page (in seconds). If the page does not have a DB request, then the delta is 0
    > the remote IP Address
    > the route name of the page
    > any associated parameters with that route
"""


def log_page_visit(route_name='', parameters='none', start_time=0):
    if not start_time == 0:
        time_delta = time.time() - start_time
    else:
        time_delta = 0
    app.logger.info('{}|{}|{}|{}|{}'.format(
        int(time.time()),
        time_delta,
        request.environ['REMOTE_ADDR'],
        route_name,
        parameters
    ))


# Inject the application info into each template
@app.context_processor
def inject_app_info():
    return dict(ocellus_debug=app_info['debug'], ocellus_version=app_info['version'])


# Error handler route
@app.errorhandler(404)
def page_not_found(e):
    log_page_visit('error', '404')
    return render_template('error.html', error_code=404), 404


# Front facing routes
@app.route('/')
def index():
    log_page_visit('index')
    return render_template('index.html')


@app.route('/about')
def about():
    log_page_visit('about')
    return render_template('about.html')


@app.route('/about/news/')
@app.route('/about/news/<page_number>')
def news(page_number=1):
    access_time = time.time()
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1
    news_db_access = db_access.NewsArticlesPagination(per_page=4)
    news_db_access.run()
    news_articles = news_db_access.get_page(page_number=page_number)
    # TODO: Get pagination data from the database
    page_data = {
        'current': page_number,
        'per_page': 3,
        'total': news_db_access.get_page_count()
    }
    log_page_visit('news', start_time=access_time)
    return render_template('news.html',
                           news_articles=news_articles,
                           page_data=page_data)


@app.route('/games')
def games():
    log_page_visit('games')
    return render_template('games.html', games=game_names)


@app.route('/game/<game_name>')
def game(game_name):
    access_time = time.time()
    name_dict = return_name_dict(name=game_name)
    global_game_data = db_access.GameGlobalData(game_url_name=name_dict['url'])
    log_page_visit('game', game_name, start_time=access_time)
    return render_template('game.html',
                           app_info=app_info,
                           game_name=name_dict,
                           game_data=global_game_data.return_global_overview_dict())


@app.route('/streamers')
def streamers():
    log_page_visit('streamers')
    return render_template('streamers.html', games=game_names)


@app.route('/streamers/<game_url_name>/<int:page_number>')
def streamers_list(game_url_name, page_number=1):
    access_time = time.time()
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1
    # id the page number requested is less than 1, then return 1
    if page_number < 1:
        page_number = 1
    # get access to the database through an object which will take care of pagination
    overview_access = db_access.AllStreamerOverviewsDataPagination(
            game_name=convert_name(given_type='url', given_name=game_url_name, return_type='short'),
            per_page=10)
    overview_access.run()
    # get the overview data for that page
    streamer_overview_dicts = enumerate(overview_access.get_page(page_number))
    # get the game overview
    game_global_data = db_access.GameGlobalData(game_url_name=game_url_name)
    tier_bounds = game_global_data.return_tier_bounds()
    tier_counts = game_global_data.return_tier_counts()
    tier_streamers = game_global_data.return_tier_streamers()
    # if the page number requested is greater than the last page number, then return the last page
    if page_number > overview_access.get_page_count():
        page_number = overview_access.get_page_count()
    # put the page data in a dictionary
    page_data = {
        'current': page_number,
        'per_page': 10,
        'total': overview_access.get_page_count()
    }
    log_page_visit('streamers_list', '{},{}'.format(game_url_name, page_number), start_time=access_time)
    return render_template('streamer_list.html',
                           app_info=app_info,  # TODO: REMOVE THIS
                           game_name=return_name_dict(name=game_url_name),
                           streamer_overviews=streamer_overview_dicts,
                           tier_bounds=tier_bounds,
                           tier_counts=tier_counts,
                           tier_streamers=tier_streamers,
                           page_data=page_data)


@app.route('/streamer/')
def streamer_no_name():
    return redirect('streamers')


@app.route('/streamer/<streamer_name>')
def streamer(streamer_name):
    access_time = time.time()
    games_streamed_dict = db_access.DetermineIfStreamed(streamer_name=streamer_name).check_for_all_games()
    streamer_dict = {
        'name': streamer_name,
        'overviews': dict()
    }
    streamer_dict.update(games_streamed_dict)
    # If a streamer is listed, but there are no streams under the name, then redirect
    if not streamer_dict['ED'] and not streamer_dict['PC']:
        return redirect('page_not_found')
    streamer_global_db = db_access.StreamerGlobalData(streamer_name=streamer_name)
    streamer_global_db.run()
    # update the streamer dict with the overviews for each game
    streamer_dict['overviews'] = streamer_global_db.get_all_overviews()
    log_page_visit('streamer', streamer_name, start_time=access_time)
    return render_template('streamer.html',
                           app_info=app_info,
                           game_names=game_names_dict,
                           streamer=streamer_dict)


@app.route('/streamer/<streamer_name>/<game_url_name>/streams/')
@app.route('/streamer/<streamer_name>/<game_url_name>/streams/<page_number>')
def streams(streamer_name, game_url_name, page_number=1):
    access_time = time.time()
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1
    # id the page number requested is less than 1, then return 1
    if page_number < 1:
        page_number = 1
    # get access to the database through an object which will take care of pagination
    streams_access = db_access.StreamsDataPagination(
        game_name=convert_name(given_type='url', given_name=game_url_name, return_type='short'),
        streamer_name=streamer_name,
        per_page=10)
    streams_access.run()
    # get the streams data for that page
    streams_overviews_dicts = enumerate(streams_access.get_page(page_number))
    # if the page number requested is greater than the last page number, then return the last page
    if page_number > streams_access.get_page_count():
        page_number = streams_access.get_page_count()
    # put the page data in a dictionary
    page_data = {
        'current': page_number,
        'per_page': 10,
        'total': streams_access.get_page_count()
    }
    log_page_visit('streams', '{},{},{}'.format(streamer_name, game_url_name, page_number), start_time=access_time)
    return render_template('streams.html',
                           app_info=app_info,
                           game_name=return_name_dict(name=game_url_name),
                           streamer_name=streamer_name,
                           streams_overviews=streams_overviews_dicts,
                           page_data=page_data)


@app.route('/streamer/<streamer_name>/<game_url_name>/stream/')
@app.route('/streamer/<streamer_name>/<game_url_name>/stream/<stream_id>')
def stream(streamer_name, game_url_name, stream_id=1):
    access_time = time.time()
    try:
        stream_id = int(stream_id)
    except ValueError:
        stream_id = 1
    # get the stream data from the database
    stream_access = db_access.StreamData(
        game_name=convert_name(given_type='url', given_name=game_url_name, return_type='short'),
        streamer_name=streamer_name,
        stream_id=stream_id)
    stream_access.run()
    # get the data for that stream
    stream_data_dict = stream_access.get_stream_data()
    log_page_visit('stream', '{},{},{}'.format(streamer_name, game_url_name, stream_id), start_time=access_time)
    return render_template('stream.html',
                           app_info=app_info,
                           game_name=return_name_dict(name=game_url_name),
                           streamer_name=streamer_name,
                           stream_data=stream_data_dict)


# API Routes below here
@app.route('/api/v1/raw_stream_data/<streamer_name>/<game_short_name>/<stream_id>')
def api_raw_stream_data(streamer_name, game_short_name, stream_id):
    access_time = time.time()
    stream_db_access = db_access.StreamData(streamer_name=streamer_name, game_name=game_short_name, stream_id=stream_id)
    stream_db_access.run()
    data = stream_db_access.get_stream_viewer_data_json()
    log_page_visit('stream_api', '{},{},{}'.format(streamer_name, game_short_name, stream_id), start_time=access_time)
    return data


@app.route('/api/v1/streamer/<streamer_name>/')
def api_streamer_data(streamer_name):
    access_time = time.time()
    # first check which games the streamer has streamed to avoid polling a database needlessly
    games_streamed_dict = db_access.DetermineIfStreamed(streamer_name=streamer_name).check_for_all_games()
    streamer_global_db = db_access.StreamerGlobalData(streamer_name=streamer_name)
    streamer_global_db.run()
    streamer_graph_data = {'streamer_name': streamer_name}
    # add defaults to the dict for each known game
    for game in game_names:
        streamer_graph_data[game['short']] = {}
    for game_short_name, streamed in games_streamed_dict.items():
        if streamed:
            streams_db = db_access.StreamsDataPagination(game_name=game_short_name, streamer_name=streamer_name)
            streams_db.run()
            average_viewer_dicts = streams_db.get_average_viewer_count_dicts()
            follower_count_dicts = streamer_global_db.get_follower_counts(game_short_name=game_short_name)
            streamer_graph_data[game_short_name] = {
                'viewers_average': [
                    [row['start_time'], row['viewers_average']]for row in average_viewer_dicts
                ],
                'followers': [
                    [row['update_time'], row['followers']] for row in follower_count_dicts
                ]
            }
    log_page_visit('streamer_api', streamer_name, start_time=access_time)
    return json.dumps(streamer_graph_data)


if __name__ == '__main__':
    handler = RotatingFileHandler('application.log', maxBytes=100000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    if not app_info['debug']:
        minify_css()
    app.run(host='127.0.0.1', port=9000, debug=app_info['debug'])
    # app.run(host='0.0.0.0', port=9000, debug=debug_mode)

"""
Logging references:
    https://stackoverflow.com/questions/3759981/get-ip-address-of-visitors-using-python-flask
    https://gist.github.com/ibeex/3257877
"""
