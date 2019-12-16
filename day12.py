import numpy as np
import re
import operator
import functools
import math

import pytest
import matplotlib.pyplot as plt

day12_input = '''<x=-9, y=-1, z=-1>
<x=2, y=9, z=5>
<x=10, y=18, z=-12>
<x=-6, y=15, z=-7>'''

class Moon:
    
    def __init__(self, location):
        self.location = np.array(location)
        self.start_location = np.copy(self.location)
        self.velocity = np.array([0, 0, 0])
        self.start_velocity = np.copy(self.velocity)

    def update_velocity(self, moons):
        for moon in moons:
            self.velocity += np.sign(moon.location - self.location)

    def update_location(self):
        self.location += self.velocity
    
    @property
    def potential_energy(self):
        return np.sum(np.abs(self.location))

    @property
    def kinetic_energy(self):
        return np.sum(np.abs(self.velocity))

    @property
    def total_energy(self):
        return self.potential_energy * self.kinetic_energy

    @property
    def is_in_start_state(self):
        return np.logical_and(
            self.location == self.start_location, 
            self.velocity == self.start_velocity)

    def __eq__(self, other):
        return np.array_equal(self.location, other.location) \
            and np.array_equal(self.velocity, other.velocity)

    def __str__(self):
        return f'Moon(pos={self.location}, vel={self.velocity})'


INPUT_REGEX=re.compile('<x=(-?\\d+), y=(-?\\d+), z=(-?\\d+)>')


def parse_moon(line):
    result = re.match(INPUT_REGEX, line)
    return Moon(np.array([int(m) for m in result.group(1,2,3)]))


def parse_moons(text):
    return [parse_moon(line) for line in text.splitlines()]


def advance_time(moons):
    for moon in moons:
        moon.update_velocity(moons)
    for moon in moons:
        moon.update_location()

def find_periods(moons):
    periods = [None, None, None]
    period = 0
    while not all(periods):
        period += 1
        advance_time(moons)
        for dim in range(3):
            if periods[dim]:
                continue
            same = all(moon.is_in_start_state[dim] for moon in moons)
            if same:
                periods[dim] = period
    
    return periods


