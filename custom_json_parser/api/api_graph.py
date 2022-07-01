import json
import re
from api_node import ApiNode

class ApiGraph(object):
    def __init__(self):
        self.rootNode = ApiNode("ROOT", {}, [], [])
    
    def generateApiGraph(self, apiConfigJson):
        # Map reference of every API specified
        apiNodeMap = {}
        
        # Initialize api node map with every api object in the config json
        for apiId in apiConfigJson.keys():
            apiNode = ApiNode(apiId, apiConfigJson[apiId], [], [])
            apiNodeMap[apiId] = apiNode
        
        # For every node in the map, fill out their parent/child nodes (i.e. form the graph)
        for apiNodeId in apiNodeMap:
            apiNode = apiNodeMap[apiNodeId]
            apiRefsList = self.getDistinctAPIReferences(apiNode)
            # If no references in this node, add to ROOT nodes children list
            if not apiRefsList:
                self.rootNode.appendChildList(apiNode)
                apiNode.appendParentList(self.rootNode)
            # Else if references exist, find the parent node and append all relevent relationship lists
            else:
                for apiRefId in apiRefsList:
                    if apiRefId not in apiConfigJson.keys():
                        raise ValueError(f"Cannot find API reference {apiRefId} in API Config JSON File.")
                    parentNode = apiNodeMap[apiRefId]
                    parentNode.appendChildList(apiNode)
                    apiNode.appendParentList(parentNode)
    
    def getDistinctAPIReferences(apiNode):
        apiMatchRegex = "[%]{([^\$!#@{}()]+)\."
        apiList = re.findall(apiMatchRegex, json.dumps(apiNode.getJson()))
        return list(set(apiList))