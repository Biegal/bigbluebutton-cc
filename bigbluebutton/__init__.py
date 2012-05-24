
from urllib2 import urlopen
from urllib import urlencode
from hashlib import sha1
import xml.etree.ElementTree as ET
import random
from bigbluebutton.utils import api_call, get_xml


class Meeting(object):
    def __init__(self, bbb_api_url=None, salt=None, meeting_name='', meeting_id='', attendee_password=None, moderator_password=None):
        self.bbb_api_url = bbb_api_url
        self.salt = salt
        self.meeting_name = meeting_name
        self.meeting_id = meeting_id
        self.attendee_password = attendee_password
        self.moderator_password = moderator_password

    def is_running(self):
        call = 'isMeetingRunning'
        query = urlencode((
            ('meetingID', self.meeting_id),
        ))
        result = get_xml(self.bbb_api_url, self.salt, call, query)
        if result:
            return result.find('running').text == 'true'
        else:
            return 'error'

    def create_meeting(self):
        if not self.is_running():
            call = 'create'
            voicebridge = 70000 + random.randint(0, 9999)
            query = urlencode((
                ('name', self.meeting_name),
                ('meetingID', self.meeting_id),
                ('attendeePW', self.attendee_password),
                ('moderatorPW', self.moderator_password),
                ('voiceBridge', voicebridge),
                ('welcome', "Welcome!"),
            ))
            result = get_xml(self.bbb_api_url, self.salt, call, query)
            if result:
                return result
            else:
                raise

