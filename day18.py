import pytest
import maze
import string
import networkx as nx
import matplotlib.pyplot as plt
from itertools import permutations

def parse_vault_map(data):
    vault_maze = maze.Maze('#')
    lines = [s.strip() for s in data.splitlines()]

    for y in range(len(lines)):
        for x in range(len(lines[y])):
            vault_maze.update_tile((x,y), lines[y][x])

    return maze_to_graph(vault_maze)


def find_reachable_things(maze, start, tiles_filled=None):
    if tiles_filled is None:
        tiles_filled = set()
    tiles_filled |= {start}
    next_tiles = {start}
    keys = set()
    doors = set()
    distance = 0
    while next_tiles:
        distance += 1
        tiles_filled |= next_tiles
        next_tiles = {loc 
            for tile in next_tiles
            for loc in maze.neighbors(tile)
            if loc not in tiles_filled}
        keys |= {(l, distance) for l in next_tiles if maze.get_tile(l) in string.ascii_lowercase}
        doors |= {(l, distance) for l in next_tiles if maze.get_tile(l) in string.ascii_uppercase}
        next_tiles -= {d[0] for d in keys | doors}
    return (keys, doors)

def maze_to_graph(maze, G=None, start=None, visited=None):
    if start is None:
        start = maze.start_location
    if G is None:
        G = nx.Graph()
    if visited is None:
        visited = set()
    start_id = maze.get_tile(start)
    (keys, doors) = find_reachable_things(maze, start, visited)
    for thing in keys | doors:
        id = maze.get_tile(thing[0])
        location = thing[0]
        G.add_node(id, location=location)
        G.add_edge(start_id, id, distance=thing[1])
        maze_to_graph(maze, G, location, visited)

    return G

def show_graph(G):
    plt.subplot(1,1,1)
    edge_labels = {e:G.edges[e]['distance'] for e in G.edges}
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()

def is_path_clear(path, missing_keys):
    keys_needed = {d.lower() for d in path if d in string.ascii_uppercase}
    clear = not keys_needed.intersection(missing_keys)
    return clear

def is_key(x):
    return x in string.ascii_lowercase

def is_door(x):
    return x not in string.ascii_lowercase
    
def is_open(x, missing_keys):
    is_closed = is_door(x) and (x.lower() in missing_keys)
    return not is_closed

def is_open_door(x, missing_keys):
    return is_door(x) and is_open(x, missing_keys)

def reachable_missing_keys(G, current, missing_keys):
    '''neighborng keys  of open doors are also neigbors'''
    all_neighbors = set(nx.all_neighbors(G, current))
    visited = {current}
    while True:
        other_nodes = {x for x in all_neighbors if x not in missing_keys} - visited
        visited |= all_neighbors
        if not other_nodes:
            break
        for n in {x for x in other_nodes if is_open(x, missing_keys)}:
            all_neighbors |= set(nx.all_neighbors(G, n))
    rmk = {x for x in all_neighbors if x in missing_keys}
    # print(f'{current}  : {rmk}  | {missing_keys}')
    return rmk
    

def best_key_sequence(G, loc, missing_keys, distance, min_distance):
    if not missing_keys:
        print(f'distance: {distance}/{min_distance}')
        return distance
    reachable_keys = reachable_missing_keys(G, loc, missing_keys)
    for key in reachable_keys:
        nkeys = missing_keys - {key}
        hop = nx.shortest_path_length(G, source=loc, target=key, weight='distance')
        if distance + hop < min_distance:
            ndist = best_key_sequence(G, key, nkeys, distance + hop, min_distance)
            if ndist < min_distance:
                min_distance = ndist
        else:
            print('aborted')
    return min_distance
            

def collect_keys(maze):
    #show_graph(G)
    keys = {n for n in maze.nodes if n in string.ascii_lowercase}
    min_distance = 1000000000
   
    return best_key_sequence(maze, '@', keys, 0, min_distance)

#-------------------------------------------------------


def test_missing_lazy_keys_1():
    maze_text = '''#########
#b.A.@.a#
#########'''
    m = parse_vault_map(maze_text)
    actual = reachable_missing_keys(m, '@', {'a', 'b'})
    assert actual == {'a'}

def test_missing_lazy_keys_2():
    maze_text = '''#########
#b.A.@.a#
#########'''
    m = parse_vault_map(maze_text)
    actual = reachable_missing_keys(m, 'a', {'b'})
    assert actual == {'b'}


def test_simple():
    maze_text = '''#########
#b.A.@.a#
#########'''
    m = parse_vault_map(maze_text)
    steps = collect_keys(m)
    assert steps == 8

def test_larger():
    maze_text = '''########################
#f.D.E.e.C.b.A.@.a.B.c.#
######################.#
#d.....................#
########################'''
    m = parse_vault_map(maze_text)
    steps = collect_keys(m)
    assert steps == 86

def test_example3():
    maze_text = '''########################
#...............b.C.D.f#
#.######################
#.....@.a.B.c.d.A.e.F.g#
########################'''
    m = parse_vault_map(maze_text)
    steps = collect_keys(m)
    assert steps == 132

@pytest.mark.skip
def test_example3():
    maze_text = '''#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################'''
    m = parse_vault_map(maze_text)
    steps = collect_keys(m)
    assert steps == 136

def play_area():
    day18_maze = parse_vault_map(day18_input)
    day18_maze.print_maze()
    #day18_maze.remove_dead_ends()
    #day18_maze.print_maze()

    (keys, doors) = find_reachable_things(day18_maze, (40, 40))

    print(f'keys: {keys}')
    print(list(map(day18_maze.get_tile, (k[0] for k in keys))))
    print(f'doors: {doors}')
    print(list(map(day18_maze.get_tile, (d[0] for d in doors))))

    matching_pairs = [(key, door)
        for key in keys
        for door in doors
        if day18_maze.get_tile(key[0]).upper() == day18_maze.get_tile(door[0])]

    print(matching_pairs)

    G = maze_to_graph(day18_maze, (40, 40))

    plt.subplot(1,1,1)
    nx.draw(G, with_labels=True)
    plt.show()

if __name__ == '__main__':

    pytest.main([__file__])

    with open('day18_input.txt', 'r') as f:
        day18_input = f.read()

    m = parse_vault_map(day18_input)
    steps = collect_keys(m)
    print(steps)