import pytest
import scipy.ndimage as ndi
import numpy as np
import numpy.ma as ma
import functools as ft
import itertools as it
import re
from collections import defaultdict


KERNEL = np.array([
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0],
    ])

def generation(data):
    neighbors= ndi.convolve(data, KERNEL, mode='constant', cval=0)
    has_bugs = data == 1

    dies = np.logical_and(has_bugs, neighbors != 1)

    spawns = np.logical_and(~has_bugs, np.logical_or(neighbors == 1, neighbors == 2))

    result = ma.MaskedArray(data, mask=dies).filled(0)
    return ma.MaskedArray(result, mask=spawns).filled(1)

def biodiversity_rating(data):
    bits = reversed(data.reshape((25,)))
    return ft.reduce(lambda a, x: a*2 + x, bits)

def parse_bugs(data):
    xs = [1 if c == '#' else 0
        for line in data.splitlines()
        for c in line]
    return np.array(xs).reshape((5, 5))

RE_DEPTH = re.compile(r'Depth (-?\d+):')
def parse_populations(data):
    lines = data.splitlines()
    pos = 0
    populations = create_populations({})
    while pos < len(lines):
        m = re.match(RE_DEPTH, lines[pos])
        if not m:
            pos += 1
            continue  
        depth = int(m.group(1)) 
        populations[depth] = parse_bugs("\n".join(lines[pos+1:pos+6]))
        pos += 6
    return populations

def create_populations(data):
    '''return a virtual limitless stack of populations'''
    def empty_pop():
        pop = np.zeros((5, 5))
        return pop

    populations = defaultdict(empty_pop)
    for k in data.keys():
        populations[k] = np.copy(data[k])
    return populations

def layer_generation(old, new, layer):
    for y in range(5):
        for x in range(5):
            if (x, y) == (2, 2):
                continue
            nbr = list(neighbors(x, y, layer))
            nr_bugs_around = sum(old[z][y][x] for (x, y, z) in nbr) 
            if old[layer][y][x] and nr_bugs_around != 1: 
                new[layer][y][x] = 0 
            if not old[layer][y][x] and (nr_bugs_around == 1 or nr_bugs_around == 2):
                new[layer][y][x] = 1 

def neighbors(x, y, layer):
    return filter(is_valid, all_neighbors(x, y, layer))

def all_neighbors(x, y, layer): 
    yield (x, y - 1, layer) 
    yield (x + 1, y, layer) 
    yield (x, y + 1, layer) 
    yield (x - 1, y, layer) 
    if x == 0: 
        yield(1, 2, layer - 1) 
    if x == 4: 
        yield(3, 2, layer - 1)
    if y == 0:
        yield(2, 1, layer - 1)
    if y == 4:
        yield(2, 3, layer - 1)
    if (x, y) == (2, 1):
        yield from ((k, 0, layer + 1) for k in range(5))
    if (x, y) == (3, 2):
        yield from ((4, k, layer + 1) for k in range(5))
    if (x, y) == (2, 3):
        yield from ((k, 4, layer + 1) for k in range(5))
    if (x, y) == (1, 2):
        yield from ((0, k, layer + 1) for k in range(5))



def is_valid(loc):
    (x, y, _) = loc
    return x in range(5) \
        and y in range(5)\
        and not (x == 2 and y == 2)
    

                
def generation_in_folded_spacetime(populations):
    new_populations = create_populations(populations)
    layers = sorted(list(populations.keys()))
    layers.append(min(layers) - 1)
    layers.append(max(layers) + 1)
    for layer in layers:
        layer_generation(populations, new_populations, layer)
    return new_populations  


def count_bugs(populations):
    return sum(np.count_nonzero(populations[layer]) for layer in populations)

def print_populations(populations):
    for z in sorted(populations):
        pop = populations[z]
        if np.count_nonzero(pop) > 0:
            print(f'Depth: {z}')
            for y in range(5):
                for x in range(5):
                    if (x, y) == (2, 2):
                        print('?', end='')
                        continue
                    print('#' if pop[y][x] else '.', end='')
                print()
            print()


