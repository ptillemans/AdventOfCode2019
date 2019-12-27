import pytest
import operator
import string
from collections import defaultdict
from heapq import heappush, heappush, heappop

DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

def read_raw(data:str):
    data = data.replace(' ', '#') # make spaces impassible
    return [s.strip() for s in data.splitlines()]


def find_connectors(data):
    labels = defaultdict(set)
    nrows = len(data)
    ncols = len(data[0])
    for row in range(nrows-1):
        for col in range(ncols-1):
            pos = None
            outer = True
            c1 = data[row][col]
            c2 = data[row][col + 1]
            c3 = data[row + 1][col]
            if c1 not in string.ascii_uppercase \
                or (c2 not in string.ascii_uppercase 
                    and c3 not in string.ascii_uppercase):
                continue
            label = c1 + c2 if c2 != '#' else c1 + c3
            if row == 0:
                pos = (col, row + 2)
            elif row == nrows - 2:
                pos = (col, row - 1)
            elif col == 0:
                pos = (col + 2, row)
            elif col == ncols - 2:
                pos = (col - 1, row)
            elif c3 in string.ascii_uppercase:
                outer = False
                if row < nrows/2:
                    pos = (col, row)
                else:
                    pos = (col, row + 1)
            elif c2 in string.ascii_uppercase:
                outer = False
                if col < ncols/2:
                    pos = (col, row)
                else:
                    pos = (col + 1, row)
                    
            labels[label].add((pos, outer))
            (x, y) = pos
            data[y] =data[y][:x] + '.' + data[y][x+1:]
    return dict(labels)
            

def parse_maze(maze):
    connectors = find_connectors(maze)
    edges = defaultdict(lambda:defaultdict(lambda:(1000000, (0, 0))))
    con_locations = {k:(v, o) 
        for (v, locs) in connectors.items()
        for (k, o) in locs}

    start_locations = con_locations.keys()
    for start_loc in start_locations:
        seen = set()
        stack = []
        heappush(stack, (0, start_loc))
        while stack:
            (d, loc) = heappop(stack)
            seen.add(loc)
            if loc != start_loc and loc in con_locations:
                [(l1, d1), (l2, d2)] = sorted((con_locations[l][0],level_shift(con_locations, l)) 
                                    for l in [start_loc, loc])
                edges[l1][l2] = (min(d, edges[l1][l2][0]), (d1, d2))
                continue
            new_locs = [(x, y) for d in DIRS for (x, y) in [t_add(loc, d)] 
                        if maze[y][x] == '.' and (x, y) not in seen]
            for nloc in new_locs:
                heappush(stack,(d + 1, nloc))
    
    return edges


def level_shift(labels, location):
    (label, is_outer) = labels[location]
    if label in ['AA', 'ZZ']:
        return 0
    else:
        return -1 if is_outer else 1

def t_add(t1, t2):
    return tuple(map(operator.add, t1, t2))



def shortest_path(maze, start, finish):
    stack = []
    seen = set()
    heappush(stack, (0, [start]))
    while stack:
        (d, path) = heappop(stack)
        loc = path[-1]
        if loc == finish:
            return (d, path)
        seen.add(loc)
        for nloc in [l for l in neighbors(maze, loc) if l not in seen]:
            heappush(stack, (d + distance(maze, loc, nloc), path + [nloc]))



def distance(maze, l1, l2):
    return maze[l1][l2][0] if l1 <= l2 else maze[l2][l1][0]

def neighbors(maze, loc):
    direct = list(maze[loc].keys())
    indirect = [k for k in maze if loc in maze[k]]
    return direct + indirect


def shortest_path_recursive(maze, start, finish):
    stack = []
    seen = set()
    heappush(stack, (0, 0, 0, [(start, 0)]))
    while stack:
        (d, lvl, ldl, path) = heappop(stack)
        loc = path[-1][0]
        if lvl == 0 and loc == finish:
            print(f'Path recursive : {path}')
            return (d, path)
        seen.add((loc, lvl))
        candidates = [(l, dl) 
                    for l in neighbors(maze, loc) 
                    for dl in [level_change(maze, loc, l)]
                    if (l, lvl + d) not in seen
                    if not(l in {'AA', 'ZZ'} and lvl != 0)
                    if level_change(maze, l, loc) == -ldl ]
        for (nloc, dl) in candidates:
            nlvl = lvl + dl
            if lvl >= 0:
                heappush(stack, (d + distance(maze, loc, nloc), 
                            nlvl, dl,
                            path + [(nloc, nlvl)]))
    return (-1, [])

def level_change(maze, l1, l2):
    return maze[l1][l2][1][1] if l1 <= l2 else maze[l2][l1][1][0]


#######################################


SMALL_TEST_INPUT = '''         A           
         A           
  #######.#########  
  #######.........#  
  #######.#######.#  
  #######.#######.#  
  #######.#######.#  
  #####  B    ###.#  
BC...##  C    ###.#  
  ##.##       ###.#  
  ##...DE  F  ###.#  
  #####    G  ###.#  
  #########.#####.#  
DE..#######...###.#  
  #.#########.###.#  
FG..#########.....#  
  ###########.#####  
             Z       
             Z       '''

