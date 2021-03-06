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

### Quick Links to Examples
* [Basic Self References](#basic-self-references)
* [Referencing Arrays](#referencing-arrays)
* [Calling a custom function](#calling-a-custom-function)
* [Calling an external API](#calling-an-external-api)
* [Calling an external API with auth token](#calling-an-external-api-with-auth-token)


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

### Calling a custom function
```
python3 parse.py \
-j examples/ex-json-to-parse-functions.json \
-g myPassedInIdValue=id3
```

<table>
<tr>
<td> State </td> <td> examples/ex-json-to-parse-functions.json </td>
</tr>
<tr>
<td> Before </td>
<td>

```json
{
    "complexString": "this-needs-to-be-split-later",
    "callingAFunction": "@split(${complexString},-,4)",
    "aMoreComplexString": "http://something.neat/api/v1/extractthisstring?wow=cool",
    "functionInsideAFunction": "@split(@split(${aMoreComplexString},?,0),/,5)"
}
```

</td>
</tr>
<tr>
<td> After </td>
<td>

```json
{
  "complexString": "this-needs-to-be-split-later",
  "callingAFunction": "split",
  "aMoreComplexString": "http://something.neat/api/v1/extractthisstring?wow=cool",
  "functionInsideAFunction": "extractthisstring"
}
```

</td>
</tr>
</table>

### Calling an external API
Given an API Config JSON file of:

```json
{
    "GHIBLI": {
        "requestMethod": "GET",
        "description": "Studio Ghibli API for My Neighbor Totoro",
        "url": "https://ghibliapi.herokuapp.com/films/58611129-2dbc-4a81-a72f-77ddfc1b1b49",
        "headers": {
            "Content-Type": "application/json"
        },
        "data": null,
        "returnPartialResponse": false,
        "partialResponseKeyPath": null,
        "onlyCallOnce": true
    }
}
```

We can perform the following:

```
python3 parse.py \
-j examples/ex-json-to-parse-api.json \
-a examples/api-configs/ex-api-config-basic.json
```

<table>
<tr>
<td> State </td> <td> examples/ex-json-to-parse-api.json </td>
</tr>
<tr>
<td> Before </td>
<td>

```json
{
    "someKey": "abc",
    "movieTitle": "#{GHIBLI.title}",
    "movieDirector": "#{GHIBLI.director}",
    "movieRtScore": "#{GHIBLI.rt_score}"
}
```

</td>
</tr>
<tr>
<td> After </td>
<td>

```json
{
  "someKey": "abc",
  "movieTitle": "My Neighbor Totoro",
  "movieDirector": "Hayao Miyazaki",
  "movieRtScore": "93"
}
```

</td>
</tr>
</table>

### Calling an external API with auth token

Sometimes you might need to initially get an authorization token of some kind before you make an API call and we offer a solution to dynamically retrieve this token below.

In the JSON Below, the parser will detect that `COOL-ENDPOINT` references the `MY-AUTH-TOKEN` endpoint and it will form a parent/child graph in which all dependent endpoints will be queried first.

This will allow the `COOL-ENDPOINT` to reference the response data (in this case an access-token) of another endpoint.

```json
{
    "MY-AUTH-TOKEN": {
        "requestMethod": "POST",
        "description": "Get Authorization Token",
        "url": "!{authUrl}/api/auth/token",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache"
        },
        "data": {
            "grant_type": "client_credentials", 
            "some_id": "!{apiId}",
            "some_secret": "!{apiSecret}"
        },
        "returnPartialResponse": false,
        "partialResponseKeyPath": "",
        "onlyCallOnce": true
    },
    "COOL-ENDPOINT": {
        "requestMethod": "GET",
        "description": "A GET URL",
        "url": "!{baseUrl}/api/v4/something/!{lookupId}",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer %{MY-AUTH-TOKEN.access_token}"
        },
        "data": {},
        "returnPartialResponse": true,
        "partialResponseKeyPath": "data",
        "onlyCallOnce": true
    }
}
```