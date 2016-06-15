import requests


class APIRequest:
    def __init__(self, game_url_name, timeout=10):
        self.game_url_name = game_url_name
        self.json_url = 'https://api.twitch.tv/kraken/streams'
        self.timeout = timeout

    def get_game_data(self):
        # url = self.json_url + '?game=' + self.game_url_name
        try:
            game_data = requests.get(url=self.json_url, params={'game': self.game_url_name})
            print(game_data)
        except Exception as e:
            print(e)


def main():
    a = APIRequest(game_url_name='Elite:%20Dangerous')
    a.get_game_data()

if __name__ == '__main__':
    main()
