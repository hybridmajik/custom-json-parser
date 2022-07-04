from pickle import GLOBAL
from custom_json_parser.logger import logger

GLOBALS_KEY = "GLOBAL"

EXTERNAL_JSON_LOOKUP = {
    GLOBALS_KEY: {}
}

def addExternalJson(key, json):
    global EXTERNAL_JSON_LOOKUP
    EXTERNAL_JSON_LOOKUP[key] = json

def addGlobalVariable(key, value):
    global GLOBALS_KEY
    global EXTERNAL_JSON_LOOKUP
    EXTERNAL_JSON_LOOKUP[GLOBALS_KEY][key] = value

def addGlobalsAsJson(json):
    global GLOBALS_KEY
    addExternalJson(GLOBALS_KEY, json)

def extractGlobalParamPath(strPath):
    global GLOBALS_KEY
    logger.printVerbose(f"  - Checking for GLOBAL argument: {GLOBALS_KEY}." + strPath)
    return extractPathAndGetExternalJson(f"{GLOBALS_KEY}.{strPath}")

def extractPathAndGetExternalJson(strPath):
    global EXTERNAL_JSON_LOOKUP
    myList = strPath.split(".")
    keyLookup = myList[0]
    strPathNoKey = ".".join(myList[1:])

    logger.printVerbose(f"  - Checking if the key alias exists in EXTERNAL_JSON_LOOKUP: ({keyLookup})")
    if keyLookup not in EXTERNAL_JSON_LOOKUP:
        logger.errorWithMsg(f"Could not find key ({keyLookup}) in EXTERNAL_JSON_LOOKUP.  Did you add it?")
    logger.printVerbose(f"  - Attempting to parse path ({strPathNoKey}) from ({keyLookup}) lookup")
    return (strPathNoKey, EXTERNAL_JSON_LOOKUP[keyLookup])