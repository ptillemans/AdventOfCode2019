import unittest
import pytest
import queue

from intcode import *
        

def test_day5():
    code = [int(s) for s in '''3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,
999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99'''.split(',')]
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
           
   
           
        
if __name__ == "__main__":
    pytest.main([__file__])
