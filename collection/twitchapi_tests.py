import pytest
import twitchapi


# content of test_sample.py
class TestIllegalArguments:
    def test_no_game_name(self):
        with pytest.raises(twitchapi.IllegalArgumentError):
            api = twitchapi.APIStreamsRequest(game_proper_name='blabla')
        with pytest.raises(twitchapi.IllegalArgumentError):
            api = twitchapi.APIStreamsRequest(game_url_name='blabla')


class TestClass:
    def test_one(self):
        x = "this"
        assert 'h' in x

    #def test_two(self):
     #   x = "hello"
      #  assert hasattr(x, 'check')
