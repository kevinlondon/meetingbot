import pytest
import arrow
from datetime import timedelta
from mock import patch
from room_indicator.gcal import Event, GoToMeeting


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
def organizer_attendee():
    {
        u'organizer': True,
        u'displayName': u'Kevin London',
        u'email': u'kevinlondon@gmail.com',
        u'responseStatus': u'accepted'
    }


@pytest.fixture
def room_attendee():
    {
        u'resource': True,
        u'self': True,
        u'displayName': u'Small Conference Room',
        u'email': u'foo-email@resource.calendar.google.com',
        u'responseStatus': u'accepted'
    }


@pytest.fixture
def attendees(room_attendee, organizer_attendee):
    return [room_attendee, organizer_attendee]


@pytest.fixture
def room_event(attendees):
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


class TestEvents:

    def test_room_event_parses_go_to_meeting(self, room_event):
        assert isinstance(room_event.go_to_meeting, GoToMeeting)

    def test_room_without_go_to_meeting_has_no_object(self, room_event):
        room_event.description = ""
        assert room_event.go_to_meeting is None

    def test_assert_time_until_start_calculates_delta(self, room_event):
        hours_before = room_event.start.replace(hours=-2)
        with patch.object(arrow, "now", return_value=hours_before):
            assert room_event.time_until_start == timedelta(hours=2)

    def test_assert_time_until_end_calculates_delta(self, room_event):
        minutes_before = room_event.end.replace(minutes=-10)
        with patch.object(arrow, "now", return_value=minutes_before):
            assert room_event.time_until_end == timedelta(minutes=10)


class TestGoToMeeting:

    def test_can_pull_meeting_id_from_description(self, room_event):
        gotomeeting = GoToMeeting(room_event.description)
        assert gotomeeting.id == "MEETING_ID"

    def test_link_ends_with_id(self):
        gotomeeting = GoToMeeting(meeting_description="")
        fake_id = "foo"
        gotomeeting._id = fake_id
        assert gotomeeting.url.endswith(fake_id)

    @patch("webbrowser.open")
    def test_opening_link_includes_url(self, open_browser_mock):
        gtm = GoToMeeting("")
        gtm._id = "foo"
        gtm.join()
        open_browser_mock.assert_called_once_with(gtm.url)
