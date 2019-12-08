program_input='1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,10,1,19,1,6,19,23,1,23,13,27,2,6,27,31,1,5,31,35,2,10,35,39,1,6,39,43,1,13,43,47,2,47,6,51,1,51,5,55,1,55,6,59,2,59,10,63,1,63,6,67,2,67,10,71,1,71,9,75,2,75,10,79,1,79,5,83,2,10,83,87,1,87,6,91,2,9,91,95,1,95,5,99,1,5,99,103,1,103,10,107,1,9,107,111,1,6,111,115,1,115,5,119,1,10,119,123,2,6,123,127,2,127,6,131,1,131,2,135,1,10,135,0,99,2,0,14,0'


memory={}

def operation(memory, ip):
	(op, a, b, d) = memory[ip:ip+4]
	if op == 1:
		memory[d] = memory[a] + memory[b]
	elif op == 2:
		memory[d] = memory[a] * memory[b]
	elif op == 99:
		return None
	else:
		raise Error('illegal opcode')
		
	return ip + 4
	
	
def run(program, noun, verb):
	memory = program.copy()
	memory[1] = noun
	memory[2] = verb
	ip = 0
	while ip is not None:
		ip = operation(memory, ip)
		
	return memory[0]
		
		
program = [int(code) for code in program_input.split(',')]
result = run(program, 12, 2)

print(f'part1: {result}')

expected = 19690720

solutions = [ 100*noun + verb
              for verb in range(100)
              for noun in range(100)
              if run(program, noun, verb) == expected]
              
print(f'part2: {solutions}')
