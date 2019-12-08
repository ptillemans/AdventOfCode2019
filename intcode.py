from enum import Enum, IntFlag
import queue

class OpCode(Enum):
    ADD = 1
    MULT = 2
    IN = 3
    OUT = 4
    JMPIFT = 5
    JMPIFF = 6
    LT = 7
    EQL = 8
    END = 99
    
class OpFlags(IntFlag):
    IMMEDIATE = 1


class IntCodeError(Exception):
    pass

    
class IntCode:
    
    def __init__(self, program):
        self.name = 'IntCode'
        self.program = program.copy()
        self.memory = []
        self.input = queue.Queue()
        self.output = lambda x: print(f'OUT: {x}')
        self.ip = 0
        self.finished = False
        
    def fetch(self, memory, par, flags):
        if OpFlags.IMMEDIATE in flags:
            return par
        else:
            return memory[par]

    def operation(self, memory, ip):
        (op, fa, fb, _) = self.parse_operation(memory[ip])
        if op == OpCode.ADD:
            [a, b, to] = memory[ip+1:ip+4]
            v1 = self.fetch(memory, a, fa)
            v2 = self.fetch(memory, b, fb)
            result = v1 + v2
            memory[to] = result
            return ip + 4
        elif op == OpCode.MULT:
            [a, b, to] = memory[ip+1:ip+4]
            result = self.fetch(memory, a, fa) * self.fetch(memory, b, fb)
            memory[to] = result
            return ip + 4
        elif op == OpCode.IN:
            to = memory[ip+1]
            val = self.input.get()
            #print(f'IN ({self.name}): {val}')
            memory[to] = val
            return ip + 2
        elif op == OpCode.OUT:
            a = memory[ip+1]
            out = self.fetch(memory, a, fa)
            #print(f"OUT({self.name}): {out}")
            self.output(out)
            return ip + 2
        elif op == OpCode.JMPIFT:
            [a, to] = memory[ip+1:ip+3]
            if self.fetch(memory, a, fa):
                return self.fetch(memory, to, fb)
            else:
                return ip + 3
        elif op == OpCode.JMPIFF:
            [a, to] = memory[ip+1:ip+3]
            if not self.fetch(memory, a, fa):
                return self.fetch(memory, to, fb)
            else:
                return ip + 3
        elif op == OpCode.LT:
            [a, b, to] = memory[ip+1:ip+4]
            if self.fetch(memory, a, fa) < self.fetch(memory, b, fb):
                memory[to] = 1
            else:
                memory[to] = 0
            return ip + 4
        elif op == OpCode.EQL:
            [a, b, to] = memory[ip+1:ip+4]
            if self.fetch(memory, a, fa) == self.fetch(memory, b, fb):
                memory[to] = 1
            else:
                memory[to] = 0
            return ip + 4
        elif op == OpCode.END:
            return None
        else:
            raise IntCodeError(f'illegal opcode {op}')
        
    def parse_operation(self, op: int):
        (op1, op2, fa, fb, fc) = digits(op)
        return (OpCode(10*op2 + op1), OpFlags(fa), OpFlags(fb), OpFlags(fc))
    
    def run(self):
        self.finished = False
        memory = self.program.copy()
        ip = 0
        while ip is not None:
            # print(f'{ip}: {memory[ip:ip+4]}')
            ip = self.operation(memory, ip)
            
        self.finished = True

    
def digits(n):
    for _ in range(5):
        yield n % 10
        n //= 10
        
