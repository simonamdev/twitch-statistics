import db_access
import logging
import time
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect
from minify import minify as minify_css
from time import time as current_time_epoch

app = Flask(__name__)

app_info = {
    'debug': True,
    'version': 'Alpha 0.2'
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


def log_page_visit(route_name='', parameters='none'):
    app.logger.info('{}|{}|{}|{}'.format(
        int(time.time()),
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


@app.route('/games')
def games():
    log_page_visit('games')
    return render_template('games.html', games=game_names)


@app.route('/game/<game_name>')
def game(game_name):
    log_page_visit('game', game_name)
    name_dict = return_name_dict(name=game_name)
    global_game_data = db_access.GameGlobalData(game_url_name=name_dict['url'])
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
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1
    log_page_visit('streamers_list', '{},{}'.format(game_url_name, page_number))
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
    return render_template('streamer_list.html',
                           app_info=app_info,
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
    log_page_visit('streamer', streamer_name)
    games_streamed_dict = db_access.DetermineIfStreamed(streamer_name=streamer_name).check_for_all_games()
    streamer_dict = {
        'name': streamer_name,
        'overviews': dict()
    }
    streamer_dict.update(games_streamed_dict)
    streamer_global_db = db_access.StreamerGlobalData(streamer_name=streamer_name)
    streamer_global_db.run()
    # update the streamer dict with the overviews for each game
    streamer_dict['overviews'] = streamer_global_db.get_all_overviews()
    print(game_names)
    return render_template('streamer.html',
                           app_info=app_info,
                           game_names=game_names_dict,
                           streamer=streamer_dict)


@app.route('/streamer/<streamer_name>/<game_url_name>/streams/')
@app.route('/streamer/<streamer_name>/<game_url_name>/streams/<page_number>')
def streams(streamer_name, game_url_name, page_number=1):
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1
    log_page_visit('streams', '{},{},{}'.format(streamer_name, game_url_name, page_number))
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
    return render_template('streams.html',
                           app_info=app_info,
                           game_name=return_name_dict(name=game_url_name),
                           streamer_name=streamer_name,
                           streams_overviews=streams_overviews_dicts,
                           page_data=page_data)


@app.route('/streamer/<streamer_name>/<game_url_name>/stream/')
@app.route('/streamer/<streamer_name>/<game_url_name>/stream/<stream_id>')
def stream(streamer_name, game_url_name, stream_id=1):
    log_page_visit('stream', '{},{},{}'.format(streamer_name, game_url_name, stream_id))
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
    return render_template('stream.html',
                           app_info=app_info,
                           game_name=return_name_dict(name=game_url_name),
                           streamer_name=streamer_name,
                           stream_data=stream_data_dict)


@app.route('/api/v1/raw_stream_data/<streamer_name>/<game_short_name>/<stream_id>')
def api_raw_stream_data(streamer_name, game_short_name, stream_id):
    log_page_visit('stream_api', '{},{},{}'.format(streamer_name, game_short_name, stream_id))
    stream_db_access = db_access.StreamData(streamer_name=streamer_name, game_name=game_short_name, stream_id=stream_id)
    stream_db_access.run()
    return stream_db_access.get_stream_viewer_data_json()


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
