import pytest
from intcode import IntCode
from typing import Tuple
from collections import defaultdict
import enum
from day15 import Direction, DroidError
from itertools import groupby, count
from threading import Thread


SCAFFOLD = '#'
SPACE = '.'

CHAR_TO_DIR = {
    '^': Direction.NORTH,
    '>': Direction.EAST,
    '<': Direction.WEST,
    'v': Direction.SOUTH
}

COMPASS = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]

class Scaffold():


    def __init__(self):
        self.tiles = defaultdict(lambda: defaultdict(lambda: '.'))

    def get_tile(self, loc: Tuple[int, int]):
        (x,  y) = loc
        return self.tiles[y][x]

    def update_tile(self, loc: Tuple[int, int], tile):
        (x, y) = loc
        self.tiles[y][x] = tile

    def bounds(self):
        x_min = min(min(self.tiles[row].keys()) for row in self.tiles)
        y_min = min(self.tiles)
        x_max = max(max(self.tiles[row].keys()) for row in self.tiles)
        y_max = max(self.tiles)
        return (x_min, y_min, x_max, y_max)

    def show_scaffold(self):
        (x_min, y_min, x_max, y_max) = self.bounds()
        for y in range(y_min, y_max + 1):
            line = f"{y:02d}: "
            for x in range(x_min, x_max + 1):
                line = line + (self.tiles[y][x] or ' ')
            yield line


class AftScaffoldingControl:
    def __init__(self, mode=1):
        self.brain = IntCode.create_from_source('day17_input.txt')
        self.brain.program[0] = mode
        self.prg = Thread(target=self.brain.run)
        self.prg.start()
        self.scaffold = Scaffold()
        self.droid_location = None


    def read_camera(self,):
        output = self.brain.output
        y = 0
        x = 0
        self.scaffold = Scaffold()
        
        while not output.empty() or not self.brain.finished:
            pixel = output.get()
            if pixel == 10:
                y += 1
                x = 0
            else:
                tile = chr(pixel)
                self.scaffold.update_tile((x,y),chr(pixel))
                if tile in {'^', '>', '<', 'v'}:
                    self.droid_location = (x, y)
                    self.droid_direction = CHAR_TO_DIR[tile]
                x += 1

        return bool(self.scaffold.tiles)

    def neighbors(self, current):
            return [loc 
                for dir in Direction 
                for loc in [dir.move(current)]
                if self.scaffold.get_tile(loc) != SPACE]


    def crossings(self):
        (x_min, y_min, x_max, y_max) = self.scaffold.bounds()
        return [(x,y) 
            for y in range(y_min, y_max + 1)
            for x in range(x_min, x_max + 1)
            if len(self.neighbors((x,y))) == 4]

    def wander_scaffold(self):
        loc = self.droid_location
        visited = defaultdict(lambda: None)
        dir = self.droid_direction
        while(loc):
            visited[loc] = True
            next_loc = dir.move(loc)
            if self.scaffold.get_tile(next_loc) != SPACE:
                yield dir
                loc = next_loc
            else:
                poss_dirs = [d 
                    for d in Direction
                    for l in [d.move(loc)]
                    if self.scaffold.get_tile(l) != SPACE
                    if not visited[d.move(l)]]
                if poss_dirs:
                    dir = poss_dirs[0]
                else:
                    loc = None

    def walk_scaffold(self, instruction):
        cs = instruction + 'n\n'

        for c in cs:
            self.brain.input.put(ord(c))
        while not self.brain.finished or not self.brain.output.empty():
            line = ''
            while True:
                inp = self.brain.output.get(True, 10)
                if inp == 10:
                    print(line)
                    break
                if inp < 256:
                    line = line + chr(inp)
                else:
                    print(f'output:{inp}')
                    break


def path_to_instructions(path, init_dir):
    dir = init_dir
    for (l, new_dir) in path:
        turn = dirs_to_turn(dir, new_dir)
        yield turn
        yield l
        dir = new_dir



def dirs_to_turn(dir1, dir2):
    OUTCOME = ['F', 'R', 'B', 'L']
    i1 = COMPASS.index(dir1)
    i2 = COMPASS.index(dir2)
    di = (i2 - i1) % 4
    return OUTCOME[di]


# -----------------------------------------------


if __name__ == '__main__':
    pytest.main([__file__])

    ascii = AftScaffoldingControl()
    ascii.read_camera()
    for l in ascii.scaffold.show_scaffold():
        print(l)

    total = 0
    for c in ascii.crossings():
        (x, y) = c
        s = x * y
        print(f'({x}, {y} -> {s})')
        total += s

    print(f'part1: {total}')

    dirs = list(ascii.wander_scaffold())

    path = list(map(lambda x: (sum(1 for _ in x[1]), x[0]), groupby(dirs)))

    print(path)

    instructions = list(path_to_instructions(path, ascii.droid_direction))

    print(",".join(str(x) for x in instructions))

    main = '''A,A,B,C,A,C,A,B,C,B
R,12,L,8,R,6
R,12,L,6,R,6,R,8,R,6
L,8,R,8,R,6,R,12
'''
    vacuum_droid = AftScaffoldingControl(mode=2)
    dust = vacuum_droid.walk_scaffold(main)


