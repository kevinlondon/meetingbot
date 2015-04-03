import pytest
from meetingbot.gcal import Calendar


@pytest.fixture
def calendar_data():
    return {
        u'kind': u'calendar#calendarListEntry',
        u'foregroundColor': u'#000000',
        u'defaultReminders': [],
        u'colorId': u'5',
        u'selected': True,
        u'summary': u'Small Conference Room',
        u'etag': u'"1427261373011000"',
        u'backgroundColor': u'#ff7537',
        u'timeZone': u'America/Los_Angeles',
        u'accessRole': u'writer',
        u'id': u'somenumbers@resource.calendar.google.com'
    }


@pytest.fixture
def calendar(calendar_data):
    return Calendar(data=calendar_data)
