import requests
from datetime import datetime


class IllegalArgumentError(ValueError):
    pass


class APIStreamsRequest:
    def __init__(self, game_url_name=None, game_proper_name=None, timeout=10, verbose=False):
        self.game_url_name = game_url_name
        self.game_proper_name = game_proper_name
        self.json_url = 'https://api.twitch.tv/kraken/streams'
        self.timeout = timeout
        self.last_status_code = 0
        self.streams_data = []
        self.verbose = verbose
        self.verify_parameters()

    def verify_parameters(self):
        if self.game_url_name is None:
            raise IllegalArgumentError('Game URL name must be provided')
        if self.game_proper_name is None:
            raise IllegalArgumentError('Game proper name must be provided')

    def print(self, string=''):
        if self.verbose:
            print(string)

    def make_request(self, url=''):
        if url == '':
            self.print('[ERROR] No URL passed!')
            return None
        # url = self.json_url + '?game=' + self.game_url_name
        self.print('[INFO] Sending a request to: {}'.format(url))
        try:
            response = requests.get(url=url, timeout=self.timeout)
        except Exception as e:
            self.print('Encountered an exception:')
            print(e)
            return None
        self.last_status_code = response.status_code
        self.print('[INFO] Status code returned: {}'.format(self.last_status_code))
        return response.json()

    def request_all_game_data(self):
        url = self.json_url + '?game=' + self.game_url_name
        response_data = self.make_request(url=url)
        streams_data = response_data['streams']
        link_to_next = response_data['_links']['next']
        while not len(streams_data) == 0:
            self.streams_data.extend(streams_data)
            response_data = self.make_request(url=link_to_next)
            if response_data is not None and self.last_status_code == 200:
                streams_data = response_data['streams']
                link_to_next = response_data['_links']['next']
        """
        # Easy way to check whether the total count and the stream amount received match up
        print(response_data['_total'])
        print(len(self.streams_data))
        """

    def return_streams_data(self):
        return self.streams_data

    def clear_streams_data(self):
        self.streams_data = []

    def return_required_data(self):
        if not self.streams_data:
            self.print('[ERROR] No data is present. Have you requested the data yet?')
            return None
        # create a timestamp string for now
        timestamp = '{}-{}-{} {}:{}:{}'.format(
                datetime.now().day,
                datetime.now().month,
                datetime.now().year,
                datetime.now().hour,
                datetime.now().minute,
                datetime.now().second
        )
        return [(
                    stream['channel']['name'],
                    stream['viewers'],
                    stream['channel']['followers'],
                    1 if stream['channel']['partner'] else 0,  # 1 if true, 0 if false
                    timestamp
             ) for stream in self.streams_data if stream['game'] == self.game_proper_name
        ]


def main():
    a = APIStreamsRequest(game_url_name='Elite:%20Dangerous', game_proper_name='Elite: Dangerous', verbose=True)
    a.request_all_game_data()
    print(a.return_required_data())

if __name__ == '__main__':
    main()
