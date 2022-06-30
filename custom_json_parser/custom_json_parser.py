import os
import sys
import json
import re
import subprocess
# AWS
import boto3
from boto3 import client
# Customer JSON Parser Utils
from custom_json_parser.utils import general_use_functions as custFuncs
from custom_json_parser.utils import api_graph as apiGraph

###### GLOBALS #######
# Used for debug print messaging if there's problems evaluating substitution params
VERBOSE = False

# Used to add in external JSON objects with attached KEYWORDS in the substitution params
# Ex.  "#{SOMEAPIALIAS.configuration.details.id}"
# ^ Implies the global map contains { "SOMEAPIALIAS": {...} } with the attached structure
GLOBALS_KEY = "GLOBAL"
EXTERNAL_JSON_LOOKUP = {
  GLOBALS_KEY: {}
}

CUSTOM_FUNCTIONS = {
  "split": {
    "function": custFuncs.splitAndReturnIndex,
    "numArgs": 3,
    "description": "Splits a string along the disired split character and returns specified index"
  },
  "toUpper": {
    "function": custFuncs.toUpper,
    "numArgs": 1,
    "description": "Uppercases string"
  },
  "toLower": {
    "function": custFuncs.toLower,
    "numArgs": 1,
    "description": "Lowercases string"
  },
  "if": {
    "function": custFuncs.ifElse,
    "numArgs": 3,
    "description": "if/else using first arg as boolean, returns 2nd arg as string, else 3rd arg as string"
  }
  # ,
  # "doesRoleExist": {
  #   "function": awsUtils.doesRoleExist,
  #   "numArgs": 1,
  #   "description": "returns True if aws role name exists, else False"
  # }
}

########################################################################################
#   Function   : validateAndCallFunction
#   Description: Attempts to call a custom function for variable substitution
########################################################################################
#   Arguments  : functionName - (required) - Custom function alias (key in dict)
#                argsStr      - (required) - comma delimited string of arguments
#   RETURNS    : None
########################################################################################
def validateAndCallFunction(functionName, argsStr):
  if functionName in CUSTOM_FUNCTIONS:
    printVerbose(f"Found function for {functionName} command")
    printVerbose(f"Arg String to parse: {argsStr}")
    argsList = map(lambda x: x.strip(), argsStr.split(","))
    printVerbose(argsList)
    return CUSTOM_FUNCTIONS[functionName]["function"](*argsList)
  else:
    print(json.dumps(CUSTOM_FUNCTIONS, indent=2, default=str))
    errorWithMsg(f"Could not find function {functionName} in CUSTOM_FUNCTIONS lookup.  Check code.")

########################################################################################
#   Function   : addExternalJson
#   Description: Adds a key/value pair for an external json object to a global dict
########################################################################################
#   Arguments  : key - (required) - key string
#                json - (required) - value json/dict
#   RETURNS    : None
########################################################################################
def addExternalJson(key, json):
  global EXTERNAL_JSON_LOOKUP
  EXTERNAL_JSON_LOOKUP[key] = json

########################################################################################
#   Function   : addGlobalVariable
#                addGlobalsAsJson
#   Description: Adds or overrides the GLOBAL json map for furture substitutions/refs
########################################################################################
#   Arguments  : key - (required) - new global key to be referenced in the GLOBAL map
#                value - (required) - new value for that global key in the GLOBAL map
#                -----------------------------------------------------------------------
#                json - (required) - full override the GLOBAL map value with new json
#   RETURNS    : None
########################################################################################
def addGlobalVariable(key, value):
  global GLOBALS_KEY
  global EXTERNAL_JSON_LOOKUP
  EXTERNAL_JSON_LOOKUP[GLOBALS_KEY][key] = value

def addGlobalsAsJson(json):
  global GLOBALS_KEY
  addExternalJson(GLOBALS_KEY, json)

########################################################################################
#   Function   : extractPathAndGetExternalJson
#   Description: Given a (dot)-notation JSON Path, extract the first object in the path.
#                Check if this alias exists as a key in the global EXTERNAL_JSON_LOOKUP
#                dict. If so, return the original path (minus the key) and the ext json
########################################################################################
#   Arguments  : strPath - (required) - json path with key element (see description)
# 
#   RETURNS    : (1) string representing the original json path, minus the key alias
#                (2) dict representing the external json for the key alias
########################################################################################
def extractGlobalParamPath(strPath):
  global GLOBALS_KEY
  printVerbose(f"  - Checking for GLOBAL argument: {GLOBALS_KEY}." + strPath)
  return extractPathAndGetExternalJson(f"{GLOBALS_KEY}.{strPath}")

