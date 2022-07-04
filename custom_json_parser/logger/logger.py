VERBOSE = False

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

def printVerbose(msg):
    global VERBOSE
    if isinstance(VERBOSE, bool) and VERBOSE:
        print("INFO: " + str(msg))

def errorWithMsg(msg, errorCode=99):
    print("ERROR: " + msg)
    if(errorCode == 0):
        errorCode=99
        print(f"WARNING: Provided error code ({errorCode}) was Zero. This function intended for non-zero codes.")
    exit(errorCode)