def print_two_populations(pop1, pop2):
    layers = set(pop1).union(pop2)
    for z in sorted(layers):
        p1 = pop1[z]
        p2 = pop2[z]
        if np.count_nonzero(p1) or np.count_nonzero(p2):
            print(f'Depth: {z}')
            for y in range(5):
                for x in range(5):
                    if (x, y) == (2, 2):
                        print('?? ', end='')
                        continue
                    print('#' if p1[y][x] else '.', end='')
                    print('#' if p2[y][x] else '.', end=' ')
                print()
            print()

#============================================================

@pytest.fixture
def initial_population():
    return parse_bugs('''.....
.....
.....
#....
.#...''')

def test_biodiversity(initial_population):
    actual = biodiversity_rating(initial_population)
    assert actual == 2129920


TEST_POPULATIONS='''Depth -5:
..#..
.#.#.
..?.#
.#.#.
..#..

Depth -4:
...#.
...##
..?..
...##
...#.

Depth -3:
#.#..
.#...
..?..
.#...
#.#..

Depth -2:
.#.##
....#
..?.#
...##
.###.

Depth -1:
#..##
...##
..?..
...#.
.####

Depth 0:
.#...
.#.##
.#?..
.....
.....

Depth 1:
.##..
#..##
..?.#
##.##
#####

Depth 2:
###..
##.#.
#.?..
.#.##
#.#..

Depth 3:
..###
.....
#.?..
#....
#...#

Depth 4:
.###.
#..#.
#.?..
##.#.
.....

Depth 5:
####.
#..#.
#.?#.
####.
.....'''


def test_populations():
    initial_population = parse_bugs('''....#
#..#.
#.?##
..#..
#....''')
    populations = create_populations({0: initial_population})
    expected = parse_populations(TEST_POPULATIONS)
    minutes = 0
    for _ in range(10):
        print(f'After {minutes}:')
        minutes += 1
        print_populations(populations)
        new_pop = generation_in_folded_spacetime(populations)
        populations=new_pop

    #print_populations(populations)
    print_two_populations(expected, populations)
    for layer in expected:
        e = expected[layer]
        a = populations[layer]
        assert np.array_equal(e, a)


def test_one_generation(initial_population):
    expected = generation(initial_population)
    pops = create_populations({0:initial_population})
    actual = generation_in_folded_spacetime(pops)
    assert np.array_equal(actual[0], expected)

def test_upward():
    pop = parse_bugs('''..#..
.....
#.?.#
.....
..#..''')
    expected = parse_bugs('''.....
..#..
.#?#.
..#..
.....''')
    pops = create_populations({0: pop})
    pops = generation_in_folded_spacetime(pops)
    actual = pops[-1]
    assert np.array_equal(expected, actual)

def test_downward():
    pop = parse_bugs('''.....
..#..
.#?#.
..#..
.....''')
    expected = parse_bugs('''#####
#...#
#.?.#
#...#
#####''')
    pops = create_populations({0: pop})
    pops = generation_in_folded_spacetime(pops)
    assert np.array_equal(expected, pops[1])


def test_symmetry():
    pop = parse_bugs('''.....
..#..
.#.#.
..#..
.....''')
    pops = create_populations({0: pop})
    for i in range(10):
        pops = generation_in_folded_spacetime(pops)
        for (layer, x, y) in it.product(pops, range(3), range(3)):
            if (x, y) == (2, 2):
                continue
            assert pops[layer][y][x] == pops[layer][y][4 - x]
            assert pops[layer][y][x] == pops[layer][4 - y][x]
            assert pops[layer][y][x] == pops[layer][4 - y][4 - x]

            

# =====================================================

def part1(day24_input):
    # Part 1
    population = day24_input
    ratings = set()
    while True:
        population = generation(population)
        rating = biodiversity_rating(population)
        if rating in ratings:
            print(f'first duplicate: {rating}')
            break
        ratings.add(rating)


def part2(day24_input):
    populations = create_populations({0: day24_input})
    for _ in range(200):
        populations = generation_in_folded_spacetime(populations)
    
    nr_bugs = count_bugs(populations)

    print(f'number bugs: {nr_bugs}')


def print_neighbors():
    for (x, y) in it.product(range(5), range(5)):
        print(f'{x, y}: {list(neighbors(x, y, 0))}')

if __name__ == '__main__':
    pytest.main([__file__])

    day24_input = parse_bugs('''.##..
##.#.
##.##
.#..#
#.###''')

    part1(day24_input)

    # Part 2
    part2(day24_input)

    #print_neighbors()