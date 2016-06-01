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


@app.route('/streamers/<game_name>')
def streamers_game(game_name):
    pass


if __name__ == '__main__':
    if not debug_mode:
        minify_css()
    app.run(host='127.0.0.1', port=9000, debug=debug_mode)
    # app.run(host='0.0.0.0', port=9000, debug=debug_mode)
