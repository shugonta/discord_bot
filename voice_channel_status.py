import datetime


class VoiceChannelStatus:
    def __init__(self):
        self.last_changed_time = datetime.datetime.now()
        self.last_post_time = None
        self.last_invite_time = None

    def status_change(self):
        self.last_changed_time = datetime.datetime.now()
        self.last_post_time = None
        self.last_invite_time = None

    def post(self):
        self.last_post_time = datetime.datetime.now()

    def invite(self):
        self.last_invite_time = datetime.datetime.now()