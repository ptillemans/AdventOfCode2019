import pytest
from itertools import islice, count, takewhile
import functools
import math


puzzle_input = '''.##.#.#....#.#.#..##..#.#.
#.##.#..#.####.##....##.#.
###.##.##.#.#...#..###....
####.##..###.#.#...####..#
..#####..#.#.#..#######..#
.###..##..###.####.#######
.##..##.###..##.##.....###
#..#..###..##.#...#..####.
....#.#...##.##....#.#..##
..#.#.###.####..##.###.#.#
.#..##.#####.##.####..#.#.
#..##.#.#.###.#..##.##....
#.#.##.#.##.##......###.#.
#####...###.####..#.##....
.#####.#.#..#.##.#.#...###
.#..#.##.#.#.##.#....###.#
.......###.#....##.....###
#..#####.#..#..##..##.#.##
##.#.###..######.###..#..#
#.#....####.##.###....####
..#.#.#.########.....#.#.#
.##.#.#..#...###.####..##.
##...###....#.##.##..#....
..##.##.##.#######..#...#.
.###..#.#..#...###..###.#.
#..#..#######..#.#..#..#.#'''.splitlines()

def distance(loc):
    return max(abs(c) for c in loc)
    
    
def scan_sequence():
    "return a search spiral of location in increasing distance"
    for distance in count(1, 1):
        for y in range (-distance, distance):
            yield (-distance, y)
        for x in range (-distance, distance):
            yield (x, distance)
        for y in range (distance, -distance, -1):
            yield (distance, y)
        for x in range (distance, -distance, -1):
            yield (x, -distance)
            

def occlusion_step(loc, p):
    '''return the repeat step for occlusions by p'''
    delta = (p[0] - loc[0], p[1] - loc[1])
    cd = math.gcd(delta[0], delta[1])
    return (delta[0]//cd, delta[1]//cd)


def occlusions(grid_map, loc, p):
    "return all asteroids made unobservable by asteroid on location"
    to_abs = lambda p : rel_to_abs(loc, p)
    is_rock = lambda p: is_asteroid(grid_map, p)
    is_point = lambda x : is_on_map(grid_map, x)
    
   
    ks = count(1,1)
    delta = occlusion_step(loc, p)
    occ_point = lambda k: (p[0]+k*delta[0], p[1] + k*delta[1])
    occluded_points = list(takewhile(is_point, map(occ_point, ks)))
    return filter(is_rock, occluded_points)     
                       
def observable_asteroids(grid_map, loc):
    "return list of observable grid points"
    max_distance = max(loc[0], loc[1], len(grid_map[0]) - loc[0], len(grid_map) - loc[1])
    is_within_distance = lambda p: distance(p) <= max_distance
    to_abs = lambda p: rel_to_abs(loc, p)
    has_asteroid = lambda p: is_asteroid(grid_map, p)
    occluded = set(loc)
    asteroids = list(filter(has_asteroid,
                  map(to_abs, 
                      takewhile(is_within_distance, scan_sequence()))))
    for p in asteroids:
        occluded = occluded.union(occlusions(grid_map, loc, p))
        if p not in occluded:
            yield p
    
          
def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))
    
    
def rel_to_abs(origin, loc):
    return(origin[0] + loc[0], origin[1] + loc[1])
    
    
def is_on_map(map, loc):
    (x, y) = loc
    return  x >= 0 and y >= 0 and x < len(map[0]) and y < len(map)

def is_asteroid(map, loc):
    (x, y) = loc
    if is_on_map(map, loc):
        return map[y][x] == '#'
    else:
        return None
    
def asteroid_locations(grid_map):
    width = len(grid_map[0])
    height = len(grid_map)
    return ((x,y) for y in range(height) for x in range(width) if is_asteroid(grid_map, (x,y)))


def location_scores(grid_map):
    return [(loc,len(list(observable_asteroids(grid_map, loc))))
            for loc in asteroid_locations(grid_map)]

def best_location(grid_map):
    number_observable_asteroids = lambda score: score[1]
    scores = location_scores(grid_map)
    return max(scores, key=number_observable_asteroids)


