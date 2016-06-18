import db_access
from flask import Flask, render_template
from minify import minify as minify_css

app = Flask(__name__)

app_info = {
    'debug': True,
    'version': 'Alpha 0.1'
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


def convert_name(given_type, given_name, return_type):
    for name in game_names:
        if name[given_type] == given_name:
            return name[return_type]


def return_name_dict(name):
    for name_dict in game_names:
        if name in list(name_dict.values()):
            return name_dict


@app.route('/')
def index():
    return render_template('index.html', app_info=app_info)


@app.route('/about')
def about():
    return render_template('about.html', app_info=app_info)


@app.route('/games')
def games():
    return render_template('games.html', app_info=app_info, games=game_names)


@app.route('/game/<game_name>')
def game(game_name):
    name_dict = return_name_dict(name=game_name)
    global_game_data = db_access.GlobalGameData(game_url_name=name_dict['url'])
    return render_template('game.html',
                           app_info=app_info,
                           game_name=name_dict,
                           game_data=global_game_data.return_global_overview_dict())


@app.route('/streamers')
def streamers():
    return render_template('streamers.html', app_info=app_info, games=game_names)


@app.route('/streamers/<game_url_name>/<int:page_number>')
def streamers_list(game_url_name, page_number):
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


@app.route('/streamer/<streamer_name>')
def streamer(streamer_name):
    streamer_dict = {
        'name': streamer_name,
        'overviews': dict()
    }
    streamer_global_db = db_access.StreamerGlobalData(streamer_name=streamer_name)
    streamer_global_db.run()
    # update the streamer dict with the overviews for each game
    streamer_dict['overviews'] = streamer_global_db.get_all_overviews()
    return render_template('streamer.html',
                           app_info=app_info,
                           game_names=game_names,
                           streamer=streamer_dict)


if __name__ == '__main__':
    if not app_info['debug']:
        minify_css()
    app.run(host='127.0.0.1', port=9000, debug=app_info['debug'])
    # app.run(host='0.0.0.0', port=9000, debug=debug_mode)
