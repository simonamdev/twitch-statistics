from os.path import isfile as file_exists


def is_production():
    if file_exists('.gitignore'):
        return True
    return False

ocellus_debug = is_production()

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

games_short_names = [
    name['short'] for name in game_names
]

games_url_names = [
    name['url'] for name in game_names
]

games_full_names = [
    name['full'] for name in game_names
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
