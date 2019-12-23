import pytest
from intcode import IntCode
import queue
import threading
import time
import logging


class Computer():

    def __init__(self, network, address):
        self.network = network
        self.address = address
        self.core = IntCode.create_from_source('day23_input.txt')
        self.core.output = self
        self.core.input = self
        self.out_packet = ()
        self.input = queue.Queue()
        self.input.put(address)

    def boot(self):
        self.prg = threading.Thread(target=self.core.run)
        self.prg.start()
        logging.info(f'{self} started')

    def shutdown(self):
        self.core.finished = True
        self.prg.join()
        logging.info(f'{self} stopped')

    def listen_network(self, packet):
        (addr, x, y) = packet
        if addr == self.address:
            logging.debug(f'computer({addr}) received {x}, {y}')
            self.input.put(x)
            self.input.put(y)
      
    def put(self, input):
        ''' ducktype as queue
        
        Note that this method will run int the core thread.
        '''
        time.sleep(0.05)
        self.out_packet += (input,)
        if len(self.out_packet) == 3:
            network.queue.put(self.out_packet)
            self.out_packet = ()

      
    def get(self, block, timeout):
        ''' ducktype as queue
        
        Note that this method will run int the core thread.
        '''
        time.sleep(0.05)
        if self.input.empty():
            return -1
        else:
            return self.input.get(block, timeout)


    @property
    def is_idle(self):
        return self.input.empty() and self.out_packet == ()

    @property
    def name(self):
        return f'computer_{self.address}'

    def __repr__(self):
        return self.name

class Nat():

    def __init__(self, network):
        self.x = None
        self.y = None
        self.last_y_sent = None
        self.network = network

    def listen_network(self, packet):
        (addr, x, y) = packet
        logging.info('Nat received %s, %s was %s, %s', x, y, self.x, self.y)
        self.x = x
        self.y = y
        
    def check_activity(self):
        time.sleep(0.15)
        computers = self.network.computers
        computers_idle = all(computers[address].is_idle for address in computers)
        network_idle = self.network.queue.empty()
        if network_idle and computers_idle and self.x and self.y:
            network.queue.put((0, self.x, self.y))
            logging.info('Nat sent idle packet (0, %s, %s)', self.x, self.y)
            if self.y == self.last_y_sent:
                logging.warning('Nat sent duplicate y : %s', self.y)
            self.last_y_sent = self.y 


class Network():

    def __init__(self, n):
        self.computers = {}
        for address in range(n):
            computer = Computer(self, address)
            self.computers[address] = computer
        self.queue = queue.Queue()
        self.nat = Nat(self)

    def boot(self):
        computers = self.computers
        for address in computers:
            self.computers[address].boot()

        idle_timer = 25
        while not all(computers[address].core.finished for address in computers):
            time.sleep(0.05)
            
            try:
                packet = self.queue.get(False)
                (address, x, y) = packet
                idle_timer = 25
                if address in computers:
                    computers[address].listen_network(packet)
                elif address == 255:
                    self.nat.listen_network(packet)
                else:
                    logging.error(f'Undeliverable packet: {packet}')
            except queue.Empty:
                logging.debug(f'network queue empty')
                idle_timer -= 1
                if idle_timer < 0:
                    self.nat.check_activity()


        for address in computers:
            self.computers[address].shutdown()
        logging.info(f'network shutdown')

def test_create_network():
    network = Network(50)
    assert len(network.computers) == 50


def test_network_addresses():
    network = Network(50)
    for addr in network.computers.keys():
        assert network.computers[addr].address == addr

if __name__ == '__main__':
    logging.basicConfig(filename='day23.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info('************ Network starting ************')
    #pytest.main([__file__])

    network = Network(50)
    network.boot()