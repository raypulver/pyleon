from leontypes import *
class BufferIterator():
  def __init__(self, buf):
    self.i = 0
    self.sb = buf
  def readUInt8(self):
    self.i += 1
    return self.sb.readUInt8(self.i - 1)
  def readInt8(self):
    self.i += 1
    return self.sb.readInt8(self.i - 1)
  def readUInt16(self):
    self.i += 2
    return self.sb.readUInt16LE(self.i - 2)
  def readInt16(self):
    self.i += 2
    return self.sb.readInt16LE(self.i - 2)
  def readUInt32(self):
    self.i += 4
    return self.sb.readUInt32LE(self.i - 4)
  def readInt32(self):
    self.i += 4
    return self.sb.readInt32LE(self.i - 4)
  def readFloat(self):
    self.i += 4
    return self.sb.readFloatLE(self.i - 4)
  def readDouble(self):
    self.i += 8
    return self.sb.readDoubleLE(self.i - 8)
  def readValue(self, valtype):
    if valtype is CHAR:
      return self.readUInt8()
    elif valtype is SIGNED | CHAR:
      return self.readInt8()
    elif valtype is SHORT:
      return self.readUInt16()
    elif valtype is SIGNED | SHORT:
      return self.readInt16()
    elif valtype is INT:
      return self.readUInt32()
    elif valtype is SIGNED | INT:
      return self.readInt32()
    elif valtype is FLOAT:
      return self.readFloat()
    elif valtype is DOUBLE:
      return self.readDouble()
