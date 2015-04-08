import pytest
from mock import patch
from pubsub import pub
from meetingbot import lights


class TestLittleBits:

    @patch.object(lights, "change_littlebits_power")
    def test_subscription_calls_change_lights(self, littlebits_mock):
        pub.subscribe(lights.change_light, "meeting_light")
        pub.sendMessage("meeting_light", color="red")
        littlebits_mock.assert_called_with(lights.COLORS['red'])

    def test_invalid_color_raises_value_error(self):
        with pytest.raises(ValueError):
            lights.change_light(color="black")
