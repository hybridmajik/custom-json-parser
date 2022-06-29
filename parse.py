import os
import sys
import json
import re
import subprocess
import argparse

from custom_json_parser import custom_json_parser as jsonParser

from custom_json_parser.utils.general_use_functions import printJson

######## GLOBALS #########
VERBOSE = False
######## GLOBALS #########

def setVerbose(v):
  global VERBOSE
  VERBOSE = v

def printVerbose(msg, override = False):
  global VERBOSE
  if(VERBOSE or override):
    if(type(msg) is dict):
      printJson(msg)
    else:
      print(msg)


def validateAndSaveGlobals(globalsList):
  flatlistGlobals=[element for sublist in globalsList for element in sublist] # python list comprehension
  for g in flatlistGlobals:
    match = re.search("[A-Za-z0-9]+=[A-Za-z0-9]", g)
    if(not match):
      raise ValueError(f"Bad passed global ({g}). Global values passed must follow pattern KEY=VALUE")
    (key, value) = g.split("=")
    jsonParser.addGlobalVariable(key, value)

#####################################################
#                     MAIN
#####################################################
if __name__ == '__main__':
  parser = argparse.ArgumentParser(prog='custom-json-parser', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-j', '--json-path', required=True, default="version.json", help='path of json file to parse')
  parser.add_argument('-g', '--globals', action='append', nargs=1, metavar=('Key=Value'), help='global args to replace inside json using !\{\}')
  parser.add_argument('-a', '--api-config', help='config json file of REST api references to lookup')
  parser.add_argument('-o', '--output-path', help='output filepath to post evaluated json')
  parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Print all normal logs (Otherwise only prints evaluated Json')
  parser.add_argument('-d', '--debug', action='store_true', default=False, help='Add additional debug/verbose print statements')
  args = parser.parse_args()
  
  try:
    printVerbose("Starting Custom JSON Parser.")
    jsonFilePath = args.json_path
    globalsArrayOfArrays = args.globals
    apiConfigJsonFilePath = args.api_config
    outputJsonFilePath = args.output_path
    verboseFlag = args.verbose
    debugFlag = args.debug

    # Turn on verbose flag for this driver script
    setVerbose(verboseFlag)
    # Turn on verbose (debug) flag for the json parsing logic if you want to follow it through
    jsonParser.setVerbose(debugFlag)

    # If globals exist, add them to the json parsers GLOBAL-keyed map for future lookup
    if(globalsArrayOfArrays is not None):
      validateAndSaveGlobals(globalsArrayOfArrays)
    printVerbose(jsonParser.EXTERNAL_JSON_LOOKUP)
    
    # Read in the passed in json file
    with open(jsonFilePath) as json_file:
      inputJson = json.load(json_file)
    printVerbose("Input Json...")
    printVerbose(inputJson)

    # Read in API-CONFIG file if passed in
    # Check input json for references (#{...}) to APIs and attempt to extract those API results beforehand
    if(apiConfigJsonFilePath is not None):
      with open(apiConfigJsonFilePath) as json_file:
        apiConfigInputJson = json.load(json_file)
      printVerbose("API Config Json...")
      printVerbose(apiConfigInputJson)
      jsonParser.checkForAndExtactAPIResults(inputJson, apiConfigInputJson)

    # Evaluate Json (This steps assumes all jsonParser Global/External extractions are set above)
    evaluatedJson = jsonParser.parse(inputJson)

    # Decide whether we print to standard out or to a file
    if(outputJsonFilePath is None):
      printVerbose(evaluatedJson, True)
    else:
      printVerbose("Writing the following json to a file.")
      printVerbose(f"Output filename: {outputJsonFilePath}")
      printVerbose(evaluatedJson)
      with open(outputJsonFilePath, 'w', encoding='utf-8') as f:
        json.dump(evaluatedJson, f, ensure_ascii=False, indent=4)
  except ValueError as err:
    print(err)
    raise