import itertools as it
import functools as ft
import pytest
from operator import mul, add


def pattern(n = 1):
    base = it.cycle([0, 1, 0, -1])
    stretched = (y for x in base for y in (x,) * n)
    yield from it.islice(stretched, 1, None)

def output_digit(signal, n):
    raw = sum(map(mul, pattern(n), [int(c) for c in signal]))
    return abs(raw) % 10

def output_signal(signal, repeat = 1):
    code = signal
    for _ in range(repeat):
        raw = map(output_digit, it.repeat(code), range(1, len(signal) + 1))
        code = ''.join(str(d) for d in raw)
    return code

def final_message(signal):
    offset = int(signal[:7])
    input = signal*10000
    fft = reversed(tuple(int(c) for c in input[offset:]))
    for _ in range(100):
        fft = it.accumulate(fft, lambda a, b: (a + b) % 10)
    return ''.join(str(d) for d in reversed(tuple(fft)))




def test_pattern_1():
    actual = list(it.islice(pattern(), 0, 8))
    expected = [1, 0, -1, 0, 1, 0, -1, 0]
    assert actual == expected


def test_pattern_2():
    actual = list(it.islice(pattern(2), 0, 16))
    expected = [0, 1, 1, 0, 0, -1, -1, 0, 0, 1, 1, 0, 0, -1, -1, 0]
    assert actual == expected


def test_output_digit():
    signal = '12345678'
    actual = output_digit(signal, 1)
    assert actual == 4


def test_outout_signal():
    signal = '12345678'
    expected = '48226158'
    actual = output_signal(signal)
    assert actual == expected


def test_outout_signal_2():
    signal = '12345678'
    expected = '34040438'
    actual = output_signal(signal, 2)
    assert actual == expected


def test_outout_signal_3():
    signal = '12345678'
    expected = '03415518'
    actual = output_signal(signal, 3)
    assert actual == expected


def test_outout_signal_4():
    signal = '12345678'
    expected = '01029498'
    actual = output_signal(signal, 4)
    assert actual == expected

def test_outout_signal_4():
    signal = '80871224585914546619083218645595'
    expected = '24176176'
    actual = output_signal(signal, 100)
    assert actual[:8] == expected

def test_outout_signal_4():
    signal = '19617804207202209144916044189917'
    expected = '73745418'
    actual = output_signal(signal, 100)
    assert actual[:8] == expected

def test_outout_signal_4():
    signal = '69317163492948606335995924319873'
    expected = '52432133'
    actual = output_signal(signal, 100)
    assert actual[:8] == expected

def test_final_message():
    signal = '03036732577212944063491565474664'
    expected = '84462026'
    actual = final_message(signal)
    assert actual[:8] == expected

if __name__ == '__main__':
    pytest.main([__file__])

    with open('day16_input.txt', 'r') as f:
        signal = f.read().strip()

    message = output_signal(signal, 100)
    print(f'part1: {message[:8]}')

    final = final_message(signal)
    print(f'part2: {final[:8]}')