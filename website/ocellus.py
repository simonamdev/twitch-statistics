import db_access
from flask import Flask, render_template
from minify import minify as minify_css


app = Flask(__name__)

debug_mode = True
app_version = 'Alpha 0.1'
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


@app.route('/')
def index():
    return render_template('index.html', app_version=app_version, debug_mode=debug_mode)


@app.route('/about')
def about():
    return render_template('about.html', app_version=app_version, debug_mode=debug_mode)


@app.route('/games')
def games():
    return render_template('games.html', app_version=app_version, debug_mode=debug_mode, games=game_names)


@app.route('/game/<game_name>')
def game(game_name):
    # Get only the related dictionary
    name = [data for data in game_names if data['url'] == game_name][0]
    # get the data for this specific game from the DB
    data = dict()
    return render_template('game.html', app_version=app_version, debug_mode=debug_mode, game=name, data=data)


@app.route('/streamers')
def streamers():
    return render_template('streamers.html', app_version=app_version, debug_mode=debug_mode, games=game_names)


@app.route('/streamers/<game_url_name>/<int:page_number>')
def streamers_list(game_url_name, page_number):
    # id the page number requested is less than 1, then return 1
    if page_number < 1:
        page_number = 1
    # get access to the database through an object which will take care of pagination
    overview_access = db_access.OverviewsDataPagination(
            game_name=convert_name(given_type='url', given_name=game_url_name, return_type='short'),
            per_page=10)
    overview_access.run()
    # if the page number requested is greater than the last page number, then return the last page
    if page_number > overview_access.get_page_count():
        page_number = overview_access.get_page_count()
    overviews = overview_access.get_page(page_number)
    return render_template('streamer_list.html',
                           app_version=app_version,
                           debug_mode=debug_mode,
                           game_url_name=game_url_name,
                           game_name=convert_name(given_type='url', given_name=game_url_name, return_type='full'),
                           streamer_data=overviews,
                           per_page=10,
                           page_number=page_number,
                           page_total=overview_access.get_page_count())


if __name__ == '__main__':
    if not debug_mode:
        minify_css()
    app.run(host='127.0.0.1', port=9000, debug=debug_mode)
    # app.run(host='0.0.0.0', port=9000, debug=debug_mode)
