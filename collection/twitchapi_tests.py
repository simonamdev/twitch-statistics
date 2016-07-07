import pytest
import twitchapi  # ignore PyCharm error here


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

