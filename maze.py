import enum
from typing import Tuple
from pyrsistent import m


class MazeError(Exception):
    pass


class Direction(enum.Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4

    def move(self, location):
        if self == Direction.NORTH:
            return location[0], location[1] - 1
        elif self == Direction.WEST:
            return location[0] - 1, location[1]
        elif self == Direction.SOUTH:
            return location[0], location[1] + 1
        elif self == Direction.EAST:
            return location[0] + 1, location[1]
        else: 
            raise MazeError('No such direction')

    def back(self):
        if self == Direction.NORTH:
            return Direction.SOUTH
        elif self == Direction.WEST:
            return Direction.EAST
        elif self == Direction.SOUTH:
            return Direction.NORTH
        elif self == Direction.EAST:
            return Direction.WEST
        else: 
            raise MazeError('No such direction')




class Maze():

    def __init__(self, wall_tile='#', floor_tile='.', start_tile='@'):
        self.tiles = m()
        self.wall_tile = wall_tile
        self.floor_tile = floor_tile
        self.start_tile = start_tile

    def get_tile(self, loc: Tuple[int, int]):
        (x,  y) = loc
        row = self.tiles.get(y, m())
        return row.get(x, ) 


    def update_tile(self, loc: Tuple[int, int], tile):
        (x, y) = loc
        row = self.tiles.get(y, m())
        if tile != self.wall_tile:
            self.tiles = self.tiles.set(y,row.set(x,tile))
        elif x in row:
            self.tiles = self.tiles.set(y, row.remove(x))
        if tile == self.start_tile:
            self.start_location = loc

    def bounds(self):
        x_min = min(min(row.keys()) for row in self.tiles.values())
        y_min = min(self.tiles)
        x_max = max(max(row.keys()) for row in self.tiles.values())
        y_max = max(self.tiles)
        return (x_min, y_min, x_max, y_max)

    def neighbors(self, current):
            return [loc 
                for dir in Direction 
                for loc in [dir.move(current)]
                if self.get_tile(loc)]

    def show_maze(self):
        (x_min, y_min, x_max, y_max) = self.bounds()
        for y in range(y_min, y_max + 1):
            line = f"{y:+02d}"
            for x in range(x_min, x_max + 1):
                line = line + str(self.tiles[y].get(x,' '))
            yield line

    def print_maze(self):
        for line in self.show_maze():
            print(line)

    def remove_dead_ends(self):
        has_deadend = True
        (x0, y0, x1, y1) = self.bounds()
        while has_deadend:
            has_deadend = False
            for x in range(x0, x1+1):
                for y in range(y0, y1+1):
                    ns = self.neighbors((x,y))
                    if len(ns) == 1 and self.get_tile((x,y)) == self.floor_tile:
                        self.update_tile((x,y), self.wall_tile)
                        has_deadend = True
            