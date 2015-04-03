import pytest
import copy
from mock import Mock
from meetingbot import bot

from .fixtures import calendar_data


def test_get_useful_calendars(calendar_data):
    expected_calendar = calendar_data
    unexpected_calendar = copy.deepcopy(calendar_data)
    unexpected_calendar['summary'] = "Foo Bar"
    calendar_list = {"items": [expected_calendar, unexpected_calendar]}

    useful_list = bot.get_useful_calendars(calendar_list)
    assert len(useful_list) == 1
    assert useful_list[0]._data == calendar_data
