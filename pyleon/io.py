from bufferiterator import BufferIterator
from stringbuffer import StringBuffer
from leontypes import *
from datetime import date
import datetime
import math
import re
import collections

PARSED_SI = 0x01
PARSED_OLI = 0x02

reg = re.compile('^$')

class Parser():
  def __init__(self, buf):
    self.buffer = BufferIterator(StringBuffer(buf))
    self.state = 0
    self.stringIndex = []
    self.objectLayoutIndex = []
  def setSpec(self, spec):
    self.spec = spec
    return self
  def readString(self):
    ret = ""
    while (True):
      char = self.buffer.readUInt8()
      if (char is 0):
        break
      ret += unichr(char)
    return ret
  def parseSI(self):
    self.stringIndexType = self.buffer.readUInt8()
    if self.stringIndexType is CHAR or self.stringIndexType is SHORT or self.stringIndexType is INT:
      stringCount = self.buffer.readValue(self.stringIndexType)
    elif self.stringIndexType is EMPTY:
      stringCount = 0
    else:
      raise Exception('Invalid LEON.')
    i = 0
    while i < stringCount:
      self.stringIndex.append(self.readString())
      i += 1
    self.state |= PARSED_SI
    return self
  def parseOLI(self):
    if len(self.stringIndex) is 0:
      return self
    self.OLItype = self.buffer.readUInt8()
    if self.OLItype is CHAR or self.OLItype is SHORT or self.OLItype is INT:
      count = self.buffer.readValue(self.OLItype)
    elif self.OLItype is EMPTY:
      return self
    else:
      raise Exception('Invalid LEON.')
    i = 0
    while i < count:
      self.objectLayoutIndex.append([])
      numFields = self.buffer.readValue(self.buffer.readUInt8())
      j = 0
      while j < numFields:
        self.objectLayoutIndex[i].append(self.buffer.readValue(self.stringIndexType))
        j += 1
      i += 1
    return self
  def parseValueWithSpec(self, *args):
    if len(args) is 0:
      spec = self.spec
    else:
      spec = args[0]
    if spec is STRING:
      return self.readString()
    elif type(spec) is list:
      spec = spec[0]
      valtype = self.buffer.readUInt8()
      length = self.buffer.readValue(valtype)
      ret = []
      i = 0
      while i < length:
        ret.append(self.parseValueWithSpec(spec))
        i += 1
      return ret
    elif type(spec) is dict:
      ret = {}
      od = collections.OrderedDict(sorted(spec.items()))
      for prop in od.items():
        ret[prop[0]] = self.parseValueWithSpec(spec[prop[0]])
      return ret;
    elif spec is (TRUE & FALSE):
      return self.parseValue()
    else:
      return self.parseValue(spec)
  def parseValue(self, *args):
    if len(args) is 0:
      valtype = self.buffer.readUInt8()
    else:
      valtype = args[0]
    if valtype < OBJECT:
      return self.buffer.readValue(valtype)
    elif valtype is VARARRAY:
      valtype = self.buffer.readUInt8()
      length = self.buffer.readValue(valtype)
      ret = []
      i = 0
      while i < length:
        ret.append(self.parseValue())
        i += 1
      return ret
    elif valtype is OBJECT:
      index = self.objectLayoutIndex[self.buffer.readValue(self.OLItype)]
      ret = {}
      i = 0
      while i < len(index):
        ret[self.stringIndex[index[i]]] = self.parseValue()
        i += 1
    elif valtype is STRING:
      return self.stringIndex[self.buffer.readValue(self.stringIndexType)]
    elif valtype is UNDEFINED or valtype is NULL or valtype is NAN:
      return None
    elif valtype is TRUE:
      return True
    elif valtype is FALSE:
      return False
    elif valtype is DATE:
      return date.fromtimestamp(self.readValue(self.buffer.readUInt8()))
    elif valtype is REGEXP:
      return re.compile(self.readString())
    else:
      raise Exception('Invalid LEON.')
    return ret

