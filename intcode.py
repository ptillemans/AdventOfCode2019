from enum import Enum, IntEnum
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
        self.output = queue.Queue()
        self.ip = 0
        self.finished = False
        self.rp = 0

    def target(self, par, flags):
        if flags == OpFlags.POSITIONAL:
            return par
        elif flags == OpFlags.RELATIVE:
            return self.rp + par
        else:
            raise IntCodeError('Invalid opcode flags : {flags}')

    def fetch(self, par, flags):
        if OpFlags.IMMEDIATE == flags:
            return par
        else:
            return self.memory[self.target(par, flags)]

    def store(self, par, flags, value):
        self.memory[self.target(par, flags)] = value

    def operation(self, ip):
        (op, fa, fb, fc) = self.parse_operation(self.memory[ip])
        if op == OpCode.ADD:
            [a, b, to] = self.memory[ip+1:ip+4]
            result = self.fetch(a, fa) + self.fetch(b, fb)
            self.store(to, fc, result)
            return ip + 4
        elif op == OpCode.MULT:
            [a, b, to] = self.memory[ip+1:ip+4]
            result = self.fetch(a, fa) * self.fetch(b, fb)
            self.store(to, fc, result)
            return ip + 4
        elif op == OpCode.IN:
            to = self.memory[ip+1]
            result = self.input.get()
            self.store(to, fa, result)
            return ip + 2
        elif op == OpCode.OUT:
            a = self.memory[ip+1]
            out = self.fetch(a, fa)
            self.output.put(out)
            return ip + 2
        elif op == OpCode.JMPIFT:
            [a, to] = self.memory[ip+1:ip+3]
            return self.fetch(to, fb) if self.fetch(a, fa) else ip + 3
        elif op == OpCode.JMPIFF:
            [a, b] = self.memory[ip+1:ip+3]
            return self.fetch(b, fb) if not self.fetch(a, fa) else ip + 3
        elif op == OpCode.LT:
            [a, b, c] = self.memory[ip+1:ip+4]
            result = 1 if self.fetch(a, fa) < self.fetch(b, fb) else 0
            self.store(c, fc, result)
            return ip + 4
        elif op == OpCode.EQL:
            [a, b, c] = self.memory[ip+1:ip+4]
            result = 1 if self.fetch(a, fa) == self.fetch(b, fb) else 0
            self.store(c, fc, result)
            return ip + 4
        elif op == OpCode.RPA:
            a = self.memory[ip+1]
            self.rp += self.fetch(a, fa)
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
        self.memory = self.program.copy() + [0] * 2**16
        self.ip = 0
        self.rp = 0
        while self.ip is not None:
            self.ip = self.operation(self.ip)

        self.finished = True

    @classmethod
    def create_from_source(cls, filename) -> IntCode:
        with open(filename, 'r') as f:
            code = [int(s.strip()) for s in f.read().split(',')]
            return IntCode(code)


def digits(n):
    for _ in range(5):
        yield n % 10
        n //= 10
