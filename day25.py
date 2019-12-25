from intcode import IntCode
from threading import Thread
from queue import Queue
from collections import defaultdict
import itertools as it
import time
import re
import logging
import networkx as nx
import pickle

class Computer():

    def __init__(self):
        self.core = IntCode.create_from_source('day25_input.txt', timeout=30)
        self.core.output = self
        self.core.input = self
        self.queue = Queue()
        self.command_buffer = []
        self.line = ""
        self.items = set()
        self.room = 'Hull Breach'

    def boot(self):
        self.prg = Thread(target=self.core.run)
        self.prg.start()
        logging.info(f'{self} started')

    def shutdown(self):
        self.core.finished = True
        self.prg.join()
        logging.info(f'{self} stopped')

    def command(self, command):
        self.command_buffer = [ord(c) for c in command]
        self.command_buffer.append(10)
        print(f'> {command}')
    
    def put(self, input):
        ''' ducktype as queue
        
        Note that this method will run int the core thread.
        '''
        self.line += chr(input)
        if input == 10:
            print(f'< {self.line}')
            self.queue.put(self.line)
            self.line = ""
      
    def get(self, block, timeout):
        ''' ducktype as queue
        
        Note that this method will run int the core thread.
        '''
        while not self.command_buffer:
            time.sleep(0.05)

        (code, *rest) = self.command_buffer
        self.command_buffer = rest
        return code


    @property
    def is_idle(self):
        return self.queue.empty() and not self.command

    @property
    def name(self):
        return f'computer'

    def __repr__(self):
        return self.name

def manual_interaction():
    while not computer.core.finished:
        time.sleep(0.05)
        try:
            line = computer.queue.get()
            print(line, end='')
            if line.strip() == 'Command?':
                computer.command(input())
        except Empty:
            pass

ITEM_BLACKLIST=['infinite loop', 'giant electromagnet', 'escape pod', 'molten lava', 'photons']

RE_ROOM = re.compile(r'== (.*) ==')
RE_DOORS = re.compile(r'Doors here lead:')
RE_ITEMS = re.compile(r'Items here:')
RE_THING = re.compile(r'- (.*)')

def parse_description(computer, G):
    category = None
    doors = nx.get_node_attributes(G, 'rooms')
    items = nx.get_node_attributes(G, 'items')
    while True:
        line = computer.queue.get().strip()
        m = re.match(RE_ROOM, line)
        if m:
            room = m.group(1)
            print(f'add room {room}')
            G.add_node(room)
            doors[room] = set()
            items[room] = set()
        m = re.match(RE_DOORS, line)
        if m:
            category = 'doors'
        m = re.match(RE_ITEMS, line)
        if m:
            category = 'items'
        m = re.match(RE_THING, line)
        if m:
            thing = m.group(1)
            print(f'add {thing} to {category}')
            if category == 'doors':
                doors[room].add(thing)
            if category == 'items':
                items[room].add(thing)
        if line == 'Command?':
            computer.room = room
            nx.set_node_attributes(G, doors, 'doors')
            nx.set_node_attributes(G, items, 'items')
            return room
def wait_for_prompt(computer):
    line = ''
    while line != 'Command?':
        line = computer.queue.get().strip()
    

def explore(computer, G, dir=None):
    if dir:
        print(f'Go {dir}')
        computer.command(dir)
    room = parse_description(computer, G)
    print(f'Entering {room}')
    items = nx.get_node_attributes(G, 'items')
    doors = nx.get_node_attributes(G, 'doors')
    for item in items[room]:
        if item not in ITEM_BLACKLIST:
            take_item(computer, item)
    for door in doors[room]:
        if door == reverse_direction(dir):
            continue
        if room != 'Security Checkpoint':
            to = explore(computer, G, door)
            G.add_edge(room, to)
            directions = nx.get_edge_attributes(G, 'directions')
            directions[(room, to)] = door
            nx.set_edge_attributes(G, directions, 'directions')
            computer.room = room
        print(f'Back in {room}')
    print(f'Leaving {room}')
    if dir:
        computer.command(reverse_direction(dir))
        wait_for_prompt(computer)
    return room


def take_item(computer, item):
    print(f'take {item}')
    computer.command(f'take {item}')
    wait_for_prompt(computer)
    computer.items.add(item)

def drop_item(computer, item):
    print(f'drop {item}')
    computer.command(f'drop {item}')
    wait_for_prompt(computer)
    computer.items.remove(item)

def reverse_direction(dir):
    if dir == 'north':
        return 'south'
    elif dir == 'south':
        return 'north'
    elif dir == 'east':
        return 'west'
    elif dir == 'west':
        return 'east'

def go_to_room(computer, G, room):
    path = nx.shortest_path(G, computer.room, room)
    directions = nx.get_edge_attributes(G, 'directions')
    moves = [directions[edge] for edge in zip(path, path[1:])]
    for move in moves:
        computer.command(move)
        parse_description(computer, G)

def try_weight_combos(computer):
    all_items = computer.items.copy()
    room = computer.room
    move = 'west'    
    for r in range(len(all_items)):
        for combo in it.combinations(all_items, r):
            print(f'trying {combo}')
            for item in [i for i in combo if i not in computer.items]:
                take_item(computer, item)
            for item in [i for i in computer.items if i not in combo]:
                drop_item(computer, item)
            computer.command(move)
            parse_description(computer, G)
            if computer.room != room:
                print('found combination {combo} to open access to {new_room}')
                return computer.room, combo

if __name__ == "__main__":
    logging.basicConfig(filename='day23.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info('************ Network starting ************')
    computer = Computer()
    computer.boot()

    G = nx.Graph()

    explore(computer, G)
    #nx.write_gpickle(G, 'day25_graph.pkl')
    #G = nx.read_gpickle('day25_graph.pkl')
    go_to_room(computer, G, 'Security Checkpoint')
    try_weight_combos(computer)
    print('done')