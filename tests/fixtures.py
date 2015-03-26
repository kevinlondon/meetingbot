import pytest


@pytest.fixture
def room_calendar():
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
def attendees():
    return [
        {
            u'displayName': u'Some Guy',
            u'email': u'dude@wiredrive.com',
            u'responseStatus': u'accepted'
        }, {
            u'organizer': True,
            u'displayName': u'Kevin London',
            u'email': u'kevinlondon@gmail.com',
            u'responseStatus': u'accepted'
        }, {
            u'resource': True,
            u'self': True,
            u'displayName': u'Small Conference Room',
            u'email': u'foo-email@resource.calendar.google.com',
            u'responseStatus': u'accepted'
        }


@pytest.fixture
def room_event(attendees):
    meeting_description = (u'What did I accomplish?\nJoin this.\n'
                           u'https://www4.gotomeeting.com/join/MEETING_ID\n')
    return {
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
