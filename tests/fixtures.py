import pytest
from meetingbot.gcal import Calendar, Event


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


@pytest.fixture
def event(attendees):
    meeting_description = (u'What did I accomplish?\nJoin this.\n'
                           u'https://www4.gotomeeting.com/join/MEETING_ID\n')
    data = {
        u'status': u'confirmed',
        u'kind': u'calendar#event',
        u'end': {u'dateTime': u'2015-03-26T10:00:00-07:00'},
        u'description': meeting_description,
        u'created': u'2014-12-01T17:35:56.000Z',
        u'iCalUID': u'something@google.com',
        u'reminders': {u'useDefault': True},
        u'htmlLink': u'https://www.google.com/calendar/event?eid=foo',
        u'sequence': 0,
        u'updated': u'2015-03-23T17:07:38.562Z',
        u'summary': u'Daily Event',
        u'start': {u'dateTime': u'2015-03-26T09:45:00-07:00'},
        u'etag': u'"2854260917124000"',
        u'originalStartTime': {u'dateTime': u'2015-03-26T09:45:00-07:00'},
        u'location': u'Small Conference Room',
        u'recurringEventId': u're-id',
        u'attendees': attendees,
        u'organizer': {u'displayName': u'Kevin', u'email': u'foo@foo.com'},
        u'creator': {u'displayName': u'Kevin', u'email': u'foo@foo.com'},
        u'id': u'eventid', u'hangoutLink': u'https://plus.google.com/link'
    }
    return Event(data=data)


@pytest.fixture
def organizer():
    return {
        u'organizer': True,
        u'displayName': u'Kevin London',
        u'email': u'kevinlondon@gmail.com',
        u'responseStatus': u'accepted'
    }


@pytest.fixture
def room():
    return {
        u'resource': True,
        u'self': True,
        u'displayName': u'Small Conference Room',
        u'email': u'foo-email@resource.calendar.google.com',
        u'responseStatus': u'accepted'
    }


@pytest.fixture
def attendees(room, organizer):
    return [room, organizer]



@pytest.fixture
def hipchat_users():
    return {
        'links': {'self': 'https://api.hipchat.com/v2/user'},
        'maxResults': 100,
        'startIndex': 0,
        'items': [
            {
                'id': 11111,
                'links': {'self': 'https://api.hipchat.com/v2/user/11111'},
                'mention_name': 'Foo',
                'name': 'Foo Lee'
            }, {
                'id': 22222,
                'links': {'self': 'https://api.hipchat.com/v2/user/22222'},
                'mention_name': 'Kevin',
                'name': 'Kevin London'
            }
        ]
    }


