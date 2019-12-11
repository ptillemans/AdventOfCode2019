
import pytest
import queue

from intcode import *

def parse(source):
    return [int(s.strip()) for s in source.split(',')]
        

def test_day5():
    code = parse('''3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,
999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99''')
    out_queue = queue.Queue()
    prg = IntCode(code)
    prg.output = lambda x: out_queue.put(x)
    prg.input.put(5)
    prg.run()
    assert 999 == out_queue.get()
    prg.input.put(8)
    prg.run()
    assert 1000 == out_queue.get()
    prg.input.put(9)
    prg.run()
    assert 1001 == out_queue.get()

           
def test_day5_full():
    with open('day5_input.txt', 'r') as f:
	    code = [int(t) for t in  f.read().split(',')]
	

    out_queue = queue.Queue()
    prg = IntCode(code)
    prg.output = lambda x: out_queue.put(x)
    prg.input.put(5)
    prg.run()
    result = out_queue.get()
    assert result == 15586959


def test_day_9():
    code = parse('109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99')
    out_queue = queue.Queue()
    prg = IntCode(code)
    prg.output = lambda x: out_queue.put(x)
    
    prg.run()
    
    for c in code:
        assert c == out_queue.get()


def test_day_9_2():
    code = parse('1102,34915192,34915192,7,4,7,99,0')
    out_queue = queue.Queue()
    prg = IntCode(code)
    prg.output = lambda x: out_queue.put(x)
    
    prg.run()

    out = out_queue.get()

    assert len(str(out)) == 16


def test_day_9_3():
    code = parse('104,1125899906842624,99')
    out_queue = queue.Queue()
    prg = IntCode(code)
    prg.output = lambda x: out_queue.put(x)
    
    prg.run()

    out = out_queue.get()

    assert out == 1125899906842624


def test_day_9_boost():
    with open('day9_input.txt', 'r') as f:
        code = [int(s.strip()) for s in f.read().split(',')]

    out_queue = queue.Queue()
    prg = IntCode(code)
    prg.output = lambda x: out_queue.put(x)
    prg.input.put(1)
    prg.run()

    assert out_queue.get() == 3780860499
    assert out_queue.empty()

if __name__ == "__main__":
    pytest.main([__file__])
