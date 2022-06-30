# custom-json-parser
A way to write and parse JSON that is rich in self reference and custom evaluation features.  Below are some of the most important features:

* **Self reference** any other json path in the document
* References can be **variablized** using other references
* Pass in **global variable references** custom to run-time
* Index or filtered **array referencing** 
* Can reference **external API results** through api configuration options
* Build/use **custom functions** to return dynamic results

## Usage

Here is the current usage of the parser. Note that parsed results default to `standard out` but you can specify an output file.  There are also verbose printing and debug options if you think there are issues.

```python
python3 parse.py --help
```
```bash
usage: custom-json-parser [-h] -j JSON_PATH [-g Key=Value] [-a API_CONFIG]
                          [-o OUTPUT_PATH] [-v] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -j JSON_PATH, --json-path JSON_PATH
                        path of json file to parse (default: version.json)
  -g Key=Value, --globals Key=Value
                        global args to replace inside json using !\{\}
                        (default: None)
  -a API_CONFIG, --api-config API_CONFIG
                        config json file of REST api references to lookup
                        (default: None)
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        output filepath to post evaluated json (default: None)
  -v, --verbose         Print all normal logs (Otherwise only prints evaluated
                        Json (default: False)
  -d, --debug           Add additional debug/verbose print statements
                        (default: False)
```

## Examples

Examples can be found in `./examples/` directory in this project.  This section will show shell commands with before and after evaluations of the JSON.

### Basic Self References
```
python3 parse.py \
-j examples/ex-json-to-parse-basic.json \
-g envFromGlobal=prod
```

<table>
<tr>
<td> State </td> <td> examples/ex-json-to-parse-beg.json </td>
</tr>
<tr>
<td> Before </td>
<td>

```json
{
    "myLocalKey": "uat",
    "myEnv": "!{envFromGlobal}",
    "myObject": {
        "dev": {
            "someKey": "devKey"
        },
        "sit": {
            "someKey": "sitKey"
        },
        "uat": {
            "someKey": "uatKey"
        },
        "prod": {
            "someKey": "prodKey"
        }
    },
    "referenceASimpleKey": "${myLocalKey}",
    "callingNestedKey": "${myObject.dev.someKey}",
    "callingNestedKeyWithVariable": "${myObject.${myEnv}.someKey}"
}
```

</td>
</tr>
<tr>
<td> After </td>
<td>

```json
{
  "myLocalKey": "uat",
  "myEnv": "prod",
  "myObject": {
    "dev": {
      "someKey": "devKey"
    },
    "sit": {
      "someKey": "sitKey"
    },
    "uat": {
      "someKey": "uatKey"
    },
    "prod": {
      "someKey": "prodKey"
    }
  },
  "referenceASimpleKey": "uat",
  "callingNestedKey": "devKey",
  "callingNestedKeyWithVariable": "prodKey"
}
```

</td>
</tr>
</table>

### Referencing Arrays
```
python3 parse.py \
-j examples/ex-json-to-parse-arrays.json \
-g myPassedInIdValue=id3
```

<table>
<tr>
<td> State </td> <td> examples/ex-json-to-parse-arrays.json </td>
</tr>
<tr>
<td> Before </td>
<td>

```json
{
    "myKey1": "test",
    "anArrayOfItems": [ "this", "is", "an", "array"],
    "anArrayOfObjects": [
        {
            "id": "id1",
            "myKey1": "myArrayValue1",
            "myKey2": "myArrayValue2"
        },
        {
            "id": "id2",
            "myKey1": "myArrayValue3",
            "myKey2": "myArrayValue4"
        },
        {
            "id": "id3",
            "myKey1": "myArrayValue5",
            "myKey2": "myArrayValue6"
        }
    ],
    "referenceASimpleKey": "${myKey1}",
    "accessingAnArrayWithIndex": "${anArrayOfItems[3]}",
    "accessingAnArrayOfObjectsWithIndex": "${anArrayOfObjects[0].myKey1}",
    "accessingAnArrayWithFilter": "${anArrayOfObjects[id=id2].myKey1}",
    "accessingAnArrayWithFilterAndGlobal": "${anArrayOfObjects[id=!{myPassedInIdValue}].myKey1}"
}
```

</td>
</tr>
<tr>
<td> After </td>
<td>

```json
{
  "myKey1": "test",
  "anArrayOfItems": [
    "this",
    "is",
    "an",
    "array"
  ],
  "anArrayOfObjects": [
    {
      "id": "id1",
      "myKey1": "myArrayValue1",
      "myKey2": "myArrayValue2"
    },
    {
      "id": "id2",
      "myKey1": "myArrayValue3",
      "myKey2": "myArrayValue4"
    },
    {
      "id": "id3",
      "myKey1": "myArrayValue5",
      "myKey2": "myArrayValue6"
    }
  ],
  "referenceASimpleKey": "test",
  "accessingAnArrayWithIndex": "array",
  "accessingAnArrayOfObjectsWithIndex": "myArrayValue1",
  "accessingAnArrayWithFilter": "myArrayValue3",
  "accessingAnArrayWithFilterAndGlobal": "myArrayValue5"
}
```

</td>
</tr>
</table>