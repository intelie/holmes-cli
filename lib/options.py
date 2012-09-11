#!/usr/bin/env python 
#-*- coding:utf-8 -*- 

import traceback
import urllib 
import httplib 
import sys
import ldap
from ldap.controls import SimplePagedResultsControl

try:
    from lib import __meta__
    sys.path = __meta__.PATHS.values() + sys.path
except Exception, e:
    print e
    sys.exit(-1)

import rest
import streams
import entity_types
import users
import holmes_admin_conf

def handle_remove_users_option():
    print 'Remove users option yet not implemented.'

def handle_remove_entity_types_option():
    print 'Remove entity-types option yet not implemented.'

def handle_remove_streams_option():
    print 'Remove streams option yet not implemented.'

def handle_get_users_option():
    print 'Get users option yet not implemented.'

def handle_get_entity_types_option():
    print 'Get entity-types option yet not implemented.'

def handle_get_streams_option():
    cookie = rest.login_holmes()
    rest.get_streams(cookie)

def handle_insert_entity_type_option():
    cookie = rest.login_holmes()
    for data in entity_types.DATA:
        rest.insert_entity_type(data, cookie)

def handle_insert_streams_option():
    cookie = rest.login_holmes()
    stream_list = streams.STREAM_LIST
    stream_dir  = streams.STREAM_DIR
    for stream in stream_list:
        exec('from %s import %s' % (stream_dir, stream))
        exec('stream_conf = %s' % stream)
        rest.insert_stream(stream_conf, cookie)

def handle_insert_users_from_file_option():
    cookie = rest.login_holmes()
    for data in users.DATA:
       rest.insert_user(data, cookie)

def handle_insert_users_from_ldap_option():
    try:
        l = ldap.initialize(holmes_admin_conf.LDAP_SERVER_URI)
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.simple_bind(holmes_admin_conf.LDAP_USERNAME, holmes_admin_conf.LDAP_PASSWORD)
    except ldap.LDAPError, e:
        print e
        sys.exit(-1)
    try:
        result_set = []
        for search_filter in holmes_admin_conf.LDAP_SEARCH_FILTERS:
            ldap_result_id = l.ch(holmes_admin_conf.LDAP_BASE_DN, holmes_admin_conf.LDAP_SEARCH_SCOPE, search_filter, holmes_admin_conf.LDAP_RETRIEVE_ATTRIBUTES)
            
            while 1:
                result_type, result_data = l.result(ldap_result_id, 0)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        #print result_data
                        result_set.append(result_data)
    except ldap.LDAPError, e:
       print e
       sys.exit(-1)
    cookie = rest.login_holmes()
    for result in result_set:
        name = result[0][1]['name'][0]
        username = result[0][1]['sAMAccountName'][0]
        if holmes_admin_conf.EMAIL_DOMAIN:
            data = {"username":username, "name":name, "email": username + "@" + holmes_admin_conf.EMAIL_DOMAIN, "xmpp_user":""}
        else:
            data = {"username":username, "name":name, "email": "", "xmpp_user":""}
	    
        print data
        rest.insert_user(data, cookie)

#Import users from ldap using paged queries strategy
def handle_insert_users_from_ldap_paged_option():

    #Initialing ldap connection parameters
    try:        
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        l = ldap.initialize(holmes_admin_conf.LDAP_SERVER_URI)
        l.protocol_version = 3
        l.simple_bind_s(holmes_admin_conf.LDAP_USERNAME, holmes_admin_conf.LDAP_PASSWORD)
        lc = SimplePagedResultsControl(ldap.LDAP_CONTROL_PAGE_OID,True,(holmes_admin_conf.LDAP_PAGE_SEARCH_PAGE_SIZE,''))
    except ldap.LDAPError, e:
        print e
        sys.exit(-1)

    #Performing searches, one for each given search filter
    try:
        result_list = []
        for search_filter in holmes_admin_conf.LDAP_SEARCH_FILTERS:

            ldap_result_id = l.search_ext(holmes_admin_conf.LDAP_BASE_DN, holmes_admin_conf.LDAP_SEARCH_SCOPE, search_filter, serverctrls=[lc])
            pages = 0
            while True:
                pages += 1
                print "Getting page %d" % (pages,)
                rtype, rdata, rmsgid, serverctrls = l.result3(ldap_result_id)

                #Recovering valid user entries
                for rdata_element in rdata:
                    dn, result = rdata_element
                    if (('name' in result.keys()) and ('sAMAccountName' in result.keys())):
                        result_list.append(result)

                pctrls = [c for c in serverctrls if c.controlType == ldap.LDAP_CONTROL_PAGE_OID]
            
                if pctrls:
                    est, cookie = pctrls[0].controlValue
                    if cookie:
                        lc.controlValue = (holmes_admin_conf.LDAP_PAGE_SEARCH_PAGE_SIZE, cookie)
                        ldap_result_id = l.search_ext(holmes_admin_conf.LDAP_BASE_DN, holmes_admin_conf.LDAP_SEARCH_SCOPE, search_filter, serverctrls=[lc])
                    else:
                        break
                else:
                    print "Warning:  Server ignores RFC 2696 control."
                    break                                    

    except ldap.LDAPError, e:
        print e
        print traceback.format_exc()
        sys.exit(-1)
    
    #Debug
    print "\n\nTotal users: " + str(len(result_list)) + '\n\n'
    cookie = rest.login_holmes()
    for result in result_list:
        name = result['name'][0]
        username = result['sAMAccountName'][0]
        if holmes_admin_conf.EMAIL_DOMAIN:
            data = {"username":username, "name":name, "email": username + "@" + holmes_admin_conf.EMAIL_DOMAIN, "xmpp_user":""}
        else:
            data = {"username":username, "name":name, "email": "", "xmpp_user":""}
	    
        print data
        rest.insert_user(data, cookie)

insert_users_options = {
    'from_file': handle_insert_users_from_file_option,
    'from_ldap': handle_insert_users_from_ldap_option,
    'from_ldap_paged': handle_insert_users_from_ldap_paged_option
}

insert_options = {
    'streams': handle_insert_streams_option,
    'entity-types': handle_insert_entity_type_option,
    'users': insert_users_options
}

get_options = {
    'streams': handle_get_streams_option,
    'entity-types': handle_get_entity_types_option,
    'users': handle_get_users_option
}

remove_options = {
    'streams': handle_remove_streams_option,
    'entity-types': handle_remove_entity_types_option,
    'users': handle_remove_users_option
}


options = {
    'insert': insert_options,
    'get': get_options,
    'remove': remove_options
}

