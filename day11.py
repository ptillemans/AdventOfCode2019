from intcode import IntCode
from typing import Iterable, NamedTuple, MutableMapping
from enum import Enum
import threading


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
        panels[self.location] = color
        if turn == Turn.LEFT:
            self.direction = self.direction.turn_left()
        elif turn == Turn.RIGHT:
            self.direction = self.direction.turn_right()
        else:
            raise Day11Error('no such turn {turn}')

        self.location = take_step(self.location, self.direction)

        return self.panels.get(self.location, Color.BLACK)


    def loopback(self):
        new_color = self.computer.output.get()
        turn = self.computer.output.get()
        color = self.do_step(color, turn)
        self.computer.input.put(new_color)

    def run(self):
         loop_thread = threading.Thread(target=self.loopback)
         self.computer.input.put(Color.BLACK.value)
         self.computer.run()

def read_paint_code(src='day11_input.txt'):
    with open(src, 'r') as f:
        return f.read().strip().split(',')

def paint_program(code):
    robot = PaintRobot(code)
    painted_panels = robot.panels.keys()
    print(f"Panels: {painted_panels}")
    print(f"Total: {len(painted_panels)}")


paint_program(read_paint_code())
