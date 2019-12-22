import intcode
import queue
import threading

class SpringDroid():

    def __init__(self):
        self.computer = intcode.IntCode.create_from_source('day21_input.txt')

    def __enter__(self):
        self.prg = threading.Thread(target=self.computer.run)
        self.prg.start()
        return self

    def __exit__(self, _type, _value, _tb):
        self.computer.finished = True
        self.prg.join()

    def show_output(self):
        while True:
            try:
                c = self.computer.output.get(True, 10)
                if c < 128:
                    print(chr(c), sep='', end='')
                else:
                    print(f'output: {c}')
            except queue.Empty:
                break

    def input_line(self, line):
        print(f'In: {line}')
        for c in line:
            self.computer.input.put(ord(c))
        self.computer.input.put(10)

spring_droid = SpringDroid()
with spring_droid as droid:
    droid.show_output()
    droid.input_line('OR A T')
    droid.input_line('AND A T')
    droid.input_line('AND B T')
    droid.input_line('AND C T')
    droid.input_line('NOT T J')
    droid.input_line('AND D J')
    droid.input_line('WALK')
    droid.show_output()

part2_input = '''OR A T
AND A T
AND B T
AND C T
NOT T J
AND D J
NOT I T
NOT T T
OR F T
AND E T
OR H T
AND T J
RUN
'''

with spring_droid as droid:
    droid.show_output()
    for line in part2_input.splitlines():
        droid.input_line(line)
    droid.show_output()

print()

