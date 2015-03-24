import sys
import json
import webbrowser
import httplib2

from oauth2client.client import SignedJwtAssertionCredentials
from googleapiclient import sample_tools
from apiclient.discovery import build


def authenticate_client():
    with open("server_key.json", "r") as auth_file:
        auth = json.load(auth_file)

    credentials = SignedJwtAssertionCredentials(
        auth['client_email'], auth['private_key'],
        "https://www.googleapis.com/auth/calendar.readonly",
        sub="kevin@wiredrive.com",
    )
    http_auth = credentials.authorize(httplib2.Http())
    return http_auth


def main():
    # Authenticate and construct service.
    http_auth = authenticate_client()
    service = build("calendar", "v3", http=http_auth)

    calendar_list = service.calendarList().list().execute()
    for entry in calendar_list['items']:
        print entry['summary']


if __name__ == '__main__':
    main()
