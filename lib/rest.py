#!/usr/bin/env python 
#-*- coding:UTF-8 -*-

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
    headers = {"Content-type" : 'application/x-www-form-urlencoded'}
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
    if response.status != 200:
        print response.read()

    conn.close()
    
def insert_perspective(data, cookie):
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    params = str(data)
    headers = {"Content-type" : 'application/x-www-form-urlencoded', 'Cookie' : cookie}

    print 'Inserting perspective: %s ' % data['name']
    conn.request("POST", "/rest/perspective", params, headers)
    response = conn.getresponse()
    print "Response: HTTP %s %s" % (response.status, response.reason)
    if response.status != 200:
        print response.read()

    conn.close()

def get_perspectives(cookie):
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    headers = {"Content-type" : 'application/x-www-form-urlencoded', 'Cookie' : cookie}
    #print 'Getting perspectives...'
    conn.request("GET", "/rest/perspective", None, headers)
    response = conn.getresponse()
    #print "Response: HTTP %s %s" % (response.status, response.reason)
    to_return = []
    if response.status == 200:
        responseRead = response.read()
        responseObj = json.loads(responseRead)
        to_return = responseObj['items']
    conn.close()
    return to_return

def get_nodes_from_parent(perspectiveId, parentNodeId, nodeType, cookie):
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    headers = {"Content-type" : 'application/x-www-form-urlencoded', 'Cookie' : cookie}
    #print 'Getting nodes from parent %s...' % parentNodeId
    resource = "/rest/perspective/%s/tree?type=%s&id=%s" % (perspectiveId, nodeType, parentNodeId)
    conn.request("GET", resource, None, headers)
    response = conn.getresponse()
    #print "Response: HTTP %s %s" % (response.status, response.reason)
    to_return = []
    if response.status == 200:
        responseRead = response.read()
        responseObj = json.loads(responseRead)
        to_return = responseObj
    conn.close()
    return to_return

def get_inner_nodes(globalNodeList, perspectiveId, parentNodeId, cookie):
        innerNodeList = get_nodes_from_parent(perspectiveId, parentNodeId, 'node', cookie)
        globalNodeList += innerNodeList
        for innerNode in innerNodeList:
            print '"%s"' % innerNode['text'],
            get_inner_nodes(globalNodeList, perspectiveId, innerNode['id'], cookie)

def get_all_nodes(cookie, verbose=False):
    perspectiveList = get_perspectives(cookie)
    globalNodeList = []
    for perspective in perspectiveList:
        if verbose: print 'Perspective "%s":' % perspective['name'], 
        rootNodeList = get_nodes_from_parent(perspective['id'], perspective['rootnode_id'], 'root', cookie)
        globalNodeList += rootNodeList
        for rootNode in rootNodeList:
            if verbose: print '"%s"' % rootNode['text'],
            get_inner_nodes(globalNodeList, perspective['id'], rootNode['id'], cookie)
        print
    if verbose: print "\nTotal perspectives: %s" % len(perspectiveList)
    if verbose: print "Total nodes:        %s" % len(globalNodeList)
    return globalNodeList 

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
    conn.request("PUT", "/rest/node", params, headers)
    response = conn.getresponse()
    print "Response: HTTP %s %s" % (response.status, response.reason)
    responseRead = response.read()
    responseObj = json.loads(responseRead)
    conn.close()
    if response.status != 200:
        print responseRead
    else:
        return responseObj['data']  
    
def insert_node_entity(entityId, nodeId, cookie):
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    params = urllib.urlencode({'entityId' : entityId})
    headers = {"Content-type" : 'application/x-www-form-urlencoded', 'Cookie' : cookie}
    resource = "/rest/node/%s/entities" % nodeId
    
    print 'Inserting entities %s on node %s' % (entityId, nodeId)
    conn.request("POST", resource, params, headers)
    response = conn.getresponse()
    print "Response: HTTP %s %s" % (response.status, response.reason)
    if response.status != 200:
        print response.read()

    conn.close()

def insert_user(data, cookie):
    conn = httplib.HTTPConnection(holmes_admin_conf.HOLMES_URL)
    params = urllib.urlencode({'data' : data})
    headers = {"Content-type" : 'application/x-www-form-urlencoded', 'Cookie' : cookie}

    print 'Inserting user: %s ' % data['username']
    conn.request("PUT", "/rest/user", params, headers)
    response = conn.getresponse()
    print "Response: HTTP %s %s" % (response.status, response.reason)
    if response.status != 200:
        print response.read()

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
    if response.status != 200:
        print response.read()

    conn.close()
