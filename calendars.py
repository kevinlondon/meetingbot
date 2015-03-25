from operator import attrgetter
import arrow
from events import Event


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

        print "\nRoom: ", self.summary
        event_list = [Event(data) for data in events['items'] if 'start' in data]
        self.events = sorted(event_list, key=attrgetter('start'))


