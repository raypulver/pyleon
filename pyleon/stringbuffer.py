from leontypes import *
import math

class StringBuffer():
  def __init__(self, *args):
    if len(args) >= 1 and (type(args[0]) is str or type(args[0]) is unicode):
      self.buffer = args[0]
    else:
      self.buffer = ""
  def writeUInt8(self, val, offset):
    val = int(val)
    if offset is len(self.buffer) or offset is -1:
      self.buffer += unichr(val)
    else:
      self.buffer = self.buffer[:offset] + unichr(val) + self.buffer[offset + 1:]
    return offset + 1
  def writeInt8(self, val, offset):
    val = int(val)
    val = complement(-val, 8) if val < 0 else val
    return self.writeUInt8(val, offset)
  def writeUInt16LE(self, val, offset):
    bytelist = bytearr(val, SHORT)
    addendum = ''
    for b in reversed(bytelist):
      addendum += unichr(b)
    if offset >= len(self.buffer) or offset is -1:
      self.buffer += addendum
    else:
      self.buffer = self.buffer[:offset] + addendum + self.buffer[offset + 2:]
    return offset + 2
  def writeInt16LE(self, val, offset):
    val = complement(-val, 16) if val < 0 else val
    return self.writeUInt16LE(val, offset)
  def writeUInt32LE(self, val, offset):
    bytelist = bytearr(val, INT)
    addendum = ''
    for b in reversed(bytelist):
      addendum += unichr(b)
    if offset >= len(self.buffer) or offset is -1:
      self.buffer += addendum
    else:
      self.buffer = self.buffer[:offset] + addendum + self.buffer[offset + 4:]
    return offset + 4
  def writeInt32LE(self, val, offset):
    val = complement(-val, 32) if val < 0 else val
    return self.writeUInt32LE(val, offset)
  def writeFloatLE(self, val, offset):
    bytelist = bytearr(val, FLOAT)
    for i, b in enumerate(reversed(bytelist)):
      self.writeUInt8(b, offset + i)
    return offset + 4
  def writeDoubleLE(self, val, offset):
    bytelist = bytearr(val, DOUBLE)
    for i, b in enumerate(reversed(bytelist)):
      self.writeUInt8(b, offset + i)
    return offset + 8
  def readUInt8(self, offset):
    return ord(self.buffer[offset])
  def readInt8(self, offset):
    val = ord(self.buffer[offset])
    if 0x80 & val:
      return -complement(val, 8)
    return val
  def readUInt16LE(self, offset):
    return ord(self.buffer[offset]) | (ord(self.buffer[offset + 1]) << 8)
  def readInt16LE(self, offset):
    val = self.readUInt16LE(offset)
    if val & 0x8000:
      return -complement(val, 16)
    return val
  def readUInt32LE(self, offset):
    return ord(self.buffer[offset]) | (ord(self.buffer[offset + 1]) << 8) | (ord(self.buffer[offset + 2]) << 16) | (ord(self.buffer[offset + 3]) << 24)
  def readInt32LE(self, offset):
    val = self.readUInt32LE(offset)
    if val & 0x80000000:
      return -complement(val, 32)
    return val
  def readFloatLE(self, offset):
    bytelist = []
    i = 0
    while i < 4:
      bytelist.append(self.readUInt8(offset + (3 - i)))
      i += 1
    return bytes_to_float(bytelist)
  def readDoubleLE(self, offset):
    bytelist = []
    i = 0
    while i < 8:
      bytelist.append(self.readUInt8(offset + (7 - i)))
      i += 1
    return bytes_to_double(bytelist)

def complement(val, bits):
  mask = (1 << bits) - 1
  return (val ^ mask) + 1

def bytearr(val, valtype):
  ret = []
  if valtype is CHAR:
    ret.append(val)
    return ret
  elif valtype is SIGNED | CHAR:
    return bytearr(complement(-val, 8), CHAR) if val < 0 else bytearr(val, CHAR)
  elif valtype is SHORT:
    ret.append(rshift(val, 8))
    ret.append(val & 0xFF)
    return ret
  elif valtype is SIGNED | SHORT:
    return bytearr(complement(-val, 16), SHORT) if val < 0 else bytearr(val, SHORT)
  elif valtype is INT:
    ret.append(rshift(val, 24) & 0xFF)
    ret.append(rshift(val, 16) & 0xFF)
    ret.append(rshift(val, 8) & 0xFF)
    ret.append(val & 0xFF)
    return ret
  elif valtype is SIGNED | INT:
    return bytearr(complement(-val, 32), INT) if val < 0 else bytearr(val, INT)
  elif valtype is FLOAT:
    exp = 127
    sig = val
    if sig < 0:
      sign = 1
    else:
      sign = 0
    sig = abs(sig)
    log = math.log(sig)/math.log(2)
    if log > 0:
      log = int(math.floor(log))
    else:
      log = int(math.ceil(log))
    sig *= (2**(-log + 23))
    exp += log
    sig = int(round(sig))
    sig &= 0x7FFFFF
    ret.append(sign << 7)
    ret[0] |= rshift((exp & 0xFE), 1)
    ret.append((exp & 0x01) << 7)
    ret[1] |= (rshift(sig, 16) & 0x7F)
    ret.append(rshift(sig, 8) & 0xFF)
    ret.append(sig & 0xFF)
    return ret
  elif valtype is DOUBLE:
    exp = 1023
    sig = val
    if sig < 0:
      sign = 1
    else:
      sign = 0
    sig = abs(sig)
    log = math.log(sig)/math.log(2)
    if log > 0:
      log = int(math.floor(log))
    else:
      log = int(math.ceil(log))
    sig *= (2**(-log + 52))
    exp += log
    sig = int(round(sig))
    sig = int(bin(sig)[3:], 2)
    ret.append(sign << 7)
    ret[0] |= rshift(exp, 4)
    ret.append((exp & 0x0F) << 4)
    ret[1] |= rshift(sig, 48) & 0x0F
    sh = 40
    i = 0
    while i < 6:
      ret.append(rshift(sig, sh) & 0xFF)
      sh -= 8
      i += 1
    return ret

def bytes_to_float(bytelist):
  sign = rshift(0x80 & bytelist[0], 7)
  exp = ((bytelist[0] & 0x7F) << 1) + rshift(bytelist[1] & 0x80, 7)
  sig = 0
  bytelist[1] &= 0x7F
  i = 0
  while i < 3:
    sig += (bytelist[i + 1] << ((2 - i)*8))
    i += 1
  sig |= 0x800000
  if sign is 1:
    sig = -sig
  return sig*2**(exp - (127 + 23))

def bytes_to_double(bytelist):
  sign = rshift((0x80 & bytelist[0]), 7)
  exp = ((bytelist[0] & 0x7F) << 4) + (rshift((bytelist[1] & 0xF0), 4))
  sig = 0
  bytelist[1] &= 0x0F
  i = 0
  while (i < 7):
    sig += bytelist[i + 1] << ((6 - i)*8)
    i += 1
  sig += (1 << 52)
  if sign is 1:
    sig = -sig
  return sig*2**(exp - (1023 + 52))

def rshift(val, n):
  return val >> n
