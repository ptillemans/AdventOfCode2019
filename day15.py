import pytest
import intcode
import enum
import queue
import threading
from collections import defaultdict
from typing import Tuple


class Direction(enum.Enum):
    NORTH = 1
    WEST = 2
    SOUTH = 3
    EAST = 4

    def move(self, location):
        return location[0] + self.value[0], location[1] + self.value[1]

    def back(self):
        back_dir = (-self.value[0], -self,value[1])
        return Direction(back_dir)


class Tile(enum.Enum):
    WALL = 0
    FLOOR = 1
    OXYGEN_SYSTEM = 2


class Deck():

    def __init__(self):
        self.tiles = defaultdict(lambda: defaultdict(lambda: None))

    def get_tile(self, loc: Tuple[int, int]):
        (x,  y) = loc
        return self.tiles[y][x]

    def update_tile(self, loc: Tuple[int, int], tile: Tile):
        (x, y) = loc
        self.tiles[y][x] = tile

    
class RepairDroid():

    brain: intcode.IntCode

    def __init__(self):
        self.brain = intcode.IntCode.create_from_source('day15_input.txt')
        self.deck = Deck()
        self.location = (0, 0)
        self.prg = threading.Thread(target=self.brain.run)
        self.prg.start()


    def take_step(self, direction: Direction) -> bool:
        '''move the droid and return true if actually moved'''
        print('send instruction: {direction}')
        self.brain.input.put(direction)
        print('await response')
        tile = Tile(self.brain.output.get())
        print('got {tile} as response')
        if tile != Tile.WALL:
            self.location = dir.move(self.location)
            print(f'Moved to {self.location}')
            moved = True
        else:
            print(f'Hit a wall at {self.location}')
            moved = False
        self.deck.update_tile(loc, tile)
        return moved


    def wander(self, direction: Direction):
        print(f'wander from {self.location} to {direction}')
        if self.take_step(direction):
            for dir in Direction:
                new_location = dir.move(self.location)
                if self.deck.get_tile(new_location):                    
                    continue
                self.wander(dir)
            self.take_step(direction.back())

        

if __name__ == '__main__':
    droid = RepairDroid()
    for dir in Direction:
        print(f'Going {dir}')
        droid.wander(dir)
    print('Done wandering.')







                

    
    

