import queue
import intcode

def day9_input():
    with open('day9_input.txt', 'r') as f:
        return [int(s.strip()) for s in f.read().split(',')]
    

def run_boost(in_val):
    code = day9_input()
    out_queue = queue.Queue()
    prg = intcode.IntCode(code)
    prg.output = lambda x: out_queue.put(x)
    prg.input.put(in_val)
    prg.run()

    while not out_queue.empty():
        print(f'OUT: {out_queue.get()}')

print('Self Test:')
run_boost(1)
print('Distress Location:')
run_boost(2)