from enum import Enum, IntEnum
import queue
import numpy as np

class OpCode(Enum):
    ADD = 1
    MULT = 2
    IN = 3
    OUT = 4
    JMPIFT = 5
    JMPIFF = 6
    LT = 7
    EQL = 8
    RPA = 9
    END = 99
    
class OpFlags(IntEnum):
    POSITIONAL = 0
    IMMEDIATE = 1
    RELATIVE = 2


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
        self.rp = 0
        
    def fetch(self, memory, par, flags):
        if OpFlags.POSITIONAL == flags:
            return memory[par]
        elif OpFlags.IMMEDIATE == flags:
            return par
        elif OpFlags.RELATIVE == flags:
            return memory[self.rp + par]
        else:
            raise IntCodeError('Invalid opcode flags : {flags}')

    def store(self, memory, par, flags, value):
        if OpFlags.POSITIONAL == flags:
            memory[par] = value
        elif OpFlags.RELATIVE == flags:
            memory[self.rp + par] = value
        else:
            raise IntCodeError('Invalid opcode flags : {flags}')

    def operation(self, memory, ip):
        (op, fa, fb, fc) = self.parse_operation(memory[ip])
        if op == OpCode.ADD:
            [a, b, to] = memory[ip+1:ip+4]
            v1 = self.fetch(memory, a, fa)
            v2 = self.fetch(memory, b, fb)
            result = v1 + v2
            self.store(memory, to, fc, result)
            return ip + 4
        elif op == OpCode.MULT:
            [a, b, to] = memory[ip+1:ip+4]
            result = self.fetch(memory, a, fa) * self.fetch(memory, b, fb)
            self.store(memory, to, fc, result)
            return ip + 4
        elif op == OpCode.IN:
            to = memory[ip+1]
            result = self.input.get()
            #print(f'IN ({self.name}): {val}')
            self.store(memory, to, fa, result)
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
            if fc == OpFlags.RELATIVE:
                to = self.rp + to
            if self.fetch(memory, a, fa) < self.fetch(memory, b, fb):
                memory[to] = 1
            else:
                memory[to] = 0
            return ip + 4
        elif op == OpCode.EQL:
            [a, b, to] = memory[ip+1:ip+4]
            if fc == OpFlags.RELATIVE:
                to = self.rp + to
            if self.fetch(memory, a, fa) == self.fetch(memory, b, fb):
                memory[to] = 1
            else:
                memory[to] = 0
            return ip + 4
        elif op == OpCode.RPA:
            a = memory[ip+1]
            self.rp += self.fetch(memory, a, fa)
            return ip + 2
        elif op == OpCode.END:
            return None
        else:
            raise IntCodeError(f'illegal opcode {op}')
        
    def parse_operation(self, op: int):
        (op1, op2, fa, fb, fc) = digits(op)
        return (OpCode(10*op2 + op1), OpFlags(fa), OpFlags(fb), OpFlags(fc))
    
    def run(self):
        self.finished = False
        memory = self.program.copy() + [0] * 2**16
        self.ip = 0
        self.rp = 0
        while self.ip is not None:
            # print(f'{ip}: {memory[ip:ip+4]}')
            self.ip = self.operation(memory, self.ip)
            
        self.finished = True

    
def digits(n):
    for _ in range(5):
        yield n % 10
        n //= 10
        
