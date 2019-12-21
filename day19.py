import numpy as np 
from intcode import IntCode
import threading
import pytest
from matplotlib import pyplot as plt

class DroneSystem:
    
    def __init__(self):
        self.computer = IntCode.create_from_source('day19_input.txt')

    def measure(self, x, y):
        self.prg = threading.Thread(target=self.computer.run)
        self.prg.start()
        self.computer.input.put(x)
        self.computer.input.put(y)
        out = self.computer.output.get()
        #print(f'out: {out}')
        self.prg.join()
        return out

    def scan(self, area):
        (x_max, y_max) = area.shape
        for x in range(x_max):
            for y in range(y_max):
                measure = self.measure(x, y)
                area[y][x] = measure

    def track_edges(self):
        x = 22
        y0 = 30
        y1 = 31
        while True:
            x += 1
            y0 += 1
            y1 += 1
            while not self.measure(x,y0):
                y0 += 1
            while self.measure(x,y1 + 1):
                y1 += 1
            yield x, y0, y1


def bounds(area):
    (x_max, y_max) = area.shape
    for x in range(x_max):
        in_beam = False
        y0 = -1
        y1 = -1
        for y in range(y_max):
            m = area[y][x]
            if m and not in_beam:
                y0 = y
                in_beam = True
            if not m and in_beam:
                y1 = y
                break
        if in_beam:
            yield (x, y0, y1)





def test_measure():
    dcs = DroneSystem()

    actual = dcs.measure(0,0)
    assert actual == 1

if __name__ == '__main__':
    #pytest.main([__file__])

    dcs = DroneSystem()

    scan_area = np.zeros((50, 50))
    dcs.scan(scan_area)
    print(scan_area)
    print(f'areas of tractorbeam: {np.count_nonzero(scan_area)}')

    for y in range(50):
        print(''.join("#" if scan_area[x][y] else "." for x in range(50)))

    plt.imshow(scan_area, interpolation='nearest')
    plt.show()

    for t in bounds(scan_area):
        print(t)

    beam = {}
    for t in dcs.track_edges():
        print(t)
        (x, y0, y1) = t
        beam[x] = (y0, y1)
        x_ll = x - 99
        y_ll = y0 + 99
        beam_ll = beam.get(x_ll)
        if beam_ll and beam_ll[1] >= y_ll:
            print(f'solution: {x_ll}, {y0}')
            print(f'part2: {x_ll*10000 + y0}')
            break
