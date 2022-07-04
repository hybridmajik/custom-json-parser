import json
import re
import requests
from queue import Queue
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
    
    def getDistinctAPIReferences(self, apiNode):
        apiMatchRegex = "[%]{([^\$!#@{}()]+)\."
        apiList = re.findall(apiMatchRegex, json.dumps(apiNode.getJson()))
        return list(set(apiList))
    
    def printApiNodeGraph(self):
        self.traverseApiNodeGraphBFS(shouldPrint=True, attemptApiCall=False, externalLookupMap=None)

    def performAllApiCalls(self, externalLookupMap, shouldPrint=False):
        self.traverseApiNodeGraphBFS(shouldPrint, attemptApiCall=True, externalLookupMap=externalLookupMap)

    def traverseApiNodeGraphBFS(self, shouldPrint, attemptApiCall, externalLookupMap):
        global ROOT_API_NODE
        q = Queue(0) # inf size
        q.put(ROOT_API_NODE)
        level = 0
        # While queue has working nodes, do things (breadth first search)
        while not q.empty():
            # Get current working node and perform operations
            apiNode = q.get()
            if shouldPrint:
                apiNode.printNode()
            if attemptApiCall and apiNode.getId() != "ROOT":
                self.attemptApiCallAndRegisterResults(apiNode, externalLookupMap)
            # Add all new children to queue (FIFO)
            for childNode in apiNode.getChildList():
                level += 1
                childNode.setLevel(level)
                q.put(childNode)
    
    def attemptApiCallAndRegisterResults(self, apiNode, externalLookupMap):
        newApiJson = self.evaluateApiReferences(apiNode.getJson())
        apiNode.setJson(newApiJson)
        apiJson = apiNode.getJson()

        response = None
        if apiJson["requestMethod"] == "POST":
            response = requests.post(apiJson["url"], data=apiJson["data"], headers=apiJson["headers"])
        elif apiJson["requestMethod"] == "GET":
            response = requests.get(apiJson["url"], data=apiJson["data"], headers=apiJson["headers"])
        else:
            raise ValueError(f"Unsupported API Request type found {apiJson.requestMethod}. Only POST and GET allowed.")

        if response.status_code != 200:
            raise ValueError(f"Current API ({apiNode.getId()} attempt failed. Error Code {response.status_code}.\n Response Json:\n{response.json()}")
        else:
            if apiJson["returnPartialResponse"]:
                pathToExtract = apiJson["partialResponseKeyPath"]
                extractedJson = jsonParse.traverseJsonCheckForArrays(pathToExtract, response.json())
                externalLookupMap[apiNode.getId()] = extractedJson
            else:
                externalLookupMap[apiNode.getId()] = response.json()

def evaluateApiReferences(self, apiJson):
    jsonToReplace = apiJson
    apiMatchRegex = "[%]{([^\$!#@{}()]+)}"
    jsonAsStr = json.dumps(jsonToReplace)
    apiReferencesList = re.findall(apiMatchRegex, jsonAsStr)
    for ref in apiReferencesList:
        (strPath, tmpJson) = jsonParse.extractPathAndGetExternalJson(ref)
        evaluatedStr = jsonParse.traverseJsonCheckForArrays(strPath, tmpJson)
        print(evaluatedStr)
        printJson(jsonToReplace)
        replacedJsonAsStr = jsonAsStr.replace("%{" + ref + "}", evaluatedStr)
        jsonToReplace = json.loads(replacedJsonAsStr)
        printJson(jsonToReplace)
    return jsonToReplace