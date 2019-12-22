import pytest
import itertools as it
import re


def fresh_pack(n = 10007):
    return range(n)

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return it.zip_longest(*args)

def deal_into_new_stack(cards):
    print('deal into new stack')
    return list(reversed(cards))

def cut(n, cards):
    print(f'cut {n}')
    xs = list(cards)
    return xs[n:] + xs[:n]

def deal_with_increment(n, cards):
    print(f'deal with increment {n}')
    xs = list(cards)
    size = len(xs)
    result = [0]*size
    for i in range(size):
        result[(i * n) % size] = xs[i]
    return result

RE_DEAL_INTO_NEW_STACK = re.compile(r"deal into new stack")
RE_CUT = re.compile(r"cut (-?\d+)")
RE_DEAL_WITH_INCREMENT = re.compile(r"deal with increment (\d+)")
RE_RESULT = re.compile(r"Result: (.*)")
def shuffle(input, n=10007):
    cards = fresh_pack(n)
    for line in input.splitlines():
        match = RE_DEAL_INTO_NEW_STACK.match(line)
        if match:
            cards = deal_into_new_stack(cards)
            continue
        match = RE_CUT.match(line)
        if match:
            n = int(match.group(1))
            cards = cut(n, cards)
            continue
        match = RE_DEAL_WITH_INCREMENT.match(line)
        if match:
            n = int(match.group(1))
            cards = deal_with_increment(n, cards)
            continue
        match = RE_RESULT.match(line)
        if match:
            expected = [int(x) for x in match.group(1).split(' ')]
            assert cards == expected

    return cards

# ------------------------------------------------------------

test_input_1 = '''deal with increment 7
deal into new stack
deal into new stack
Result: 0 3 6 9 2 5 8 1 4 7'''

test_input_2 = '''cut 6
deal with increment 7
deal into new stack
Result: 3 0 7 4 1 8 5 2 9 6'''

test_input_3 = '''deal with increment 7
deal with increment 9
cut -2
Result: 6 3 0 7 4 1 8 5 2 9'''

test_input_4 = '''deal into new stack
cut -2
deal with increment 7
cut 8
cut -4
deal with increment 7
cut 3
deal with increment 9
deal with increment 3
cut -1
Result: 9 2 5 8 1 4 7 0 3 6'''


def test_deal_into_new_stack():
    cards = range(10)
    actual = deal_into_new_stack(cards)
    assert list(actual) == list(range(9,-1, -1))

def test_cut_3():
    cards = range(10)
    actual = cut(3, cards)
    assert list(actual) == [3, 4, 5, 6, 7, 8, 9, 0, 1, 2,]

def test_cut_minus4():
    cards = range(10)
    actual = cut(-4, cards)
    assert list(actual) == [6, 7, 8, 9, 0, 1, 2, 3, 4, 5,]

def test_deal_with_increment():
    cards = range(10)
    actual = deal_with_increment(3, cards)
    assert list(actual) == [0, 7, 4, 1, 8, 5, 2, 9, 6, 3,]

def test_shuffle():
    shuffle(test_input_1, 10)
    shuffle(test_input_2, 10)
    shuffle(test_input_3, 10)
    shuffle(test_input_4, 10)

if __name__ == '__main__':
    pytest.main([__file__])

    with open('day22_input.txt', 'r') as f:
        day22_input = f.read()

    cards = shuffle(day22_input)

    print(f'part1: {cards.index(2019)}')