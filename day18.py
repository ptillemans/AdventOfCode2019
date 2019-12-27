import pytest
import maze
import string
import networkx as nx
import networkx.algorithms.traversal.depth_first_search as dfs
import matplotlib.pyplot as plt
from itertools import permutations
from collections import defaultdict
from heapq import heapify, heappush, heappop

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
        keys |= {(l, distance) for l in next_tiles if is_key(maze.get_tile(l))}
        doors |= {(l, distance) for l in next_tiles if is_door(maze.get_tile(l))}
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

def get_distance(attribs, edge):
    (f,t) = edge
    distance = attribs.get(edge, attribs.get((t,f)))
    if distance is None:
        print(f'distance for {edge} not found')
    return distance


def remove_doors_from_maze(maze):
    G = nx.Graph()
    distances = dict(nx.get_edge_attributes(maze, 'distance'))
    paths = nx.all_pairs_shortest_path(maze, cutoff=3)
    lengths = dict(nx.all_pairs_shortest_path_length(maze, cutoff=3))
    for src in [x for x in paths if not is_door(x[0])]:
        G.add_node(src[0])
        for dst in [x for x in src[1] if x > src[0] and not is_door(x) and x != '@']:
            G.add_node(dst)
            path = src[1][dst]
            doors = {x for x in path if is_door(x)}
            distance = sum(get_distance(distances, x) for x in zip(path[:-1], path[1:]))
            length = lengths[src[0]][dst]
            G.add_edge(src[0], dst, length=length, distance=distance, path=path, doors=doors)
       
                        
    
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
    return x in string.ascii_uppercase
    
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

def shortest_pairs(G):
    keys = {k for k in G.nodes if is_key(k)}
    for start in keys:
        targets = nx.shortest_path(G, source=start, weight='distance')
        lengths = nx.shortest_path_length(G, source=start, weight='distance')
        yield from (
            ((start,t), lengths[t], targets[t]) 
            for t in targets 
            if is_key(t) and t != start)

def is_not_key_after_door(path):
    p = list(path)
    for i in range(1, len(p)):
        if p[i].upper() in p[:i]:
            return False
    return True
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
def test_example4():
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

def test_remove_doors():
    maze = nx.Graph()
    maze.add_node('@')
    maze.add_node('a')
    maze.add_edge('@', 'a', distance=2)
    maze.add_node('B')
    maze.add_edge('@', 'B', distance=2)
    maze.add_node('A')
    maze.add_edge('a', 'A', distance=3)
    maze.add_node('b')
    maze.add_edge('A', 'b', distance=4)
    maze.add_node('c')
    maze.add_edge('B', 'c', distance=5)
    clean_maze = remove_doors_from_maze(maze)
    distances = nx.get_edge_attributes(clean_maze, 'distance')
    doors = nx.get_edge_attributes(clean_maze, 'doors')
    assert distances[('a', 'b')] == 7
    assert doors[('a', 'b')] == {'A'}
    assert distances[('@', 'c')] == 7
    assert doors[('@', 'c')] == {'B'}


def play_area():
    day18_maze = parse_vault_map(day18_input)

    plt.subplot(1,1,1)
    nx.draw(day18_maze, with_labels=True)
    plt.show()

if __name__ == '__main__':

    pytest.main([__file__])

    with open('day18_input.txt', 'r') as f:
        day18_input = f.read()

    m = parse_vault_map(day18_input)
    #steps = collect_keys(m)
    #print(steps)
    show_graph(m)

    shortest_pairs = list(shortest_pairs(m))
    print(f'total {len(shortest_pairs)} pairs')

    free_keys = {'z', 'b', 'u', 'y', 't','l','i','h','s','e', 'p', 'f'}
    filtered_pairs = list(
        #filter(lambda p: is_not_key_after_door(p[2]),
        filter(lambda p: (p[0][0] not in free_keys) and (p[0][1] not in free_keys), 
        shortest_pairs))    
    for p in filtered_pairs:
        print(p)
    print(f'total {len(filtered_pairs)} filtered pairs')

    key_map = defaultdict(defaultdict)
    for (t, d, p) in filtered_pairs:
        (src, dst) = t
        keys = {x for x in p if is_key(x)}
        needed = {x.lower() for x in p if is_door(x) and not x.lower() in keys}
        key_map[src][dst] = (d, keys, needed)

    pruned_map = defaultdict(defaultdict)
    cutoff = 15
    for f in  key_map:
        dsts = sorted(list(key_map[f]), key=lambda x: len(key_map[f][x][1]))[:cutoff]
        for dst in dsts:
            pruned_map[f][dst] = key_map[f][dst]


    all_keys = list(pruned_map.keys())
    len_all_keys = len(all_keys)
    reachable_keys = reachable_missing_keys(m, '@', all_keys)

    G = nx.Graph()
    for s in pruned_map:
        G.add_node(s)
        for d in pruned_map[s]:
            G.add_node(d)
            G.add_edge(s, d, distance=pruned_map[s][d][0])
    show_graph(G)

    stack =[(nx.shortest_path_length(m, source='@', target=k, weight='distance'), k, {k}) 
        for k in reachable_keys]
    heapify(stack)


    min_distance = 1000000
    keyset_min = defaultdict(lambda: 1000000)
    i = 0

    while stack:
        (dist, cur_key, keys) = heappop(stack)
        if i % 10 == 0:
            print(f'{i:08d}: {min_distance} {len(stack)} | {dist}, {cur_key}, {keys}')
        destinations = [d for d in pruned_map[cur_key] if d not in keys]
        for dst in destinations:
            (d, provided, needed) = pruned_map[cur_key][dst]
            nxt_keys = frozenset(keys.union(provided))
            nxt_dist = dist + d
            missing_keys = needed - nxt_keys
            
            if missing_keys:
                # cannot reach it yet
                continue
            if nxt_dist >= min_distance:
                continue
            if nxt_dist >= 16*keyset_min[nxt_keys]:
                continue
            else:
                keyset_min[nxt_keys] = nxt_dist
            if len(nxt_keys) >= len_all_keys:
                min_distance = nxt_dist
                print(f'min distance : {min_distance}')
            heappush(stack, (nxt_dist, dst, nxt_keys))
        i += 1

    print('done')