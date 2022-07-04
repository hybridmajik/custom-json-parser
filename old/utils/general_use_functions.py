import os
import json

###### GLOBALS #######
GENERIC_DEBUG = False

########################################################################################
#   Function   : splitAndReturnIndex
#   Description: Given a string and a split sequence (char/string), split a string into
#                a list and return the value of the specified index
########################################################################################
#   Arguments  : inputStr - (required) - input string to be split apart
#                splitStr - (required) - string used as a split sequence
#                index    - (required) - int index of split list
#   RETURNS    : (str) value of specified index after splitting string
########################################################################################
def splitAndReturnIndex(inputStr, splitStr, index):
    return str(inputStr).split(str(splitStr))[int(index)]

########################################################################################
#   Function   : toUpper
#   Description: Uppercases a string input
########################################################################################
#   Arguments  : inputStr - (required) - input string
#   RETURNS    : (str) uppercase version of inputStr
########################################################################################
def toUpper(inputStr):
    return inputStr.upper()

########################################################################################
#   Function   : toLower
#   Description: Lowercases a string input
########################################################################################
#   Arguments  : inputStr - (required) - input string
#   RETURNS    : (str) lowercase version of inputStr
########################################################################################
def toLower(inputStr):
    return inputStr.lower()

########################################################################################
#   Function   : cwdVerbose
#   Description: Changing working directory (with print statement)
########################################################################################
#   Arguments  : dir - (required) - directory string
#   RETURNS    : None
########################################################################################
def cwdVerbose(dir):
  os.chdir(dir)
  print(f"New Working Directory: {dir}")

########################################################################################
#   Function   : evalBoolean
#   Description: Takes a variety of specific scenarios and decides to return true/false
########################################################################################
#   Arguments  : value - (required) - item to convert to boolean
#   RETURNS    : boolean True or False
########################################################################################
def evalBoolean(value):
    if isinstance(value, str) and value.lower() in ["true", "t", "yes", "y", "1"]:
        return True
    elif isinstance(value, str) and value.lower() in ["false", "f", "no", "n", "0"]:
        return False
    elif isinstance(value, bool):
        return value
    elif (isinstance(value, int) or isinstance(value,float)) and int(value) == 1:
        return True
    elif (isinstance(value, int) or isinstance(value,float)) and int(value) == 0:
        return True
    else:
        print(f"Unexpected conversion to bool type found: {value} type({type(value)})")
        exit(1)

########################################################################################
#   Function   : setDebug
#   Description: set global debug boolean for print verbose
########################################################################################
#   Arguments  : b - (required) - boolean or string representing true/false
#   RETURNS    : None
########################################################################################
def setDebug(b):
    global GENERIC_DEBUG
    GENERIC_DEBUG = evalBoolean(b)

########################################################################################
#   Function   : print Debug / Info / Warning
#   Description: prints message with prefix string
########################################################################################
#   Arguments  : msg    - (required) - string message to print
#                isJson - (required) - boolean to print pretty/indentated
#   RETURNS    : None
########################################################################################
def printJson(jsonStr, indent=2):
    print(json.dumps(jsonStr, indent=indent, default=str))

def printDebug(msg, isJson=False):
  if isinstance(GENERIC_DEBUG, bool) and GENERIC_DEBUG:
    if isJson:
        print("DEBUG: (see json below)")
        print(json.dumps(msg, indent=2, default=str))
    else:
        print("DEBUG: " + str(msg))

def printInfo(msg, isJson=False):
    if isJson:
        print("INFO: (see json below)")
        print(json.dumps(msg, indent=2, default=str))
    else:
        print("INFO: " + str(msg))

def printWarning(msg, isJson=False):
    if isJson:
        print("WARNING: (see json below)")
        print(json.dumps(msg, indent=2, default=str))
    else:
        print("WARNING: " + str(msg))

########################################################################################
#   Function   : errorWithMsg
#   Description: prints message with ERROR prefix.  Exits with error code
########################################################################################
#   Arguments  : msg    - (required) - string message to print
#                code   - (required) - int code to exit script with
#   RETURNS    : None
########################################################################################
def errorWithMsg(msg, code):
    print("ERROR: " + str(msg))
    exit(int(code))

def ifElse(_bool, _then, _else):
    if(evalBoolean(_bool)):
        return str(_then)
    else:
        return str(_else)