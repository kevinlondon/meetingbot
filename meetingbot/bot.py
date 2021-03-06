import sys
import os
import json
import arrow
import httplib2
import time

from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.discovery import build

from . import settings, lights
from .gcal import Calendar, Event


def authenticate_client():
    auth = settings.load()["google"]
    credentials = SignedJwtAssertionCredentials(
        auth['client_email'], auth['private_key'],
        "https://www.googleapis.com/auth/calendar.readonly",
        sub=auth['user'],
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

    lights.configure()
    for calendar in useful_calendars:
        calendar.get_events(service)

    start_countdown(useful_calendars)


def start_countdown(calendars):
    while(1):
        countdowns = []
        for calendar in calendars:
            countdowns.append(calendar.countdown())
            if "Small Conference Room" in calendar.summary:
                calendar.update_lights()

        output = "\t\t".join(countdowns) + "\r"
        # as per http://stackoverflow.com/questions/517127
        sys.stdout.write(output)
        sys.stdout.flush()
        time.sleep(1)
