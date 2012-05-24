from urllib2 import urlopen
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
