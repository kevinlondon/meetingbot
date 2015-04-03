import copy
import pytest
import arrow
from datetime import timedelta
from mock import patch, Mock
from meetingbot import gcal
from meetingbot.gcal import Event, GoToMeeting, Calendar, User

from .fixtures import calendar, calendar_data


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


class TestCalendar:

    def test_next_event_pulls_first_event_not_ended(self, calendar, event):
        later_event = Event(data=event._data)
        later_event.start = later_event.start.replace(hours=+1)
        later_event.end = later_event.end.replace(hours=+1)
        calendar.events = [event, later_event]
        past_event_end = event.end.replace(minutes=+5)
        with patch.object(arrow, "utcnow", return_value=past_event_end):
            assert calendar.next_event == later_event

    def test_next_event_returns_none_when_no_valid_events(self, calendar):
        assert calendar.next_event is None

    @patch.object(Event, "countdown", return_value="foo countdown")
    def test_countdown_uses_start_before(self, cd_mock, calendar, event):
        two_min_before_start = event.start.replace(minutes=-2)
        calendar.events = [event, ]
        with patch.object(arrow, "utcnow", return_value=two_min_before_start):
            countdown = calendar.countdown()
            assert calendar.summary in countdown
            assert "foo countdown" in countdown

    def test_countdown_with_no_events_has_different_message(self, calendar):
        assert "No events" in calendar.countdown()

    def test_get_events_loads_events(self, calendar, event):
        events = {"items": [event._data, ]}

        class MockService:
            def events(self):
                return self

            def list(self, *args, **kwargs):
                return self

            def execute(self):
                return events

        calendar.get_events(calendar_service=MockService())
        assert len(calendar._events) == 1


class TestEvents:

    def test_event_parses_go_to_meeting(self, event):
        assert isinstance(event.go_to_meeting, GoToMeeting)

    def test_room_without_go_to_meeting_has_no_object(self, event):
        event.description = ""
        assert event.go_to_meeting is None

    def test_assert_time_until_start_calculates_delta(self, event):
        hours_before = event.start.replace(hours=-2)
        with patch.object(arrow, "now", return_value=hours_before):
            assert event.time_until_start == timedelta(hours=2)

    def test_assert_time_until_end_calculates_delta(self, event):
        minutes_before = event.end.replace(minutes=-10)
        with patch.object(arrow, "now", return_value=minutes_before):
            assert event.time_until_end == timedelta(minutes=10)

    def test_countdown_before_start_returns_countdown_to_start(self, event):
        event.start = arrow.utcnow().replace(minutes=+5, seconds=+1)
        countdown = event.countdown()
        expected = "00:05:00 until the start of {0}".format(event.summary)
        assert countdown == expected

    def test_countdown_after_start_returns_countdown_to_end(self, event):
        event.end = arrow.utcnow().replace(minutes=+5, seconds=+1)
        countdown = event.countdown()
        expected = "00:05:00 until the end of {0}".format(event.summary)
        assert countdown == expected

    def test_send_message_to_user_uses_hipchat(self, organizer, event):
        user = User(data=organizer)
        user.send_message = Mock()
        event._attendees = [user, ]
        event.notify()
        assert user.send_message.called
        assert event.notified_attendees is True

    def test_should_notify_fires_when_time_and_not_notified(self, event):
        event.start = arrow.utcnow().replace(minutes=+4)
        assert event.should_notify is True

    def test_should_notify_is_false_when_already_notified(self, event):
        event.start = arrow.utcnow().replace(minutes=+4)
        event.notified_attendees = True
        assert event.should_notify is False

    def test_should_notify_is_false_when_too_far_from_start(self, event):
        event.start = arrow.utcnow().replace(hours=+2)
        event.notified_attendees = False
        assert event.should_notify is False


class TestUser:

    @pytest.fixture
    def user(self, organizer):
        return User(data=organizer)

    def test_user_stores_data(self, organizer, user):
        assert user._data == organizer

    def test_user_name_is_str_repr(self, user):
        assert "{0}".format(user) == user.name

    def test_send_message_uses_hipchat(self, user):
        msg = "foo"
        user._hipchat = Mock()
        user.send_message(msg)
        user._hipchat.message.assert_called_with(msg, notify=True)
        assert user._hipchat.message.called

    def test_in_hipchat_property_gets_hipchat_user(self, user):
        assert user._hipchat is None
        expected_user = {"name": "hi"}
        user.find_in_hipchat = Mock(return_value=expected_user)
        assert user.in_hipchat == expected_user

    def test_send_hipchat_message_does_not_fail_without_user(self, user):
        user._hipchat = {"foo": "thing"}
        try:
            user.send_message("hi")
        except:
            # Should not happen
            raise

    def test_find_in_hipchat_matches_on_exact_name(self, user, hipchat_users):
        users = hipchat_users['items']
        expected_user = users[1]
        with patch.object(gcal, "get_hipchat_users", return_value=users):
            assert user.find_in_hipchat() == expected_user

    def test_find_matches_on_first_name_as_fallback(self, user, hipchat_users):
        users = hipchat_users['items']
        expected_user = users[0]
        # Just copy their first name
        user._data['displayName'] = expected_user['name'].split()[0]
        with patch.object(gcal, "get_hipchat_users", return_value=users):
            assert user.find_in_hipchat() == expected_user


class TestGoToMeeting:

    @pytest.fixture
    def gotomeeting(self, event):
        return GoToMeeting(event.description)

    def test_can_pull_meeting_id_from_description(self, gotomeeting):
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

    def test_join_instructions(self, gotomeeting):
        assert gotomeeting.url in gotomeeting.join_instructions
