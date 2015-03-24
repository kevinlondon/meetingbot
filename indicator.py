import sys
import json
import httplib2
import arrow
from operator import itemgetter

from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.discovery import build

SERVER_KEY_PATH = "server_key.json"
USER = "kevin@wiredrive.com"


class Calendar(object):

    def __init__(self, raw_data):
        self.pk = raw_data['id']
        self.summary = raw_data['summary']


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
        if "Room" in calendar.summary:
            useful_calendars.append(calendar)

    return useful_calendars


def list_events(calendar, calendar_service):
    now = arrow.utcnow()
    tomorrow = arrow.utcnow().replace(days=+1)

    events = calendar_service.events().list(
        calendarId=calendar.pk,
        timeMin=str(now),
        timeMax=str(tomorrow),
        showDeleted=False,
    ).execute()

    print "\n\nRoom: ", calendar.summary
    event_list = [event for event in events['items'] if 'start' in event]
    sorted_events = sorted(event_list, key=itemgetter('start'))
    for event in sorted_events:
        print event['start'], event['summary']


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
