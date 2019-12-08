from intcode import IntCode
import queue


with open('day5_input.txt', 'r') as f:
	code = [int(t) for t in  f.read().split(',')]
	
print(code)

#code = [3,3,1108,-1,8,3,4,3,99]

out_queue = queue.Queue()
prg = IntCode(code)
prg.output = lambda x: out_queue.put(x)
prg.input.put(5)
prg.run()
result = out_queue.get()
print(f'result:{result}')
