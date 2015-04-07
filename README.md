# Meeting Bot
[![Build
Status](https://travis-ci.org/kevinlondon/meetingbot.svg)](https://travis-ci.org/kevinlondon/meetingbot) [![Coverage
Status](https://coveralls.io/repos/kevinlondon/meetingbot/badge.svg?branch=master)](https://coveralls.io/r/kevinlondon/meetingbot?branch=master)

A tool to check Google Calendar and see if a room is booked. Built to run on a Raspberry Pi.

This is still in super-alpha phase.

To Run
======

Place your Google oAuth service key as `server_key.json` in the root directory.
In addition, make another file called `hipchat.key` for your HipChat
credentials and put your oAuth key in that file as well. This will be fixed
soon.

Then, from the prompt (and within your virtualenv), type `$ python -m
meetingbot` to start it.
