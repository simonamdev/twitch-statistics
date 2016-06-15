import requests


class APIStreamsRequest:
    def __init__(self, game_url_name, timeout=10, verbose=False):
        self.game_url_name = game_url_name
        self.json_url = 'https://api.twitch.tv/kraken/streams'
        self.timeout = timeout
        self.status_code = 0
        self.streams_data = None
        self.verbose = verbose

    def print(self, string=''):
        if self.verbose:
            print(string)

    def get_game_data(self, url=''):
        if url == '':
            self.print('[ERROR] No URL passed!')
            return None
        # url = self.json_url + '?game=' + self.game_url_name
        self.print('[INFO] Sending a request to: {}'.format(url))
        try:
            response = requests.get(url=url)
        except Exception as e:
            self.print('Encountered an exception:')
            print(e)
            return None
        self.status_code = response.status_code
        self.print('[INFO] Status code returned: {}'.format(self.status_code))
        self.streams_data = response.json()['streams']

    def get_streams_data(self):
        return self.streams_data


def main():
    a = APIStreamsRequest(game_url_name='Elite:%20Dangerous')
    a.get_game_data()
    print(a.get_streams_data())

if __name__ == '__main__':
    main()