def total_period(periods):
    naive_period = functools.reduce(operator.mul, periods) 

    revs = [naive_period // moon_period for moon_period in periods]

    gcd = functools.reduce(math.gcd, revs)
    return naive_period // gcd


#---------------------------------------------------------------------------

test_input = '''<x=-1, y=0, z=2>
<x=2, y=-10, z=-7>
<x=4, y=-8, z=8>
<x=3, y=5, z=-1>'''

test_long_cycle = '''<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>'''

snapshots_long_cycle = '''After 0 steps:
pos=<x= -8, y=-10, z=  0>, vel=<x=  0, y=  0, z=  0>
pos=<x=  5, y=  5, z= 10>, vel=<x=  0, y=  0, z=  0>
pos=<x=  2, y= -7, z=  3>, vel=<x=  0, y=  0, z=  0>
pos=<x=  9, y= -8, z= -3>, vel=<x=  0, y=  0, z=  0>

After 10 steps:
pos=<x= -9, y=-10, z=  1>, vel=<x= -2, y= -2, z= -1>
pos=<x=  4, y= 10, z=  9>, vel=<x= -3, y=  7, z= -2>
pos=<x=  8, y=-10, z= -3>, vel=<x=  5, y= -1, z= -2>
pos=<x=  5, y=-10, z=  3>, vel=<x=  0, y= -4, z=  5>

After 20 steps:
pos=<x=-10, y=  3, z= -4>, vel=<x= -5, y=  2, z=  0>
pos=<x=  5, y=-25, z=  6>, vel=<x=  1, y=  1, z= -4>
pos=<x= 13, y=  1, z=  1>, vel=<x=  5, y= -2, z=  2>
pos=<x=  0, y=  1, z=  7>, vel=<x= -1, y= -1, z=  2>

After 30 steps:
pos=<x= 15, y= -6, z= -9>, vel=<x= -5, y=  4, z=  0>
pos=<x= -4, y=-11, z=  3>, vel=<x= -3, y=-10, z=  0>
pos=<x=  0, y= -1, z= 11>, vel=<x=  7, y=  4, z=  3>
pos=<x= -3, y= -2, z=  5>, vel=<x=  1, y=  2, z= -3>

After 40 steps:
pos=<x= 14, y=-12, z= -4>, vel=<x= 11, y=  3, z=  0>
pos=<x= -1, y= 18, z=  8>, vel=<x= -5, y=  2, z=  3>
pos=<x= -5, y=-14, z=  8>, vel=<x=  1, y= -2, z=  0>
pos=<x=  0, y=-12, z= -2>, vel=<x= -7, y= -3, z= -3>

After 50 steps:
pos=<x=-23, y=  4, z=  1>, vel=<x= -7, y= -1, z=  2>
pos=<x= 20, y=-31, z= 13>, vel=<x=  5, y=  3, z=  4>
pos=<x= -4, y=  6, z=  1>, vel=<x= -1, y=  1, z= -3>
pos=<x= 15, y=  1, z= -5>, vel=<x=  3, y= -3, z= -3>

After 60 steps:
pos=<x= 36, y=-10, z=  6>, vel=<x=  5, y=  0, z=  3>
pos=<x=-18, y= 10, z=  9>, vel=<x= -3, y= -7, z=  5>
pos=<x=  8, y=-12, z= -3>, vel=<x= -2, y=  1, z= -7>
pos=<x=-18, y= -8, z= -2>, vel=<x=  0, y=  6, z= -1>

After 70 steps:
pos=<x=-33, y= -6, z=  5>, vel=<x= -5, y= -4, z=  7>
pos=<x= 13, y= -9, z=  2>, vel=<x= -2, y= 11, z=  3>
pos=<x= 11, y= -8, z=  2>, vel=<x=  8, y= -6, z= -7>
pos=<x= 17, y=  3, z=  1>, vel=<x= -1, y= -1, z= -3>

After 80 steps:
pos=<x= 30, y= -8, z=  3>, vel=<x=  3, y=  3, z=  0>
pos=<x= -2, y= -4, z=  0>, vel=<x=  4, y=-13, z=  2>
pos=<x=-18, y= -7, z= 15>, vel=<x= -8, y=  2, z= -2>
pos=<x= -2, y= -1, z= -8>, vel=<x=  1, y=  8, z=  0>

After 90 steps:
pos=<x=-25, y= -1, z=  4>, vel=<x=  1, y= -3, z=  4>
pos=<x=  2, y= -9, z=  0>, vel=<x= -3, y= 13, z= -1>
pos=<x= 32, y= -8, z= 14>, vel=<x=  5, y= -4, z=  6>
pos=<x= -1, y= -2, z= -8>, vel=<x= -3, y= -6, z= -9>

After 100 steps:
pos=<x=  8, y=-12, z= -9>, vel=<x= -7, y=  3, z=  0>
pos=<x= 13, y= 16, z= -3>, vel=<x=  3, y=-11, z= -5>
pos=<x=-29, y=-11, z= -1>, vel=<x= -3, y=  7, z=  4>
pos=<x= 16, y=-13, z= 23>, vel=<x=  7, y=  1, z=  1>
'''

SNAPSHOT_REGEX=re.compile(
    'pos=<x=\\s*(-?\\d+), y=\\s*(-?\\d+), z=\\s*(-?\\d+)>'
    ', vel=<x=\\s*(-?\\d+), y=\\s*(-?\\d+), z=\\s*(-?\\d+)>')

def parse_snapshots(text):
    pos = {}
    vel = {}
    for line in [l for l in text.splitlines() if l]:
        if line.startswith('After'):
            time = int(line.split(' ')[1])
            pos[time] = []
            vel[time] = []
            moon = 0
        else:
            result = re.match(SNAPSHOT_REGEX, line)
            pos[time].append(np.array([int(p) for p in result.group(1,2,3)]))
            vel[time].append(np.array([int(v) for v in result.group(4,5,6)]))
            moon = moon + 1

    return (pos, vel)


@pytest.fixture
def moons1():
    return parse_moons(test_input)


@pytest.fixture
def moons2():
    return parse_moons(test_long_cycle)


def test_parse_moon():
    line = '<x=-6, y=15, z=-7>'
    actual = parse_moon(line)
    expected = Moon([-6, 15, -7])
    assert actual == expected


def test_parse_moons(moons1):
    assert len(moons1) == 4
    assert moons1[0] == Moon([-1, 0, 2])
    assert moons1[3] == Moon([3, 5, -1])


def test_advance_time(moons1):
    advance_time(moons1)
    assert np.array_equal(moons1[0].location, np.array([2, -1, 1]))
    assert np.array_equal(moons1[0].velocity, np.array([3, -1, -1]))
    assert np.array_equal(moons1[3].location, np.array([2, 2, 0]))
    assert np.array_equal(moons1[3].velocity, np.array([-1, -3, 1]))


def test_advance_time_2(moons2):
    (pos_snap, vel_snap) = parse_snapshots(snapshots_long_cycle);
    for i in range(101):
        if i % 10 == 0:
            for moon in range(4):
                assert np.array_equal(moons2[moon].location, pos_snap[i][moon])
                assert np.array_equal(moons2[moon].velocity, vel_snap[i][moon])
        advance_time(moons2)

def test_cycle(moons1):
    for _ in range(2772):
        advance_time(moons1)
    for i in range(4):
        assert np.array_equal(moons1[i].location, moons1[i].start_location)
        assert np.array_equal(moons1[i].velocity, moons1[i].start_velocity)


def test_energy(moons1):
    for _ in range(10):
        advance_time(moons1)

    assert moons1[0].potential_energy == 6
    assert moons1[0].kinetic_energy == 6
    assert moons1[0].total_energy == 36


def test_total_periods():
    assert total_period([6, 8, 4]) == 24


def test_periods(moons1):
    periods = find_periods(moons1)
    assert total_period(periods) == 2772


def test_periods_long(moons2):
    periods = find_periods(moons2)
    assert total_period(periods) == 4686774924


if __name__ == '__main__':
    pytest.main([__file__])

    moons = parse_moons(day12_input)
    energies = np.zeros([1000, 5])
    for i in range(1000):
        advance_time(moons)
        energies[i][:] = [i] + [moon.potential_energy for moon in moons]

    total_energies = [moon.total_energy for moon in moons]
    print(f"Total Energy af 1000 ticks : {sum(total_energies)}")

    periods = find_periods(parse_moons(day12_input))
    total_period = total_period(periods)
    print(f'Periods: {total_period}, {periods}')
