import os
import datetime
from operator import attrgetter
from collections import deque
import functools

import webbrowser
from hypchat import HypChat

import arrow


def memoize(obj):
    # from https://wiki.python.org/moin/PythonDecoratorLibrary
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer


def get_hipchat_users():
    keypath = os.path.join(os.path.dirname(__file__), "hipchat.key")
    with open(keypath, 'r') as hc_file:
        key = hc_file.read().rstrip("\n")

    raw_users = HypChat(key).users()
    return raw_users['items']


def format_timedelta(tdelta):
    """Return the timedelta as a 'HH:mm:ss' string."""
    total_seconds = int(tdelta.total_seconds())
    hours, remainder = divmod(total_seconds, 60*60)
    minutes, seconds = divmod(remainder, 60)
    return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)


class Calendar(object):

    ATTRIBUTES = ['id', 'summary']

    def __init__(self, data):
        self._data = data
        self._assign_attributes()
        self._events = None

    def _assign_attributes(self):
        self.id = self._data['id']
        self.summary = self._data['summary']

    @property
    def events(self):
        while self._events and self._events[0].end < arrow.utcnow():
            # Remove any events that have already past.
            self._events.popleft()

        return self._events

    @events.setter
    def events(self, event_list):
        self._events = deque(sorted(event_list, key=attrgetter('start')))

    @property
    def next_event(self):
        try:
            return self.events[0]
        except (IndexError, TypeError):
            return None

    def countdown(self):
        if self.next_event:
            return "{0}: {1}".format(self.summary, self.next_event.countdown())
        else:
            return "{0}: No events coming up.".format(self.summary)

    def get_events(self, calendar_service, days=1):
        now = arrow.now()
        tomorrow = arrow.now().replace(days=+days)

        events = calendar_service.events().list(
            calendarId=self.id,
            timeMin=str(now),
            timeMax=str(tomorrow),
            showDeleted=False,
            singleEvents=True,
        ).execute()

        self.events = [Event(data) for data in events['items']
                       if 'start' in data]


class Event(object):

    ATTRIBUTES = ['id', 'status', 'summary', 'description']
    DATETIMES = ['start', 'end']

    def __init__(self, data):
        self._data = data
        self._assign_attributes()
        self._meeting = None
        self.notified_attendees = False
        self._room = None

    def __repr__(self):
        return "{0} - {1}\t{2}".format(self.start, self.end, self.summary)

    def _assign_attributes(self):
        self._assign_datetimes()
        self.attendees = self._data['attendees']
        for attribute in self.ATTRIBUTES:
            value = self._data.get(attribute, "")
            setattr(self, attribute, value)

    def _assign_datetimes(self):
        for datetime_attr in self.DATETIMES:
            raw_dt = self._data[datetime_attr]['dateTime']
            setattr(self, datetime_attr, arrow.get(raw_dt))

    @property
    def attendees(self):
        return self._attendees

    @attendees.setter
    def attendees(self, attendee_list):
        self._attendees = [User(data=data) for data in attendee_list
                           if "Room" not in data['displayName']]

    @property
    def room(self):
        if not self._room:
            rooms = [data for data in self._data['attendees']
                     if 'Room' in data['displayName']]
            self._room = rooms[0]['displayName']

        return self._room

    @property
    def time_until_start(self):
        return self.start - arrow.now()

    @property
    def time_until_end(self):
        return self.end - arrow.now()

    @property
    def go_to_meeting(self):
        if not self._meeting and "gotomeeting" in self.description:
            self._meeting = GoToMeeting(self.description)

        return self._meeting

    @property
    def should_notify(self):
        NOTIFY_WINDOW = datetime.timedelta(minutes=5)
        time_until = self.start - arrow.utcnow()
        if time_until < NOTIFY_WINDOW and self.notified_attendees is False:
            return True
        else:
            return False

    def show(self):
        print(self.summary)
        print("* {0} - {1}".format(self.start, self.end))
        print("* Time Until Start: {0}".format(self.time_until_start))
        print("* Attendees:")
        for attendee in self.attendees:
            print("\t{0}".format(attendee))

        print("")

    def countdown(self):
        now = arrow.utcnow()
        if self.start > now:
            time_until = self.start - now
            time_type = "start"
            if self.should_notify:
                self.notify()
        else:
            time_until = self.end - now
            time_type = "end"

        return "{remaining} until the {time_type} of {name}".format(
            remaining=format_timedelta(time_until),
            time_type=time_type,
            name=self.summary
        )

    def notify(self):
        message = "The '{0}' meeting will start in the {1} in 5 minutes. "
        if self.go_to_meeting:
            message += self.go_to_meeting.join_instructions

        for attendee in self.attendees:
            attendee.send_message(message.format(self.summary, self.room))

        self.notified_attendees = True


class User(object):

    def __init__(self, data):
        self._data = data
        self._hipchat = None

    def __str__(self):
        return self.name

    @property
    def in_hipchat(self):
        if not self._hipchat:
            self._hipchat = self.find_in_hipchat()

        return self._hipchat

    @property
    def name(self):
        return self._data['displayName']

    def send_message(self, message):
        try:
            self.in_hipchat.message(message, notify=True)
        except Exception as err:
            print("Could not message {0}. {1}".format(self.name, err))

    def find_in_hipchat(self):
        hipchat_users = get_hipchat_users()
        for user in hipchat_users:
            if user['name'] == self.name:
                return user

        # As fallback, check on first name only.
        first_name = self.name.split()[0]
        for user in hipchat_users:
            if first_name in user['name']:
                return user


class GoToMeeting(object):

    def __init__(self, meeting_description):
        self._meeting_description = meeting_description
        self._id = None

    @property
    def id(self):
        if not self._id:
            link = "gotomeeting.com/join/"
            raw_id = self._meeting_description.split(link)[1]
            self._id = raw_id.split("\n")[0]

        return self._id

    @property
    def url(self):
        return "https://global.gotomeeting.com/join/{0}".format(self.id)

    @property
    def join_instructions(self):
        return "To join the GoToMeeting, please go to {0}.".format(self.url)

    def join(self):
        """Open a web browser and join the GoToMeeting.

        Note: Unfortunately, this does not work due the way that GoToMeeting
        is configured currently. We can join as a client but cannot start
        a meeting as an organizer in Linux. This would work perfectly fine
        on a Mac or Windows installation.
        """
        webbrowser.open(self.url)
