from operator import attrgetter

import arrow

class Calendar(object):

    ATTRIBUTES = ['id', 'summary']

    def __init__(self, data):
        self._data = data
        self._assign_attributes()

    def _assign_attributes(self):
        self.id = self._data['id']
        self.summary = self._data['summary']

    def get_events(self, calendar_service):
        now = arrow.now()
        tomorrow = arrow.now().replace(days=+1)

        events = calendar_service.events().list(
            calendarId=self.id,
            timeMin=str(now),
            timeMax=str(tomorrow),
            showDeleted=False,
            singleEvents=True,
        ).execute()

        event_list = [Event(data) for data in events['items'] if 'start' in data]
        self.events = sorted(event_list, key=attrgetter('start'))


class Event(object):

    ATTRIBUTES = ['id', 'status', 'summary', 'description']
    DATETIMES = ['start', 'end']

    def __init__(self, data):
        self._data = data
        self._assign_attributes()
        self._meeting = None

    def __repr__(self):
        return "{0} - {1}\t{2}".format(self.start, self.end, self.summary)

    def _assign_attributes(self):
        self._assign_datetimes()
        for attribute in self.ATTRIBUTES:
            value = self._data.get(attribute, "")
            setattr(self, attribute, value)

    def _assign_datetimes(self):
        for datetime_attr in self.DATETIMES:
            raw_dt = self._data[datetime_attr]['dateTime']
            setattr(self, datetime_attr, arrow.get(raw_dt))

    @property
    def attendees(self):
        return [person['displayName'] for person in self._data['attendees']
                if "Room" not in person['displayName']]

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

    def show(self):
        print(self.summary)
        print("* {0} - {1}".format(self.start, self.end))
        print("* Time Until Start:", self.time_until_start)
        print("* GoToMeeting ID: {0}".format(self.gotomeeting_id))
        print("* Attendees:\n",)
        for attendee in self.attendees:
            print("\t{0}".format(attendee))

        print("")


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
