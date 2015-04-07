import pytest
from mock import Mock, patch

from meetingbot.meetings import GoToMeeting
from .fixtures import event, attendees, room, organizer


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
