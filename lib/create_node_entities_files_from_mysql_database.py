#!/usr/bin/env python 
#-*- coding:UTF-8 -*-

import sys
import subprocess

try:
    import __meta__
    sys.path = __meta__.PATHS.values() + sys.path
except Exception, e:
    print(e)
    sys.exit(-1)

import rest



def get_node_path(nodeId, nodePath): 
    #if debug: print "get_node_path: (nodeId, nodePath): %s, %s" %(nodeId, nodePath)     
    queryParentNode = '-e select name, parent_node_id from node where node_id = %s' % nodeId
    nodeLine = subprocess.Popen(["mysql", '-B', '-uroot', '-Dglbsce', queryParentNode], stdout=subprocess.PIPE).stdout
    nodeLine.readline() #ignoring first line (column names)
    nodeTuple = nodeLine.readline().rstrip('\n')
    nodeName = nodeTuple.split('\t')[0]
    parentNodeId = nodeTuple.split('\t')[1]
    if nodeName == 'root node':
        return nodeId
    else:
        nodePath.append(nodeName)
        return get_node_path(parentNodeId, nodePath)    

def search_leaf_node_id(nodePath, perspectiveId, parentNodeId, cookie):
    if nodePath:
        currentNode = nodePath.pop()
        registeredNodes = rest.get_nodes_from_parent(perspectiveId, parentNodeId, 'node', cookie)
        for registeredNode in registeredNodes:
            if registeredNode['text'] == currentNode:
                return search_leaf_node_id(nodePath, registeredPerspective['id'], registeredNode['id'], cookie)
    return parentNodeId

debug = False
nodeEntitiesDict = {}
cookie = rest.login_holmes()

queryEntityIds = "-e select node_id, entity_id from node_entity"
nodeEntityFile = subprocess.Popen(["mysql", '-B', '-uroot', '-Dglbsce', queryEntityIds], stdout=subprocess.PIPE).stdout
nodeEntityFile.readline() #ignoring first line (column name)
nodeEntityLine = nodeEntityFile.readline()

while nodeEntityLine:
    nodeEntityTuple = nodeEntityLine.rstrip('\n')
    nodeId = nodeEntityTuple.split('\t')[0]
    entityId = nodeEntityTuple.split('\t')[1]
    
    nodePath = []
    leafNodeId = -1  
    if debug: print "nodeId = %s" % nodeId
    if debug: print "entityId = %s" % entityId  
    rootNodeId = get_node_path(nodeId, nodePath)
    
    if debug: print "rootNodeId = %s" % rootNodeId
    if debug: print "nodePath = %s " % nodePath

    queryPerspective = '-e select name from perspective where root_node_id =  %s' % rootNodeId
    perspectiveLine = subprocess.Popen(["mysql", '-B', '-uroot', '-Dglbsce', queryPerspective], stdout=subprocess.PIPE).stdout
    perspectiveLine.readline() #ignoring first line (column names)
    perspectiveName = perspectiveLine.readline().rstrip('\n')
        
    registeredPerspectives = rest.get_perspectives(cookie)
    for registeredPerspective in registeredPerspectives:
        if registeredPerspective['name'] == perspectiveName.decode('utf-8'):
            break
        
    if nodePath:
        currentNode = nodePath.pop()
        if debug: print "currentNode: %s" % currentNode
        registeredNodes = rest.get_nodes_from_parent(registeredPerspective['id'], registeredPerspective['rootnode_id'], 'root', cookie)
        for registeredNode in registeredNodes:
            if registeredNode['text'] == currentNode.decode('utf-8'):
                leafNodeId = search_leaf_node_id(nodePath, registeredPerspective['id'], registeredNode['id'], cookie)
    else:
        leafNodeId = rootNodeId

    if debug: print "leafNodeId = %s" % leafNodeId
    
#    if leafNodeId != -1:
    if nodeEntitiesDict.has_key(leafNodeId):
        nodeEntitiesDict[leafNodeId].add(entityId)
    else:
        nodeEntitiesDict[leafNodeId] = set([entityId])
    # going to next loop iteration    
    nodeEntityLine = nodeEntityFile.readline()
               


nodes_file = open("node_entities.py", "w")
nodes_file.write('#!/usr/bin/env python\n')
nodes_file.write('#-*- coding:UTF-8 -*-\n\n') 
nodes_file.write("DATA = [\n")
for nodeId in nodeEntitiesDict.keys():
    line = '    {"nodeId": %s, "entityId": %s},\n' % (nodeId, list(nodeEntitiesDict[nodeId]))
    nodes_file.write(line)                 
nodes_file.write("]")
nodes_file.close()
print("\nnode_entities.py created.")
