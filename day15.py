import pytest
import intcode
import enum
import queue
import heapq
import threading
from collections import defaultdict
from typing import Tuple
import sys 

sys.setrecursionlimit(10000)

class DroidError(Exception):
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
            raise DroidError('No such direction')

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
            raise DroidError('No such direction')


class Tile(enum.Enum):
    WALL = 0
    FLOOR = 1
    OXYGEN_SYSTEM = 2


class Deck():

    SYMBOLS = {
        Tile.WALL: '#', 
        Tile.FLOOR: '.',
        Tile.OXYGEN_SYSTEM: 'O',
        None: ' '
    }
    def __init__(self):
        self.tiles = defaultdict(lambda: defaultdict(lambda: None))

    def get_tile(self, loc: Tuple[int, int]):
        (x,  y) = loc
        return self.tiles[y][x]

    def update_tile(self, loc: Tuple[int, int], tile: Tile):
        (x, y) = loc
        self.tiles[y][x] = tile

    def bounds(self):
        x_min = min(min(self.tiles[row].keys()) for row in self.tiles)
        y_min = min(self.tiles)
        x_max = max(max(self.tiles[row].keys()) for row in self.tiles)
        y_max = max(self.tiles)
        return (x_min, y_min, x_max, y_max)

    def show_deck(self):
        (x_min, y_min, x_max, y_max) = self.bounds()
        for y in range(y_min, y_max + 1):
            line = f"{y:+02d}"
            for x in range(x_min, x_max + 1):
                line = line + Deck.SYMBOLS[self.tiles[y][x]]
            yield line


    
class RepairDroid():

    brain: intcode.IntCode

    def __init__(self):
        self.brain = intcode.IntCode.create_from_source('day15_input.txt')
        self.deck = Deck()
        self.location = (0, 0)


    def take_step(self, direction: Direction) -> bool:
        '''move the droid and return true if actually moved'''
        new_location = direction.move(self.location)
        self.brain.input.put(direction.value)
        tile = Tile(self.brain.output.get())
        self.deck.update_tile(new_location, tile)
        if tile == Tile.WALL:
            return False
        else:
            self.location = new_location
            if tile == Tile.OXYGEN_SYSTEM:
                self.oxygen_system_location = self.location
            return True


    def wander(self, direction: Direction):
        if self.take_step(direction):
            for dir in Direction:
                if not self.deck.get_tile(dir.move(self.location)):
                    self.wander(dir)
            self.take_step(direction.back())
        #self.show_maze()


    def map_maze(self):
        prg = threading.Thread(target=self.brain.run)
        prg.start()
        self.deck.update_tile(self.location, Tile.FLOOR)
        for dir in Direction:
            self.wander(dir)
        self.brain.finished = True
        prg.join()

    def show_maze(self):
        for line in self.deck.show_deck():
            print(line)

    def shortest_path_to(self, goal: Tuple[int, int]):
        h = lambda loc: abs(goal[0] - loc[0]) + abs(goal[1] - loc[1])

        start = self.location
        open_set = []
        heapq.heappush(open_set, (h(start), start))

        came_from = {}
        
        # For node n, gScore[n] is the cost of the cheapest path from start to n currently known.
        g_score = defaultdict(lambda: 1000000)
        g_score[start] = 0

        # For node n, fScore[n] := gScore[n] + h(n).
        f_score = defaultdict(lambda: 1000000)
        f_score[start] = h(start)

        while open_set:
            (_, current) =  heapq.heappop(open_set)
            if current == goal:
                return g_score[current]

            for neighbor in self.neighbors(current):
                # (current,neighbor) is the weight of the edge from current to neighbor
                # tentative_gScore is the distance from start to the neighbor through current
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score[neighbor]:
                    # This path to neighbor is better than any previous one. Record it!
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + h(neighbor)
                    if neighbor not in {x[1] for x in open_set}:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # Open set is empty but goal was never reached
        return None   

    def neighbors(self, current):
            return [loc 
                for dir in Direction 
                for loc in [dir.move(current)]
                if self.deck.get_tile(loc) != Tile.WALL]

    def fill_with_oxygen(self):
        tiles_filled = set()
        next_tiles = {self.oxygen_system_location}
        minute = 0
        while next_tiles:
            minute += 1
            tiles_filled |= next_tiles
            next_tiles = {loc 
                for tile in next_tiles
                for loc in self.neighbors(tile)
                if loc not in tiles_filled}
            print(f't({minute}): {next_tiles}')
        return minute - 1

        

if __name__ == '__main__':
    droid = RepairDroid()
    droid.map_maze()
    droid.show_maze()
    print('Done wandering.')
    print(f'Oxygen system at {droid.oxygen_system_location}')
    droid.location=(0, 0)
    distance = droid.shortest_path_to(droid.oxygen_system_location)
    print(f'Shortest path: {distance}')

    time_to_fill = droid.fill_with_oxygen()
    print(f'Time to fill deck: {time_to_fill}')






                

    
    

