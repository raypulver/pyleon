from io import Parser, Encoder
from null import Null

def dumps(obj):
  return Encoder(obj).writeSI().writeOLI().writeData().export()

def loads(string):
  return Parser(string).parseSI().parseOLI().parseValue()

class Channel():
  def __init__(self, spec):
    self.spec = spec
  def dumps(self, obj):
    return Encoder(obj).setSpec(self.spec).writeData().export()
  def loads(self, string):
    return Parser(string).setSpec(self.spec).parseValueWithSpec()
