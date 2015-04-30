# Meeting Bot
[![Build
Status](https://travis-ci.org/kevinlondon/meetingbot.svg)](https://travis-ci.org/kevinlondon/meetingbot) [![Coverage
Status](https://coveralls.io/repos/kevinlondon/meetingbot/badge.svg?branch=master)](https://coveralls.io/r/kevinlondon/meetingbot?branch=master)

Notify attendees of upcoming Google calendar meetings.

This is still in alpha phase.


Installation
==========

Run the following commands:

```
$ git clone https://github.com/kevinlondon/meetingbot.git
$ cd meetingbot
$ pip install -r requirements.txt
```


Configuration
=============
Make a copy of the example config file by running 
`cp example-config.yaml config.yaml`.
Then, edit the `config.yaml` file so that it includes your
login information for the various services. To get the information for each:

Hipchat
--------

1. Go to https://hipchat.com/account/api
2. Login and create a token.
3. Copy the OAuth2 token into your `config.yaml` file. 

Google
------

1. Go to https://code.google.com/apis/console
2. Login
3. Create an app, if necessary
4. Under **APIs & Auth**, click **Credentials**
5. Create a new Service account
6. Generate the JSON key
7. Copy the values from the JSON key into the `config.yaml` file.

Littlebits (optional)
---------------------

1. Sign into http://control.littlebitscloud.cc/
2. Click **Settings** along the bottom.
3. Copy the Device ID and Access Token into your `config.yaml` file.


Running the Bot
===============

`$ python -m meetingbot` will start the bot.


Running the Tests
=================

To install the developer requirements and run the tests, run:

```
$ pip install -r dev-requirements.txt
$ py.test
```
