import sys
import os
import json
import arrow
import httplib2
import time

from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.discovery import build

from gcal import Calendar, Event

SERVER_KEY_PATH = "server_key.json"
USER = "kevin@wiredrive.com"


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


def main():
    # Authenticate and construct service.
    http_auth = authenticate_client()
    service = build("calendar", "v3", http=http_auth)
    calendar_list = service.calendarList().list().execute()
    useful_calendars = get_useful_calendars(calendar_list)

    for calendar in useful_calendars:
        calendar.get_events(service)

    start_countdown(useful_calendars)


def start_countdown(calendars):
    while(1):
        countdowns = [calendar.countdown() for calendar in calendars]
        print("\t".join(countdowns))
        time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuitting the Meeting Bot. Goodbye!")
