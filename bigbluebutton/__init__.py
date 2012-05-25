# Copyright: 2011 Steve Challis (http://schallis.com)
# Copyright: 2012 MoinMoin:ReimarBauer
# License: MIT 

"""
    bigbluebutton

    

    This module contains functions to access bigbluebutton servers
    Meeting_Setup: for initializing a meeting.
    Meeting: for operations on the meeting after initializing.
    
"""
from urllib2 import urlopen
from urllib import urlencode
from hashlib import sha1
import xml.etree.ElementTree as ET
import random
from bigbluebutton.utils import api_call, get_xml


class Meeting_Setup(object):
    def __init__(self, bbb_api_url=None, salt=None, meeting_name='', meeting_id='', attendee_password=None, moderator_password=None):
        self.bbb_api_url = bbb_api_url
        self.salt = salt
        self.meeting_name = meeting_name
        self.meeting_id = meeting_id
        self.attendee_password = attendee_password
        self.moderator_password = moderator_password

    def create_meeting(self):
        if not Meeting(self.bbb_api_url, self.salt).is_running(self.meeting_id):
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


class Meeting(object):
    def __init__(self, bbb_api_url=None, salt=None):
        self.bbb_api_url = bbb_api_url
        self.salt = salt

    def is_running(self, meeting_id):
        call = 'isMeetingRunning'
        query = urlencode((
            ('meetingID', meeting_id),
        ))
        result = get_xml(self.bbb_api_url, self.salt, call, query)
        if result:
            return result.find('running').text == 'true'
        else:
            return 'error'
        
    def join_url(self, meeting_id, name, password):
        call = 'join'
        query = urlencode((
                           ('fullName', name),
                           ('meetingID', meeting_id),
                           ('password', password),
                           ))
        hashed = api_call(self.salt, query, call)
        url = self.bbb_api_url + call + '?' + hashed
        return url

    def end_meeting(self, meeting_id, password):
        call = 'end'
        query = urlencode((
                           ('meetingID', meeting_id),
                           ('password', password),
        ))
        result = get_xml(self.bbb_api_url, self.salt, call, query)
        if result:
            pass
        else:
            return 'error'

    def meeting_info(self, meeting_id, password):
        call = 'getMeetingInfo'
        query = urlencode((
                           ('meetingID', meeting_id),
                           ('password', password),
                           ))
        r = get_xml(self.bbb_api_url, self.salt, call, query)
        if r:
            # Create dict of values for easy use in template
            d = {
                 'start_time': r.find('startTime').text,
                 'end_time': r.find('endTime').text,
                 'participant_count': r.find('participantCount').text,
                 'moderator_count': r.find('moderatorCount').text,
                 'moderator_pw': r.find('moderatorPW').text,
                 'attendee_pw': r.find('attendeePW').text,
                 'invite_url': 'join=%s' % meeting_id,
                 }
            return d
        else:
            return None

    def get_meetings(self):
        call = 'getMeetings'
        query = urlencode((
                           ('random', 'random'),
                           ))

        result = get_xml(self.bbb_api_url, self.salt, call, query)
        if result:
            # Create dict of values for easy use in template
            d = []
            r = result[1].findall('meeting')
            for m in r:
                meeting_id = m.find('meetingID').text
                password = m.find('moderatorPW').text
                d.append({
                          'name': meeting_id,
                          'running': m.find('running').text,
                          'moderator_pw': password,
                          'attendee_pw': m.find('attendeePW').text,
                          'info': self.meeting_info(
                                               meeting_id,
                                               password)
                          })
            return d
        else:
            return 'error'

