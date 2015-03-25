import sys
import json
import httplib2
import arrow
from operator import attrgetter

from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.discovery import build

SERVER_KEY_PATH = "server_key.json"
USER = "kevin@wiredrive.com"


class Calendar(object):

    ATTRIBUTES = ['id', 'summary']

    def __init__(self, data):
        self._data = data
        self._assign_attributes()

    def _assign_attributes(self):
        self.id = self._data['id']
        self.summary = self._data['summary']


class Event(object):

    ATTRIBUTES = ['id', 'status', 'summary', 'attendees', 'description']
    DATETIMES = ['start', 'end']

    def __init__(self, data):
        self._data = data
        self._assign_attributes()

    def __repr__(self):
        return "{0} - {1}\t{2}".format(self.start, self.end, self.summary)

    def _assign_attributes(self):
        self._assign_datetimes()
        for attribute in self.ATTRIBUTES:
            value = self._data.get(attribute)
            setattr(self, attribute, value)

    def _assign_datetimes(self):
        for datetime_attr in self.DATETIMES:
            value = self._data[datetime_attr]['dateTime']
            setattr(self, datetime_attr, value)



def authenticate_client():
    with open(SERVER_KEY_PATH, "r") as auth_file:
        auth = json.load(auth_file)

    credentials = SignedJwtAssertionCredentials(
        auth['client_email'], auth['private_key'],
        "https://www.googleapis.com/auth/calendar.readonly",
        sub=USER,
    )
    http_auth = credentials.authorize(httplib2.Http())
    return http_auth


def get_useful_calendars(calendar_list):
    useful_calendars = []
    for entry in calendar_list['items']:
        calendar = Calendar(entry)
        if "Conference Room" in calendar.summary:
            useful_calendars.append(calendar)

    return useful_calendars


def list_events(calendar, calendar_service):
    now = arrow.now()
    tomorrow = arrow.now().replace(days=+1)

    events = calendar_service.events().list(
        calendarId=calendar.id,
        timeMin=str(now),
        timeMax=str(tomorrow),
        showDeleted=False,
        singleEvents=True,
    ).execute()

    print "\n\nRoom: ", calendar.summary
    event_list = [Event(data) for data in events['items'] if 'start' in data]

    sorted_events = sorted(event_list, key=attrgetter('start'))
    for event in sorted_events:
        print event
        #print event['start'], event['summary']


def main():
    # Authenticate and construct service.
    http_auth = authenticate_client()
    service = build("calendar", "v3", http=http_auth)
    calendar_list = service.calendarList().list().execute()
    useful_calendars = get_useful_calendars(calendar_list)

    for calendar in useful_calendars:
        list_events(calendar, service)

if __name__ == '__main__':
    main()