def extractPathAndGetExternalJson(strPath):
  myList = strPath.split(".")
  keyLookup = myList[0]
  strPathNoKey = ".".join(myList[1:])
  
  printVerbose(f"  - Checking if the key alias exists in EXTERNAL_JSON_LOOKUP: ({keyLookup})")
  if keyLookup not in EXTERNAL_JSON_LOOKUP:
    errorWithMsg(f"Could not find key ({keyLookup}) in EXTERNAL_JSON_LOOKUP.  Did you add it?")
  printVerbose(f"  - Attempting to parse path ({strPathNoKey}) from ({keyLookup}) lookup")
  return (strPathNoKey, EXTERNAL_JSON_LOOKUP[keyLookup])

########################################################################################
#   Function   : errorWithMsg
#   Description: Prints included message and exits with provided error code
########################################################################################
#   Arguments  : msg - (required) - error message to print out
#                errorCode - (optional) - non-zero error code to exit script with
#   RETURNS    : None
########################################################################################
def errorWithMsg(msg, errorCode=99):
  print("ERROR: " + msg)
  if(errorCode == 0):
    errorCode=99
    print(f"WARNING: Provided error code ({errorCode}) was Zero. This function intended for non-zero codes.")
  exit(errorCode)

########################################################################################
#   Function   : setVerbose
#   Description: Sets the global VERBOSE flag for debugging to True or False
########################################################################################
#   Arguments  : v - boolean True or False
#   RETURNS    : None
########################################################################################
def setVerbose(v):
  global VERBOSE
  if(isinstance(v, str) and v.lower() in ["true", "t", "yes", "y", "1"]):
    VERBOSE = True
  elif(isinstance(v, str) and v.lower() in ["false", "f", "no", "n", "0"]):
    VERBOSE = False
  elif(isinstance(v, bool)):
    VERBOSE = v
  else:
    errorWithMsg(f"You can only set VERBOSE flag with Boolean value or String value 'true/false/yes/no'. Received {v}: {type(v)}", 1)

########################################################################################
#   Function   : printVerbose
#   Description: If global VERBOSE is set to True, prints DEBUG + included message
########################################################################################
#   Arguments  : msg - string to print in VERBOSE/DEBUG mode
#   RETURNS    : None
########################################################################################
def printVerbose(msg):
  if isinstance(VERBOSE, bool) and VERBOSE:
    print("DEBUG: " + str(msg))

########################################################################################
#   Function   : parseJson
#   Description: Given a json/dict structure, return the same structure, but attempt to
#                to find any key/value pairs with references to other json values.
#                Call the `evaluateJsonVariable` function to do this.
########################################################################################
#   Arguments  : input - (required) - valid json/dictionary structure to be parsed 
#                origJson - (required) - the original json structure for reference
#   RETURNS    : the input structure with dynamic values correctly evaluated
########################################################################################
def parse(origJson):
  return parseJson(origJson, origJson)

def parseJson(input, origJson):
  # If current object json object/dict, parse through each key and create new dict
  if(isinstance(input, dict)):
    temp = {}
    for key in input:
      temp[key] = parseJson(input[key], origJson)
    return temp
  # If current object json list/list, parse through each item and create new list
  elif(isinstance(input, list)):
    temp = []
    for i in input:
      temp.append(parseJson(i, origJson))
    return temp
  # If current object is string, attempt to evaluate any self.references or API references
  elif(isinstance(input,str)):
    return evaluateJsonVariable(input, origJson)
  # If current object is any other primitive, return it
  elif(isinstance(input,(bool, int, float))):
    return input
  # If the stars align and this is magically hit, please submit a bug ticket
  else:
    errorWithMsg(f"Found new uncaught type in json/dict... {type(input)}", 2)

