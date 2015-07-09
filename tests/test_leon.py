from pyleon import leon
from pyleon import leontypes

def test_object():
  obj = {'a': 1, 'b': 2}
  assert leon.loads(leon.dumps(obj)) == obj

def test_double():
  assert leon.loads(leon.dumps(2.2222222)) == 2.2222222
  assert leon.loads(leon.dumps(-2.2222)) == -2.2222

def test_float():
  assert leon.loads(leon.dumps(0.5)) == 0.5

def test_array():
  obj = [{'a': 2.2, 'b': 500, 'c': 10000}, {'a': 2.5, 'b': 400, 'c': 100}, {'a': 2.6, 'b': 7.7, 'c': 10}]
  assert leon.loads(leon.dumps(obj)) == obj

def test_channel():
  channel = leon.Channel([{ 'a': leontypes.DOUBLE, 'b': leontypes.SHORT, 'c': leontypes.SHORT }])
  obj = [{'a': 2.2, 'b': 500, 'c': 10000}, {'a': 2.5, 'b': 400, 'c': 100}, {'a': 2.6, 'b': 300, 'c': 10}]
  assert channel.loads(channel.dumps(obj))