def typeCheck(val):
  if type(val) is dict:
    return OBJECT
  if type(val) is list:
    return VARARRAY
  if type(val) is datetime.date:
    return DATE
  if type(val) is type(reg):
    return REGEXP
  if type(val) is bool:
    return TRUE if val else FALSE
  if type(val) is str:
    return STRING
  if type(val) is int:
    if val < 0:
      val = abs(val)
      if val < 1 << 6:
        return SIGNED | CHAR
      if val < 1 << 14:
        return SIGNED | SHORT
      if val < 1 << 30:
        return SIGNED | INT
      return DOUBLE
    if val < 1 << 7:
      return CHAR
    if val < 1 << 15:
      return SHORT
    if val < 1 << 31:
      return INT
    return DOUBLE
  if type(val) is float:
    val = abs(val)
    log = math.log(val)/math.log(2)
    if log < -128 or log > 127:
      return DOUBLE
    if log < 0:
      log = math.ceil(log)
    else:
      log = math.floor(log)
    val*2**(-log)
    figures = 1
    while val % 1 is not 0:
      val *= 2
      figures += 1
      if figures > 23:
        return DOUBLE
    return FLOAT

class Encoder():
  def __init__(self, obj):
    self.payload = obj
    self.buffer = StringBuffer()
    self.hasSpec = False
  def setSpec(self, spec):
    self.spec = spec
    self.hasSpec = True
    return self
  def append(self, buf):
    self.buffer.buffer += buf.buffer
  def writeData(self):
    if self.hasSpec:
      self.writeValueWithSpec(self.payload)
    else:
      self.writeValue(self.payload, typeCheck(self.payload))
    return self
  def export(self):
    return self.buffer.buffer
  def writeValueWithSpec(self, *args):
    if len(args) < 2:
      spec = self.spec
    else:
      spec = args[1]
    val = args[0]
    if type(spec) is list:
      self.writeValue(len(val), typeCheck(len(val)))
      i = 0
      while i < len(val):
        self.writeValueWithSpec(val[i], spec[0])
        i += 1
    elif spec is DATE:
      self.writeValue(val, DATE, True)
    elif type(spec) is dict:
      od = collections.OrderedDict(sorted(spec.items()))
      for prop in od.items():
        self.writeValueWithSpec(val[prop[0]], spec[prop[0]])
    elif spec is (TRUE & FALSE):
      self.writeValue(val, typeCheck(val), True)
    else:
      self.writeValue(val, spec, True)
  def writeValue(self, *args):
    if len(args) < 3:
      implicit = False
    else:
      implicit = args[2]
    valtype = args[1]
    val = args[0]
    typeByte = StringBuffer()
    typeByte.writeUInt8(valtype, 0)
    if not implicit:
      self.append(typeByte)
    if valtype is UNDEFINED or valtype is TRUE or valtype is FALSE or valtype is NULL or valtype is NAN:
      return 1
    if valtype is STRING:
      if len(self.stringIndex) is 0:
        self.writeString(val)
        return 2 + len(val)
      self.writeValue(self.stringIndex.index(val), self.stringIndexType, True)
      return 2
    if valtype is SIGNED | CHAR:
      buf = StringBuffer()
      buf.writeInt8(val, 0)
      self.append(buf)
      return 2
    if valtype is CHAR:
      buf = StringBuffer()
      buf.writeUInt8(val, 0)
      self.append(buf)
      return 2
    if valtype is SIGNED | SHORT:
      buf = StringBuffer()
      buf.writeInt16LE(val, 0)
      self.append(buf)
      return 3
    if valtype is SHORT:
      buf = StringBuffer()
      buf.writeInt16LE(val, 0)
      self.append(buf)
      return 5
    if valtype is SIGNED | INT:
      buf = StringBuffer()
      buf.writeInt32LE(val, 0)
      self.append(buf)
      return 5
    if valtype is INT:
      buf = StringBuffer()
      buf.writeUInt32LE(val, 0)
      self.append(buf)
      return 5
    if valtype is FLOAT:
      buf = StringBuffer()
      buf.writeFloatLE(val, 0)
      self.append(buf)
      return 5
    if valtype is DOUBLE:
      buf = StringBuffer()
      buf.writeDoubleLE(val, 0)
      self.append(buf)
      return 9
    if valtype is VARARRAY:
      self.writeValue(len(val), typeCheck(len(val)))
      i = 0
      while i < len(val):
        self.writeValue(val[i], typeCheck(val[i]))
        i += 1
    if valtype is OBJECT:
      index = matchLayout(val, self.stringIndex, self.OLI)
      if not implicit:
        self.writeValue(index, self.OLItype, True)
      i = 0
      while i < len(self.OLI[index]):
        tmp = val[self.stringIndex[self.OLI[index][i]]]
        self.writeValue(tmp, typeCheck(tmp))
        i += 1
    if valtype is DATE:
      self.writeValue(val.timestamp(), INT, true)
    if valtype is REGEXP:
      self.writeString(val.pattern)
  def writeString(self, string):
    buf = StringBuffer()
    for c in string:
      buf.writeUInt8(ord(c), -1)
    buf.writeUInt8(0, -1)
    self.append(buf)
  def writeOLI(self):
    if len(self.stringIndex) is 0:
      return self
    self.OLI = gatherLayouts(self.payload, self.stringIndex)
    if len(self.OLI) is 0:
      self.writeValue(EMPTY, CHAR, True)
      return self
    self.OLItype = typeCheck(len(self.OLI))
    self.writeValue(len(self.OLI), self.OLItype)
    for v in self.OLI:
      valtype = typeCheck(len(v))
      self.writeValue(len(v), valtype)
      for u in v:
        self.writeValue(u, self.OLItype, True)
    return self
  def writeSI(self):
    self.stringIndex = gatherStrings(self.payload)
    if len(self.stringIndex) is 0:
      self.writeValue(EMPTY, CHAR, True)
      return self
    self.stringIndexType = typeCheck(len(self.stringIndex))
    self.writeValue(len(self.stringIndex), self.stringIndexType)
    for v in self.stringIndex:
      self.writeString(v)
    return self