def laser_angle(origin, p):
    ''' return the angle from the north '''
    (x0, y0) = origin
    (x, y) = p
    radians = math.atan2(x - x0, y0 - y)
    return radians if radians >= 0 else radians + 2 * math.pi

def remove_asteroid(grid_map, loc):
    (x,y) = loc
    row = list(grid_map[y])
    row[x] = '.'
    grid_map[y]="".join(row)

def fire_orders(grid_map, loc):
    new_map = grid_map.copy()
    remove_asteroid(new_map, loc)
    asteroids = set(asteroid_locations(new_map))
    while asteroids:
        observables = list(observable_asteroids(new_map, loc))
        observables.sort(key=lambda x: laser_angle(loc, x))
        for asteroid in observables:
            remove_asteroid(new_map, asteroid)
            yield asteroid
        asteroids = set(asteroid_locations(new_map))
#---------------------------------------------------------------------------------------

mini_map = '''
.#..#
.....
#####
....#
...##'''.strip().splitlines()

ex1_map = '''
......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####'''.strip().splitlines()

ex2_map = '''.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##'''.splitlines()


def test_scan_seq():
    actual = list(take(10, scan_sequence()))
    expected = [(-1,-1), (-1, 0), (-1,1), (0,1), (1,1), (1,0), (1, -1), (0, -1), (-2, -2), (-2, -1)]
    assert actual == expected


def test_occlusions():
    actual = list(occlusions(mini_map, (3,4), (2,2)))
    expected = [(1,0)]
    assert actual == expected
  
def test_occlusions_1():
    actual = list(occlusions(mini_map, (4,3), (4,2)))
    expected = [(4,0)]
    assert actual == expected 

def test_distance():
    assert distance((1, -2)) == 2
    
    
def test_rel_to_abs():
    origin = (1,2)
    assert rel_to_abs(origin, (1,1)) == (2,3)
    
    
def test_is_asteroid():
    assert is_asteroid(mini_map, (3,4))
    assert not is_asteroid(mini_map, (2, 1))
    
def test_observable_asteroids():
    observables = observable_asteroids(mini_map, (3,4))
    assert len(list(observables)) == 8

def test_example_1():
    observables = observable_asteroids(ex1_map, (5,8))
    assert len(list(observables)) == 33

def test_find_best_location():
    actual = best_location(mini_map)
    assert actual == ((3,4), 8)
    
def test_find_best_location_ex1():
    actual = best_location(ex1_map)
    assert actual == ((5,8), 33)
    
#def test_find_best_location_ex2():
#    actual = best_location(ex2_map)
#    assert actual == ((11,13), 210)
    
def test_angle():
    assert laser_angle((11,13), (11,12)) == 0
    assert laser_angle((11,13), (12,13)) == math.pi/2
    assert laser_angle((11,13), (11,14)) == math.pi
    assert laser_angle((11,13), (10,13)) == 3*math.pi/2


def test_fire_order():
    locations = list(fire_orders(ex2_map, (11,13)))
    assert locations[0] == (11,12)
    assert locations[1] == (12,1)
    # The 3rd asteroid to be vaporized is at 12,2.
    assert locations[2] == (12,2)
    # The 10th asteroid to be vaporized is at 12,8.
    # The 20th asteroid to be vaporized is at 16,0.
    # The 50th asteroid to be vaporized is at 16,9.
    # The 100th asteroid to be vaporized is at 10,16.
    # The 199th asteroid to be vaporized is at 9,6.
    # The 200th asteroid to be vaporized is at 8,2.
    # The 201st asteroid to be vaporized is at 10,9.
    assert locations[200] == (10,9)
    # The 299th and final asteroid to be vaporized is at 11,1.
    assert locations[298] == (11,1)

if __name__ == '__main__':
    pytest.main([__file__])
    (location, score) = best_location(puzzle_input) 
    print(location, score)
    zap_orders = list(fire_orders(puzzle_input, location))
    print(zap_orders[199])