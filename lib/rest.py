import urllib
import httplib
import sys
import json

try:
    import __meta__
    sys.path = __meta__.PATHS.values() + sys.path
except Exception, e:
    print e
    sys.exit(-1)

import holmes_admin_conf

def login_holmes():
    """returns session cookie from Holmes."""

    params = urllib.urlencode({'j_password' : holmes_admin_conf.HOLMES_PASSWORD, 'j_username' : holmes_admin_conf.HOLMES_USERNAME})
    headers = {'Content-type' : 'application/x-www-form-urlencoded'}
    try:
        conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
        conn.request("POST", "/j_spring_security_check", params, headers)
        response = conn.getresponse()
        cookie = response.getheader('set-cookie')
        return cookie
    except Exception, e:
        print e

def assembly_stream_data(stream, properties):
    return {'name': stream,
            'properties' : [{'name' : prop[0],
                             'type' : prop[1],
                             'qualifier' : prop[2]} for prop in properties]}

def insert_stream(conf, cookie):
    stream = conf.__name__.split('.')[1]
    properties = conf.PROPERTIES
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    data = assembly_stream_data(stream, properties)
    params = urllib.urlencode({'data' : data})
    headers = {"Content-type" : 'application/x-www-form-urlencoded', 'Cookie' : cookie}

    print 'Inserting stream: %s ' % stream
    conn.request("PUT", "/rest/stream", params, headers)
    response = conn.getresponse()
    print "Response: HTTP %s %s" % (response.status, response.reason)

    conn.close()

def get_streams(cookie):
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    headers = {"Content-type" : 'application/x-www-form-urlencoded', 'Cookie' : cookie}
    print 'Getting streams...'
    conn.request("GET", "/rest/stream", None, headers)
    response = conn.getresponse()
    print "Response: HTTP %s %s" % (response.status, response.reason)
    to_return = []
    if response.status == 200:
        responseRead = response.read()
        responseObj = json.loads(responseRead)
        print 'Total available streams: %s' % responseObj['totalCount']
        if len(responseObj['items']) > 0:
            print 'Stream list:',
        for item in responseObj['items']:
            print item['name'],
        to_return = responseObj['items']
    conn.close()
    return to_return

def insert_node(data, cookie):
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    params = urllib.urlencode({'data' : data})
    headers = {"Content-type" : 'application/x-www-form-urlencoded', 'Cookie' : cookie}

    print 'Inserting node: %s ' % data['name']
    conn.request("PUT", "/rest/node", params, headers)
    response = conn.getresponse()
    print "Response: HTTP %s %s" % (response.status, response.reason)

    conn.close()
    
def insert_node_entity(entityId, nodeId, cookie):
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    params = urllib.urlencode({'entityId' : entityId})
    headers = {"Content-type" : 'application/x-www-form-urlencoded', 'Cookie' : cookie}
    resource = "/rest/node/%s/entities" % nodeId
    
    print 'Inserting entities %s on node %s' % (entityId, nodeId)
    conn.request("POST", resource, params, headers)
    response = conn.getresponse()
    print "Response: HTTP %s %s" % (response.status, response.reason)

    conn.close()

def insert_user(data, cookie):
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    params = urllib.urlencode({'data' : data})
    headers = {"Content-type" : 'application/x-www-form-urlencoded', 'Cookie' : cookie}

    print 'Inserting user: %s ' % data['username']
    conn.request("PUT", "/rest/user", params, headers)
    response = conn.getresponse()
    print "Response: HTTP %s %s" % (response.status, response.reason)

    conn.close()

def insert_entity_type(data, cookie):
#    streams = {stream['name']: stream['id'] for stream in get_streams(cookie)}
    streams = {}
    for stream in get_streams(cookie):
	streams.update({stream['name']: stream['id']})
    data['streamsBinding'] = map(lambda x: {"id": "null",
                                            "streamId": streams[x]},
                                 data['streamsBinding'])
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    headers = {"Content-type": 'application/x-www-form-urlencoded', 'Cookie' : cookie}
    params = urllib.urlencode({'data': data})
    print 'Inserting event type: %s' % data['name']
    conn.request("PUT", "/rest/entitytype", params, headers)
    response = conn.getresponse()
    print "Response: HTTP %s %s" % (response.status, response.reason)

    conn.close()
