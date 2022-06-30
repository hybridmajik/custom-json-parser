# custom-json-parser
A way to write and parse JSON that can be self-referential, reference external API results, and evaluate functions for results.

Example to parse a simple json with a couple global of global variables (output written to standard out)
```
python3 parse.py \
-j examples/ex-json-to-parse-api.json \
-g globalVariable1="my global value" \
-g globalVariable2=100
```

