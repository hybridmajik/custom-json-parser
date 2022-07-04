import json
from custom_json_parser.functions import functions as custFuncs
from custom_json_parser.logger import logger

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

def validateAndCallFunction(functionName, argsStr):
    global CUSTOM_FUNCTIONS
    if functionName in CUSTOM_FUNCTIONS:
        logger.printVerbose(f"Found function for {functionName} command")
        logger.printVerbose(f"Arg String to parse: {argsStr}")
        argsList = map(lambda x: x.strip(), argsStr.split(","))
        logger.printVerbose(argsList)
        return CUSTOM_FUNCTIONS[functionName]["function"](*argsList)
    else:
        print(json.dumps(CUSTOM_FUNCTIONS, indent=2, default=str))
        logger.errorWithMsg(f"Could not find function {functionName} in CUSTOM_FUNCTIONS lookup.  Check code.")