
import argparse
from urllib2 import urlopen
from urllib import urlencode
from hashlib import sha1
import xml.etree.ElementTree as ET
import random
import bbb_settings as settings

def parse(response):
    try:
        xml = ET.XML(response)
        code = xml.find('returncode').text
        if code == 'SUCCESS':
            return xml
        else:
            raise
    except:
        return None

def api_call(query, call):
    prepared = "%s%s%s" % (call, query, settings.SALT)
    checksum = sha1(prepared).hexdigest()
    result = "%s&checksum=%s" % (query, checksum)
    return result

def join_url(meeting_id, name, password):
    call = 'join'
    query = urlencode((
                       ('fullName', name),
                       ('meetingID', meeting_id),
                       ('password', password),
                       ))
    hashed = api_call(query, call)
    url = settings.BBB_API_URL + call + '?' + hashed
    return url


class Meeting(object):
    def __init__(self, meeting_name='', meeting_id='', attendee_password=None, moderator_password=None):
        self.meeting_name = meeting_name
        self.meeting_id = meeting_id
        self.attendee_password = attendee_password
        self.moderator_password = moderator_password

    def is_running(self):
        call = 'isMeetingRunning'
        query = urlencode((
            ('meetingID', self.meeting_id),
        ))
        hashed = api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        result = parse(urlopen(url).read())
        if result:
            return result.find('running').text
        else:
            return 'error'

    @classmethod
    def end_meeting(self, meeting_id, password):
        call = 'end'
        query = urlencode((
            ('meetingID', meeting_id),
            ('password', password),
        ))
        hashed = api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        result = parse(urlopen(url).read())
        if result:
            pass
        else:
            return 'error'

    @classmethod
    def meeting_info(self, meeting_id, password):
        call = 'getMeetingInfo'
        query = urlencode((
            ('meetingID', meeting_id),
            ('password', password),
        ))
        hashed = api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        r = parse(urlopen(url).read())
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

    @classmethod
    def get_meetings(self):
        call = 'getMeetings'
        query = urlencode((
            ('random', 'random'),
        ))
        hashed = api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        result = parse(urlopen(url).read())
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
                    'info': Meeting.meeting_info(
                        meeting_id,
                        password)
                })
            return d
        else:
            return 'error'

    def create_meeting(self):
        call = 'create' 
        voicebridge = 70000 + random.randint(0,9999)
        query = urlencode((
            ('name', self.meeting_name),
            ('meetingID', self.meeting_id),
            ('attendeePW', self.attendee_password),
            ('moderatorPW', self.moderator_password),
            ('voiceBridge', voicebridge),
            ('welcome', "Welcome!"),
        ))
        hashed = api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        result = parse(urlopen(url).read())
        if result:
            return result
        else:
            raise


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='creates and join a session')
    PARSER.add_argument('--meeting_name', dest="meeting_name", type=str, required=True,
                       help='name of the meeting')
    PARSER.add_argument('--meeting_id', dest='meeting_id', required=True,
                       help='id for the meeting')
    PARSER.add_argument('--moderator', dest='moderator', required=True,
                       help='name of the meeting moderator')
    PARSER.add_argument( '--moderator_password', dest='moderator_password', required=True,
                       help='password for moderator')
    PARSER.add_argument( '--attendee_password', dest='attendee_password', required=True,
                       help='password for attendee')

    ARGS = PARSER.parse_args()

    SESSION = Meeting(ARGS.meeting_name, ARGS.meeting_id, ARGS.attendee_password, ARGS.moderator_password)
    SESSION.create_meeting()
    print "MODERATOR:"
    print join_url(ARGS.meeting_id, ARGS.moderator, ARGS.moderator_password)
    print '-------------------------------------------'

    print "RANDOM USER:"
    print join_url(ARGS.meeting_id, 'RANDOM', ARGS.attendee_password)
    print '-------------------------------------------'    

    print "ALL MEETINGS"
    print SESSION.get_meetings()
    print '-------------------------------------------'

    print "IS RUNNING (meeting is only running after someone has joined in)"
    print SESSION.is_running()
    print '-------------------------------------------'

    print "END MEETING"
    SESSION.end_meeting(ARGS.meeting_id, ARGS.moderator_password)
    print '-------------------------------------------'
    
    
    
