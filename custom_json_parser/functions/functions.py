def splitAndReturnIndex(inputStr, splitStr, index):
    return str(inputStr).split(str(splitStr))[int(index)]

def toUpper(inputStr):
    return inputStr.upper()

def toLower(inputStr):
    return inputStr.lower()

def ifElse(_bool, _then, _else):
    if(evalBoolean(_bool)):
        return str(_then)
    else:
        return str(_else)

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
