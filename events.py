import arrow

class Event(object):

    ATTRIBUTES = ['id', 'status', 'summary', 'description']
    DATETIMES = ['start', 'end']

    def __init__(self, data):
        self._data = data
        self._assign_attributes()

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
    def gotomeeting_id(self):
        if "gotomeeting" in self.description:
            link = "gotomeeting.com/join/"
            gotomeeting_raw = self.description.split(link)[1]
            gotomeeting_id = gotomeeting_raw.split("\n")[0]
            return gotomeeting_id
        else:
            return "N/A"

    def show(self):
        print self.summary
        print "{0} - {1}".format(self.start, self.end)
        print "Time Until Start:", self.time_until_start
        print "Attendees:\n",
        for attendee in self.attendees:
            print "\t{0}".format(attendee)

        print "GoToMeeting ID: {0}".format(self.gotomeeting_id)
        print ""


