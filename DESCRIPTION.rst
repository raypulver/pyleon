pyLEON
=======================

This is an implementation of LEON serialization for Python. The "leon" module exposes two functions, "loads" and "dumps" which works exactly like json.loads and json.dumps. In addition to these functions, the module exposes a "Channel" class which you can construct by passing a template of the data to be sent, the same as how it works in the JavaScript implementation. The list of different types is in the "leontypes" module.