LARGER_INPUT = '''                   A               
                   A               
  #################.#############  
  #.#...#...................#.#.#  
  #.#.#.###.###.###.#########.#.#  
  #.#.#.......#...#.....#.#.#...#  
  #.#########.###.#####.#.#.###.#  
  #.............#.#.....#.......#  
  ###.###########.###.#####.#.#.#  
  #.....#        A   C    #.#.#.#  
  #######        S   P    #####.#  
  #.#...#                 #......VT
  #.#.#.#                 #.#####  
  #...#.#               YN....#.#  
  #.###.#                 #####.#  
DI....#.#                 #.....#  
  #####.#                 #.###.#  
ZZ......#               QG....#..AS
  ###.###                 #######  
JO..#.#.#                 #.....#  
  #.#.#.#                 ###.#.#  
  #...#..DI             BU....#..LF
  #####.#                 #.#####  
YN......#               VT..#....QG
  #.###.#                 #.###.#  
  #.#...#                 #.....#  
  ###.###    J L     J    #.#.###  
  #.....#    O F     P    #.#...#  
  #.###.#####.#.#####.#####.###.#  
  #...#.#.#...#.....#.....#.#...#  
  #.#####.###.###.#.#.#########.#  
  #...#.#.....#...#.#.#.#.....#.#  
  #.###.#####.###.###.#.#.#######  
  #.#.........#...#.............#  
  #########.###.###.#############  
           B   J   C               
           U   P   P               '''

PART2_INPUT = '''             Z L X W       C                 
             Z P Q B       K                 
  ###########.#.#.#.#######.###############  
  #...#.......#.#.......#.#.......#.#.#...#  
  ###.#.#.#.#.#.#.#.###.#.#.#######.#.#.###  
  #.#...#.#.#...#.#.#...#...#...#.#.......#  
  #.###.#######.###.###.#.###.###.#.#######  
  #...#.......#.#...#...#.............#...#  
  #.#########.#######.#.#######.#######.###  
  #...#.#    F       R I       Z    #.#.#.#  
  #.###.#    D       E C       H    #.#.#.#  
  #.#...#                           #...#.#  
  #.###.#                           #.###.#  
  #.#....OA                       WB..#.#..ZH
  #.###.#                           #.#.#.#  
CJ......#                           #.....#  
  #######                           #######  
  #.#....CK                         #......IC
  #.###.#                           #.###.#  
  #.....#                           #...#.#  
  ###.###                           #.#.#.#  
XF....#.#                         RF..#.#.#  
  #####.#                           #######  
  #......CJ                       NM..#...#  
  ###.#.#                           #.###.#  
RE....#.#                           #......RF
  ###.###        X   X       L      #.#.#.#  
  #.....#        F   Q       P      #.#.#.#  
  ###.###########.###.#######.#########.###  
  #.....#...#.....#.......#...#.....#.#...#  
  #####.#.###.#######.#######.###.###.#.#.#  
  #.......#.......#.#.#.#.#...#...#...#.#.#  
  #####.###.#####.#.#.#.#.###.###.#.###.###  
  #.......#.....#.#...#...............#...#  
  #############.#.#.###.###################  
               A O F   N                     
               A A D   M                     '''
            

@pytest.fixture
def small_input():
    return read_raw(SMALL_TEST_INPUT)

@pytest.fixture
def larger_input():
    return read_raw(LARGER_INPUT)

@pytest.fixture
def part2_input():
    return read_raw(PART2_INPUT)

def test_find_connectors(small_input):
    actual = find_connectors(small_input)
    expected = {
        'AA':{((9,2), True)}, 
        'BC': {((2,8), True),((9,7), False)},
        'DE': {((2,13), True), ((7,10), False)},
        'FG': {((11,11), False), ((2,15), True)},
        'ZZ': {((13,16), True)}
        }
    assert actual == expected


def test_parse_maze(small_input):
    actual = parse_maze(small_input)
    expected = {
        'AA': {'BC': (5, (0, 1)), 'ZZ': (26, (0, 0)), 'FG': (31, (0, 1)),},
        'BC': {'DE': (7, (-1, 1)), 'FG': (34, (1, 1)), 'ZZ': (29, (1, 0)),},
        'DE': {'FG': (4, (-1, -1))},
        'FG': {'ZZ': (7, (1, 0))},
    }
    assert actual == expected

def test_shortest_path(small_input):
    maze = parse_maze(small_input)
    (distance, path) = shortest_path(maze, 'AA', 'ZZ')
    assert distance == 23
    assert path == ['AA', 'BC', 'DE', 'FG', 'ZZ']


def test_shortest_path_recursive(part2_input):
    maze = parse_maze(part2_input)
    (distance, path) = shortest_path_recursive(maze, 'AA', 'ZZ')
    assert distance == 396

if __name__ == '__main__':
    pytest.main([__file__])

    with open('day20_input.txt', 'r') as f:
        maze = parse_maze(read_raw(f.read()))

    (dist, path) = shortest_path(maze, 'AA', 'ZZ')
    print(f'Part1: distance {dist} found for path {path}')

    (dist2, path2) = shortest_path_recursive(maze, 'AA', 'ZZ')
    print(f'Part2: distance {dist2} found for path {path2}')