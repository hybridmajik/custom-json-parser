import re
import json
from custom_json_parser.parser import external_lookup
from custom_json_parser.functions import functions_map
from custom_json_parser.api.api_graph import ApiGraph
from custom_json_parser.logger import logger

class Parser(object):
    def __init__(self):
        self.verbose = False
        self.debug = False
        self.apiGraph = ApiGraph()
    
    def parse(self, origJson):
        return self.parseJson(origJson, origJson)
    
    def parseJson(self, input, origJson):
        # If current object json object/dict, parse through each key and create new dict
        if(isinstance(input, dict)):
            temp = {}
            for key in input:
                temp[key] = self.parseJson(input[key], origJson)
            return temp
        # If current object json list/list, parse through each item and create new list
        elif(isinstance(input, list)):
            temp = []
            for i in input:
                temp.append(self.parseJson(i, origJson))
            return temp
        # If current object is string, attempt to evaluate any self.references or API references
        elif(isinstance(input,str)):
            return self.evaluateJsonVariable(input, origJson)
        elif(input is None):
            return None
        # If current object is any other primitive, return it
        elif(isinstance(input,(bool, int, float))):
            return input
        # If the stars align and this is magically hit, please submit a bug ticket
        else:
            logger.errorWithMsg(f"Found new uncaught type in json/dict... {type(input)}", 2)
    
    def evaluateJsonVariable(self, inputVar, origJson):
        logger.printVerbose(f"{inputVar}: {type(inputVar)}")
        # While input string contains ${.+} parameters, attempt to evaluate them
        while True:
            matchRegex = "[\$]{([^\$!#@{}()]+)}"
            matchExternalRegex = "[#]{([^\$!#@{}()]+)}"
            matchGlobalRegex = "[!]{([^\$!#@{}()]+)}"
            matchFunctionRegex = "[@]([^\$!#@{}()]+)\(([^\$!#@{}()]+)\)"

            match = re.search(matchRegex, inputVar)
            matchExternal = re.search(matchExternalRegex, inputVar)
            matchGlobal = re.search(matchGlobalRegex, inputVar)
            matchFunction = re.search(matchFunctionRegex, inputVar) 
    
            currPatternDict = {}
            if(match):
                currPatternDict["pattern"] = matchRegex
                currPatternDict["matchGroup"] = match.group(1)
                currPatternDict["baseJson"] = origJson
            elif(matchExternal):
                currPatternDict["pattern"] = matchExternalRegex
                currPatternDict["matchGroup"], currPatternDict["baseJson"] = external_lookup.extractPathAndGetExternalJson(matchExternal.group(1))
            elif(matchGlobal):
                currPatternDict["pattern"] = matchGlobalRegex
                currPatternDict["matchGroup"], currPatternDict["baseJson"] = external_lookup.extractGlobalParamPath(matchGlobal.group(1))
            elif(matchFunction):
                currPatternDict["pattern"] = matchFunctionRegex
                currPatternDict["functionAlias"] = matchFunction.group(1)
                currPatternDict["functionArgs"] = matchFunction.group(2)
            else:
                return inputVar

            # Parameters look like name.value.finalValue.  Split on "." and traverse the dictionary
            # This function allows for array indices (numeric) and special key/value filters
            currReplaceStr = ""
            if(matchGlobal or matchExternal or match):
                logger.printVerbose(f"  - found parameter indicators")
                logger.printVerbose(f"  - lookup: {currPatternDict['matchGroup']}")
                currReplaceStr = self.traverseJsonCheckForArrays(currPatternDict["matchGroup"], currPatternDict["baseJson"])
            elif(matchFunction):
                logger.printVerbose(f"  - found function call indicator")
                logger.printVerbose(f"  - function Alias: {currPatternDict['functionAlias']}")
                logger.printVerbose(f"  - function Args : {currPatternDict['functionArgs']}")
                currReplaceStr = functions_map.validateAndCallFunction(currPatternDict["functionAlias"], currPatternDict["functionArgs"])

            # Assuming we fine parmater substitution requests in order in the string, replace the first one we see with new value
            logger.printVerbose(f"  - Pre Replacement:  {inputVar} with str ({currReplaceStr})")
            logger.printVerbose(f"    - Current Pattern {currPatternDict['pattern']}")
            inputVar = re.sub(currPatternDict["pattern"], str(currReplaceStr), inputVar, 1)
            logger.printVerbose(f"  - Post Replacement: {inputVar}")
    
    def traverseJsonCheckForArrays(self, strPath, origJson):
        temp = origJson
        myList = strPath.split(".")
        logger.printVerbose(f"  - Split list: {myList}")
        # For every string in (dot)-notation path, traverse json, including arrays
        for partStr in myList:
            logger.printVerbose(f"    - Current Split Value: {partStr}")
            # Look for something like "arrayName[0]" or "arrayName[filterName=filterValue]"
            arrayMatch = re.search("^(.+)\[(.+)\]$", partStr)
            if(arrayMatch):
                arrayName, arrayIndex = (arrayMatch.group(1), arrayMatch.group(2))
                logger.printVerbose(f"    - Found Array: Name({arrayName}): Index/Filter({arrayIndex})")
                # If array index is number, let's access array via index directly
                if(arrayIndex.isnumeric()):
                    logger.printVerbose("    - Array Index specified as hardcoded index. Attempting to access list element with index")
                    temp = temp[arrayName][int(arrayIndex)]
                # Else lets assume array index is a custom filter of keyName=Value that exists across all array elements
                else:
                    logger.printVerbose("    - Array Index specified as value filter.  Attempting to find list element via filter")
                    myArrayIndexSplitList = arrayIndex.split("=")
                    filteredList = [x for x in temp[arrayName] if x[myArrayIndexSplitList[0]] == myArrayIndexSplitList[1]]
                    if(len(filteredList) != 1):
                        logger.errorWithMsg(f"Filter must return exactly 1 result. Result size = {len(filteredList)}. Please refine filter.", 3)
                    temp = filteredList[0]
                logger.printVerbose("    - Found the following array")
                logger.printVerbose("     " + json.dumps(temp))
            # Else, current traversal item appears to be a normal Key string. Attempt to access that key's value directly
            else:
                logger.printVerbose(f"    - Found non-array string key. Attempting to access json key directly")
                temp = temp[partStr]
                logger.printVerbose(f"    " + json.dumps(temp))
        # im out, jack
        return temp
    
    def checkForAndExtactAPIResults(self, inputJson, apiConfigInputJson):
        global EXTERNAL_JSON_LOOKUP
        # Go through input json and get unique list of referenced API calls
        # Given #{SOMEAPIALIAS.some.path.to.value}, matches the group result: SOMEAPIALIAS
        apiMatchRegex = "[#]{([^\$!#@{}()]+)\."
        logger.printVerbose(json.dumps(inputJson))
        apiList = re.findall(apiMatchRegex, json.dumps(inputJson))
        distinctApiList = list(set(apiList))

        # If we have API references, let's parse the API CONFIG json (we allow global-type evaluations)
        # and verify we see those keys.  If so, let's call that API result and place it in the EXTERNAL
        # lookup map.  If key not present or API fails, raise exceptions
        if distinctApiList:
            # Verify all API refs exists in config
            if(not set(distinctApiList).issubset(set(apiConfigInputJson.keys()))):
                diffSet = set(distinctApiList) - set(apiConfigInputJson.keys())
                raise ValueError(f"Some API References {diffSet} do not seem to exist in API Config JSON {apiConfigInputJson.keys()}")
            # Eval API config globals
            evaluatedAPIConfigJson = parse(apiConfigInputJson)
            if(self.verbose):
                custFuncs.printJson(evaluatedAPIConfigJson)

            apiGraph.generateApiGraph(evaluatedAPIConfigJson)
            apiGraph.performAllApiCalls(externalLookupMap=external_lookup.EXTERNAL_JSON_LOOKUP, shouldPrint=self.verbose)
            logger.printVerbose(EXTERNAL_JSON_LOOKUP)