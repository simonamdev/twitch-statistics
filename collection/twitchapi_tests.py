import pytest
import twitchapi  # ignore PyCharm error here
from datetime import datetime


class TestIllegalArguments:
    def test_no_game_name(self):
        with pytest.raises(twitchapi.IllegalArgumentError):
            api = twitchapi.APIStreamsRequest(game_proper_name='blabla')
        with pytest.raises(twitchapi.IllegalArgumentError):
            api = twitchapi.APIStreamsRequest(game_url_name='blabla')


class TestRequestGameData:
    def test_ed_request(self):
        api = twitchapi.APIStreamsRequest(
            game_url_name='Elite:%20Dangerous',
            game_proper_name='Elite: Dangerous',
            verbose=True)
        data = api.make_request(url='https://api.twitch.tv/kraken/streams?game=Elite:%20Dangerous')
        assert len(data) > 0

    def test_ed_all_request(self):
        api = twitchapi.APIStreamsRequest(
            game_url_name='Elite:%20Dangerous',
            game_proper_name='Elite: Dangerous',
            verbose=True)
        api.request_all_game_data()
        assert len(api.return_streams_data()) > 0
        data = api.return_required_data()
        now_timestamp = data[0][4]  # get the first timestamp
        # split the timestamp up
        date_part = now_timestamp.split(' ')[0].split('-')
        day_array = [int(date_part[0]), int(date_part[1]), int(date_part[2])]
        assert day_array == [datetime.now().year, datetime.now().month, datetime.now().day]


