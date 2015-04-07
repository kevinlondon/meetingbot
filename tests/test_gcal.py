import copy
import pytest
import arrow
from datetime import timedelta
from mock import patch, Mock
from meetingbot import gcal
from meetingbot.gcal import Event, Calendar, User
from meetingbot.meetings import GoToMeeting

from .fixtures import (calendar, calendar_data, organizer, room, event,
    hipchat_users, attendees)


class TestHipchat:

    @patch.object(gcal, "HypChat")
    def test_hipchat_user_call_returns_users(self, hc_mock):
        hc_mock().users = Mock(return_value={"items": "foo"})
        users = gcal.get_hipchat_users()
        assert hc_mock().users.called
        assert users == "foo"


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
