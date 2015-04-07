import webbrowser

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

    @property
    def url(self):
        return "https://global.gotomeeting.com/join/{0}".format(self.id)

    @property
    def join_instructions(self):
        return "To join the GoToMeeting, please go to {0}.".format(self.url)

    def join(self):
        """Open a web browser and join the GoToMeeting.

        Note: Unfortunately, this does not work due the way that GoToMeeting
        is configured currently. We can join as a client but cannot start
        a meeting as an organizer in Linux. This would work perfectly fine
        on a Mac or Windows installation.
        """
        webbrowser.open(self.url)
