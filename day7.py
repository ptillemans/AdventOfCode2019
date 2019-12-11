from intcode import IntCode
import pytest
import threading
import queue


def create_amps(source, configuration):
    amps = [IntCode(source) for _ in range(5)]
    for i in range(5):
        amps[i].input.put(configuration[i])
    amps[0].output = lambda x: amps[1].input.put(x)
    amps[1].output = lambda x: amps[2].input.put(x)
    amps[2].output = lambda x: amps[3].input.put(x)
    amps[3].output = lambda x: amps[4].input.put(x)
    amps[4].out_queue = queue.Queue()
    amps[4].output = lambda x: amps[i].out_queue.put(x)
    return amps

def thuster_output(source, configuration, signal):
    amps = create_amps(source, configuration)
    for amp in amps:
        amp.thread = threading.Thread(target=amp.run)
        amp.thread.start()
    amps[0].input.put(signal) 
    return amps[4].out_queue.get()
    
    
def all_configs():
   return ([a, b, c, d, e]
             for a in range(5)
             for b in range(5)
             for c in range(5)
             for d in range(5)
             for e in range(5))
             
             
with open('day7_input.txt', 'r') as f:
    day7_source = [int(s) for s in f.read().split(',')]
    
      
def find_max_signal():
    outputs = [(c, thuster_output(day7_source, c, 0)) for c in all_configs()]
    return max(outputs, key=lambda x: x[1])
    
    
def test_amplifier_1():
    source = [int(s) for s in '3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0'.split(',')]
    signal = thuster_output(source, [4, 3, 2, 1, 0], 0)    
    assert signal == 43210
    
    
def test_amplifier_2():
    source = [int(s) for s in '3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0'.split(',')]
    signal = thuster_output(source, [0, 1, 2, 3, 4], 0)
    assert signal == 54321
    

def test_amplifier_3():
    source = [int(s) for s in  '3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0'.split(',')]
    signal = thuster_output(source, [1, 0, 4, 3, 2], 0)
    assert signal == 65210
  
  
if __name__ == '__main__':
    pytest.main([__file__])
