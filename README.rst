pyLEON
=======================

This is an implementation of LEON serialization for Python. The "leon" module exposes two functions, "loads" and "dumps" which works exactly like json.loads and json.dumps. In addition to these functions, the module exposes a "Channel" class which you can construct by passing a template of the data to be sent, the same as how it works in the JavaScript implementation. The list of different types is in the "leontypes" module.

Install
========================
::
$ python setup.py install
::
Usage
========================

::
from pyleon import leon
from pyleon import leontypes

obj = {'key': 5, 'otherkey': 6, 'thirdkey': 7}
serialized = leon.dumps(obj)
// u'\x00\x03thirdkey\x00otherkey\x00key\x00\x00\x01\x00\x03\x00\x01\x02\t\x00\x00\x07\x00\x06\x00\x05'
leon.loads(serialized) == obj
// True

channel = leon.Channel({'key': leontypes.CHAR, 'otherkey': leontypes.CHAR, 'thirdkey': leontypes.CHAR})
serialized = channel.dumps(obj)
// u'\x05\x06\x07'
channel.loads(serialized) == obj
// True
::
