import requests


class APIStreamsRequest:
    def __init__(self, game_url_name, timeout=10, verbose=False):
        self.game_url_name = game_url_name
        self.json_url = 'https://api.twitch.tv/kraken/streams'
        self.timeout = timeout
        self.last_status_code = 0
        self.streams_data = []
        self.verbose = verbose

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

    def get_streams_data(self):
        return self.streams_data


def main():
    a = APIStreamsRequest(game_url_name='Elite:%20Dangerous', verbose=True)
    a.request_all_game_data()

if __name__ == '__main__':
    main()
