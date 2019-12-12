from intcode import IntCode
from typing import NamedTuple, Enumeration


class Point(NamedTuple):
    x : int
    y : int

class Direction(Enumeration):
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


class Day11Error(BaseException):
    pass

panel_color = {}



def take_step(loc: Point, dir: Direction) -> Point:
    (x, y) = loc
    if dir == Direction.UP:
        return (x, y + 1)
    elif dir == Direction.DOWN:
        return (x, y - 1)
    elif dir == Direction.RIGHT:
        return(x + 1, y)
    elif dir == Direction.LEFT:
        return(x - 1, y)
    else:
        raise Day11Error('no such direction: {self}')
