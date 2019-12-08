import pytest


def calculate_orbits(orbit_map):
    return list(find_orbits(orbit_map, 'COM'))

def parse_orbit(line):
    return tuple(line.split(')'))

def find_orbits(orbit_map, root):
    satellites = orbit_map.get(root, [])
    for s in satellites:
        for o in find_orbits(orbit_map, s):
            yield o 
            if o[0] == s:
                yield (root, o[1])
        yield (root, s)


def parse_orbits(lines):
    orbit_map = {}
    for (o1, o2) in (parse_orbit(line) for line in lines.splitlines()):
        satellites = orbit_map.get(o1, set())
        satellites.add(o2)
        orbit_map[o1] = satellites
    return orbit_map


def reverse_map(orbits_map):
    return {v:k for (k,vals) in orbits_map.items() for v in vals}
    
def path_to_com(reverse_map, obj):
    yield obj
    while obj != 'COM':
        obj = reverse_map[obj]
        yield obj
    
def path_between(reverse_map, start, to):
    path_from = list(path_to_com(reverse_map, start))
    path_to = list(path_to_com(reverse_map, to))
    while path_from and path_to and path_from[-1] == path_to[-1]:
        common = path_from.pop()
        path_to.pop()
    path_from.reverse()
    return path_to[:-1] + [common] + path_from
    
#-----------------------------------------------------------------------

test_input = '''COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L'''
            
            
def test_parse_line():
    assert parse_orbit('AAA)BBB') == ('AAA', 'BBB')


def test_parse_orbits():
    source = 'AAA)BBB'
    orbit_map = parse_orbits(source)
    assert len(orbit_map) == 1
    assert orbit_map['AAA'] == {'BBB'}
    
    
def test_trivial_system():
    input = 'COM)B'
    orbits = calculate_orbits(input)

    assert orbits == 1

def test_find_orbits():
    source = 'COM)A\nCOM)B'
    orbit_map = parse_orbits(source)
    orbits = find_orbits(orbit_map, 'COM')
    assert len(list(orbits)) == 2
    
def test_sample_orbit():
    input = '''COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L'''

    om = parse_orbits(input)
    orbits = calculate_orbits(om)

    assert len(orbits) == 42


if __name__ == '__main__':
    pytest.main([__file__])
    
    with open('day6_input.txt') as f:
        orbit_map = parse_orbits(f.read())
        orbits = calculate_orbits(orbit_map)
        print(len(orbits))
        rev_map=reverse_map(orbit_map)
        path = path_between(rev_map, 'YOU', 'SAN')
        print(path)
        print(len(path))
    
