import requests
from datetime import datetime


class APIStreamsRequest:
    def __init__(self, game_url_name, game_full_names, client_id, timeout=10, verbose=False):
        self.game_url_name = game_url_name
        self.game_full_names = game_full_names
        self.client_id = client_id
        self.json_url = 'https://api.twitch.tv/kraken/streams'
        self.timeout = timeout
        self.last_status_code = 0
        self.streams_data = []
        self.verbose = verbose

    def print(self, string=''):
        if self.verbose:
            print(string)

    def make_request(self, url):
        self.print('[INFO] Sending a request to: {}'.format(url))
        try:
            response = requests.get(
                url=url,
                timeout=self.timeout,
                headers={'Client-ID': self.client_id})
        except Exception as e:
            # TODO: Don't return None :(
            return None
        self.last_status_code = response.status_code
        self.print('[INFO] Status code returned: {}'.format(self.last_status_code))
        # try to parse the JSON
        try:
            json_data = response.json()
        except Exception as e:
            self.print('Unable to parse JSON:')
            print(e)
            return None
        return json_data

    def last_request_successful(self):
        return self.last_status_code == 200

    def request_all_game_data(self):
        url = self.json_url + '?game=' + self.game_url_name
        response_data = self.make_request(url=url)
        if response_data is None:
            raise Exception('No data returned in the request')
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
                datetime.now().year,
                datetime.now().month,
                datetime.now().day,
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
             ) for stream in self.streams_data if stream['game'] in self.game_full_names
        ]