########################################################################################
#   Function   : evaluateJsonVariable
#   Description: Parses json object with self-referencing key/value pairs.
#                You can reference fully qualified (dot-notation) json paths. You can
#                also reference arrays with [#]-notation or [key=value]-filter-notation.
#                References must be FULLY qualified. There is no local-scoped inferences
#                for keys in the same sub-object.
########################################################################################
#   Arguments  : inputVar - (required) String containing ${*} references to other json
#                           elements
#                origJson  - (required) original input json for reference
#   RETURNS    : Recursively evaluated string to intended values
########################################################################################
def evaluateJsonVariable(inputVar, origJson):
  printVerbose(f"{inputVar}: {type(inputVar)}")
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
      currPatternDict["matchGroup"], currPatternDict["baseJson"] = extractPathAndGetExternalJson(matchExternal.group(1))
    elif(matchGlobal):
      currPatternDict["pattern"] = matchGlobalRegex
      currPatternDict["matchGroup"], currPatternDict["baseJson"] = extractGlobalParamPath(matchGlobal.group(1))
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
      printVerbose(f"  - found parameter indicators")
      printVerbose(f"  - lookup: {currPatternDict['matchGroup']}")
      currReplaceStr = traverseJsonCheckForArrays(currPatternDict["matchGroup"], currPatternDict["baseJson"])
    elif(matchFunction):
      printVerbose(f"  - found function call indicator")
      printVerbose(f"  - function Alias: {currPatternDict['functionAlias']}")
      printVerbose(f"  - function Args : {currPatternDict['functionArgs']}")
      currReplaceStr = validateAndCallFunction(currPatternDict["functionAlias"], currPatternDict["functionArgs"])

    # Assuming we fine parmater substitution requests in order in the string, replace the first one we see with new value
    printVerbose(f"  - Pre Replacement:  {inputVar} with str ({currReplaceStr})")
    printVerbose(f"    - Current Pattern {currPatternDict['pattern']}")
    inputVar = re.sub(currPatternDict["pattern"], str(currReplaceStr), inputVar, 1)
    printVerbose(f"  - Post Replacement: {inputVar}")

########################################################################################
#   Function   : traverseJsonCheckForArrays
#   Description: For a fully qualified (dot)-notationed path, traverse a json object
#                to the end in order to evaluate the overal substitution variable.
#                This function allows arrays to be accessed via [#] notation or a 
#                special [filterName=filterValue] notation
########################################################################################
#   Arguments  : strPath   - (required) - specific substitution variable's 
#                            (dot)-notationed path referencing another element in the 
#                            origJson
#                origJson  - (optional) - original json for reference
#   RETURNS    : Recursively evaluated string to intended values
########################################################################################
def traverseJsonCheckForArrays(strPath, origJson):
  temp = origJson
  myList = strPath.split(".")
  printVerbose(f"  - Split list: {myList}")
  # For every string in (dot)-notation path, traverse json, including arrays
  for partStr in myList:
    printVerbose(f"    - Current Split Value: {partStr}")
    # Look for something like "arrayName[0]" or "arrayName[filterName=filterValue]"
    arrayMatch = re.search("^(.+)\[(.+)\]$", partStr)
    if(arrayMatch):
      arrayName, arrayIndex = (arrayMatch.group(1), arrayMatch.group(2))
      printVerbose(f"    - Found Array: Name({arrayName}): Index/Filter({arrayIndex})")
      # If array index is number, let's access array via index directly
      if(arrayIndex.isnumeric()):
        printVerbose("    - Array Index specified as hardcoded index. Attempting to access list element with index")
        temp = temp[arrayName][int(arrayIndex)]
      # Else lets assume array index is a custom filter of keyName=Value that exists across all array elements
      else:
        printVerbose("    - Array Index specified as value filter.  Attempting to find list element via filter")
        myArrayIndexSplitList = arrayIndex.split("=")
        filteredList = [x for x in temp[arrayName] if x[myArrayIndexSplitList[0]] == myArrayIndexSplitList[1]]
        if(len(filteredList) != 1):
          errorWithMsg(f"Filter must return exactly 1 result. Result size = {len(filteredList)}. Please refine filter.", 3)
        temp = filteredList[0]
      printVerbose("    - Found the following array")
      printVerbose("     " + json.dumps(temp))
    # Else, current traversal item appears to be a normal Key string. Attempt to access that key's value directly
    else:
      printVerbose(f"    - Found non-array string key. Attempting to access json key directly")
      temp = temp[partStr]
      printVerbose(f"    " + json.dumps(temp))
  # im out, jack
  return temp

def checkForAndExtactAPIResults(inputJson, apiConfigInputJson):
  global EXTERNAL_JSON_LOOKUP
  # Go through input json and get unique list of referenced API calls
  # Given #{SOMEAPIALIAS.some.path.to.value}, matches the group result: SOMEAPIALIAS
  apiMatchRegex = "[#]{([^\$!#@{}()]+)\."
  print(json.dumps(inputJson))
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
    custFuncs.printJson(evaluatedAPIConfigJson)

    apiGraph.generateApiGraph(evaluatedAPIConfigJson)
    apiGraph.performAllApiCalls(externalLookupMap=EXTERNAL_JSON_LOOKUP, shouldPrint=True)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(EXTERNAL_JSON_LOOKUP)