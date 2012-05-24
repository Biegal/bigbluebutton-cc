from urllib2 import urlopen
from urllib import urlencode
from hashlib import sha1
import xml.etree.ElementTree as ET

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

def api_call(salt, query, call):
    prepared = "%s%s%s" % (call, query, salt)
    checksum = sha1(prepared).hexdigest()
    result = "%s&checksum=%s" % (query, checksum)
    return result

def get_xml(bbb_api_url, salt, call, query):
    hashed = api_call(salt, query, call)
    url = bbb_api_url + call + '?' + hashed
    result = parse(urlopen(url).read())
    return result


class Utils(object):
    def __init__(self, bbb_api_url=None, salt=None):
        self.bbb_api_url = bbb_api_url
        self.salt = salt

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

