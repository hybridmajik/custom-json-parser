import json

class ApiNode(object):
    def __init__(self, id, jsonObj, parentList=[], childList=[]):
        self.id = id
        self.jsonObj = jsonObj
        self.parentList = parentList
        self.childList = childList
        self.level = 0

    def getId(self):
        return self.id
    
    def setJson(self, jsonObj):
        self.jsonObj = jsonObj

    def getJson(self):
        return self.jsonObj

    def getParentList(self):
        return self.parentList
    
    def getChildList(self):
        return self.childList

    def appendParentList(self, apiNode):
        self.parentList.append(apiNode)
    
    def appendChildList(self, apiNode):
        self.childList.append(apiNode)
    
    def setLevel(self, level):
        self.level = level

    def printNode(self):
        print(f"Graph Level {self.level}")
        print(self.id)
        if self.getParentList():
            print("Parents:")
            for p in self.getParentList():
                print(format(f'- {p.getId()}', f'>{self.level}'))
        if self.getChildList():
            print("Children:")
            for c in self.getChildList():
                print(format(f'- {c.getId()}', f'>{self.level}'))
        print("-------------------")