def matchLayout(val, stringIndex, OLI):
  layout = sorted(map(lambda x: stringIndex.index(x), list(val.keys())))
  i = 0
  while i < len(OLI):
    broken = False
    if len(layout) is not len(OLI[i]):
      i += 1
      continue
    tmp = sorted(OLI[i])
    j = 0
    while j < len(layout):
      if layout[j] is not tmp[j]:
        broken = True
        break
      j += 1
    if broken:
      i += 1
      continue
    return i

def gatherLayouts(*args):
  val = args[0]
  stringIndex = args[1]
  if len(args) is 2:
    ret = []
    branch = val
  else:
    ret = args[2]
    branch = args[3]
  if type(branch) is dict:
    ret.append([])
    for prop, value in branch.iteritems():
      ret[len(ret) - 1].append(stringIndex.index(prop))
    for prop, value in branch.iteritems():
      gatherLayouts(val, stringIndex, ret, value)
  elif type(branch) is list:
    for v in branch:
      gatherLayouts(val, stringIndex, ret, v)
  return ret

def gatherStrings(*args):
  val = args[0]
  if len(args) is 1:
    ret = []
    branch = val
  else:
    ret = args[1]
    branch = args[2]
  if type(branch) is dict:
    for prop, value in branch.iteritems():
      setPush(ret, prop)
    for prop, value in branch.iteritems():
      gatherStrings(val, ret, value)
  elif type(branch) is list:
    for v in branch:
      gatherStrings(val, ret, v)
  elif type(branch) is str:
    setPush(ret, branch)
  return ret

def setPush(arr, val):
  try:
    arr.index(val)
  except ValueError:
    arr.append(val)
