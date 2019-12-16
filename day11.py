from intcode import IntCode
from typing import Iterable, NamedTuple, MutableMapping
from enum import Enum
import threading
import queue
import matplotlib.pyplot as plt

class Point(NamedTuple):
    x : int
    y : int

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def turn_right(self):
        if self == Direction.LEFT:
            return Direction.UP
        else:
            return Direction(self.value + 1)

    def turn_left(self):
        if self == Direction.UP:
            return Direction.LEFT
        else:
            return Direction(self.value - 1)


class Color(Enum):
    BLACK = 0
    WHITE = 1


class Turn(Enum):
    LEFT = 0
    RIGHT = 1


class Day11Error(BaseException):
    pass



def take_step(loc: Point, dir: Direction) -> Point:
    (x, y) = loc
    if dir == Direction.UP:
        return Point(x, y + 1)
    elif dir == Direction.DOWN:
        return Point(x, y - 1)
    elif dir == Direction.RIGHT:
        return Point(x + 1, y)
    elif dir == Direction.LEFT:
        return Point(x - 1, y)
    else:
        raise Day11Error('no such direction: {self}')


class PaintRobot():

    computer: IntCode
    location: Point
    direction: Direction
    panels: MutableMapping[Point, Color]

    def __init__(self, code: Iterable[int]):
        self.computer = IntCode(code)
        self.location = Point(0, 0)
        self.direction = Direction.UP
        self.panels = {}

    def do_step(self, color: Color, turn: Turn) -> Color:
        self.panels[self.location] = color
        if turn == Turn.LEFT:
            self.direction = self.direction.turn_left()
        elif turn == Turn.RIGHT:
            self.direction = self.direction.turn_right()
        else:
            raise Day11Error('no such turn {turn}')

        self.location = take_step(self.location, self.direction)

        return self.panels.get(self.location, Color.BLACK)


    def loopback(self):
        print('Starting loopback')
        while not self.computer.finished:
            try:
                new_color = Color(self.computer.output.get(True, 1))
                turn = Turn(self.computer.output.get(True, 1))
                color = self.do_step(new_color, turn)
                #print(f'{new_color}, {turn} -> {self.location} - {color}')
                self.computer.input.put(color.value)
            except queue.Empty:
                print(f'timeout.')
        print('closing loopback thread.')

    def run(self, start_color: Color):
        loop_thread = threading.Thread(target=self.loopback)
        loop_thread.start()
        self.computer.input.put(start_color.value)
        self.computer.run()


def read_paint_code(src='day11_input.txt'):
    with open(src, 'r') as f:
        return [int(opcode) for opcode in f.read().strip().split(',')]


def paint_program(code):
    robot = PaintRobot(code)
    robot.run(Color.BLACK)
    report_panels(robot)
    robot = PaintRobot(code)
    robot.run(Color.WHITE)
    plot_panels(robot)


def report_panels(robot: PaintRobot):
    painted_panels = robot.panels.keys()
    print(f"Panels: {painted_panels}")
    print(f"Total: {len(painted_panels)}")


def plot_panels(robot: PaintRobot):
    painted_panels = robot.panels.keys()
    xs = [t[0] for t in painted_panels]
    ys = [t[1] for t in painted_panels]
    colors = [robot.panels[panel].value for panel in painted_panels]
    plt.scatter(xs, ys, c=colors)
    plt.show()


if __name__ == '__main__':
    paint_program(read_paint_code())
