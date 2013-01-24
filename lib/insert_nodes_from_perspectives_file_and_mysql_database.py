#!/usr/bin/env python 
#-*- coding:UTF-8 -*-

import sys
import json
import subprocess

try:
    import __meta__
    sys.path = __meta__.PATHS.values() + sys.path
except Exception, e:
    print(e)
    sys.exit(-1)

import rest
import perspectives


def insert_node_subtree(nodeObj, nodeIdDatabase, cookie):
    print 'Inserting node: %s ' % nodeObj['name']
    responseObj = rest.insert_node(json.dumps(nodeObj), cookie)    
    nodeIdRegistered =  responseObj['id']
    queryChild = "-e select name, node_id from node where parent_node_id = %s" % nodeIdDatabase
    childNodeFile = subprocess.Popen(["mysql", '-B', '-uroot', '-Dglbsce', queryChild], stdout=subprocess.PIPE).stdout
    childNodeFile.readline() #ignoring first line (column names)
    childNodeLine = childNodeFile.readline()
    while childNodeLine:
        childNodeName = childNodeLine.split('\t')[0]
        childNodeIdDatabase = childNodeLine.split('\t')[1].rstrip('\n')
        childNodeObj = {
                    "description":   "",
                    "perspectiveId": nodeObj['perspectiveId'],
                    "parentNodeId":  nodeIdRegistered,
                    "name":          childNodeName
        }
        insert_node_subtree(childNodeObj, childNodeIdDatabase, cookie)
        childNodeLine = childNodeFile.readline()
    

data = []
inputPerspectives = perspectives.DATA

cookie = rest.login_holmes()
registeredPerspectives = rest.get_perspectives(cookie)

for x in inputPerspectives:
    for y in registeredPerspectives: 
        if x['name'] == y['name']:
            cmd = "-e select name, node_id from node where parent_node_id = (select root_node_id from perspective where name = '%s')" % y['name']
            nodes = subprocess.Popen(["mysql", '-B', '-uroot', '-Dglbsce', cmd], stdout=subprocess.PIPE).stdout
            nodes.readline() #ignoring first line (column name)
            node = nodes.readline()
            while node:
                nodeName = node.split('\t')[0]
                nodeIdDatabase = node.split('\t')[1].rstrip('\n')
                nodeObj = {
                        "description":   "",
                        "perspectiveId": y['id'],
                        "parentNodeId":  y['rootnode_id'],
                        "name":          nodeName
                }
                insert_node_subtree(nodeObj, nodeIdDatabase, cookie)       
                node = nodes.readline()

