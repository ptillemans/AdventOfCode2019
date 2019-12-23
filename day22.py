import pytest
import itertools as it
import functools as ft
import re


def fresh_pack(n = 10007):
    return range(n)

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return it.zip_longest(*args)

def deal_into_new_stack(cards):
    #print('deal into new stack')
    return list(reversed(cards))

def cut(n, cards):
    #print(f'cut {n}')
    xs = list(cards)
    size = len(xs)
    return [xs[(i + n) % size] for i in range(size)]

def deal_with_increment(n, cards):
    #print(f'deal with increment {n}')
    xs = list(cards)
    size = len(xs)
    result = [0]*size
    if n != 0:
        for i in range(size):
            result[(i * n) % size] = xs[i]
    return result

RE_DEAL_INTO_NEW_STACK = re.compile(r"deal into new stack")
RE_CUT = re.compile(r"cut (-?\d+)")
RE_DEAL_WITH_INCREMENT = re.compile(r"deal with increment (\d+)")
RE_RESULT = re.compile(r"Result: (.*)")
def shuffle(input, size, cards=None, verify=True):
    cards = cards or fresh_pack(size)
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
        if match and verify:
            expected = parse_result(match.group(1))
            assert cards == expected

    return cards


def parse_result(data):
    return [int(x) for x in data.split(' ')]

def op_deal_into_new_stack():
    return (-1, -1)


def op_cut(n):
    return (n, 1)


def op_deal_with_increment(n, size):
    inv_n = mod_inverse(n, size)
    return (0, inv_n)    

def calculation(input, size):
    stack = []
    for line in input.splitlines():
        match = RE_DEAL_INTO_NEW_STACK.match(line)
        if match:
            stack.append(op_deal_into_new_stack())
            continue
        match = RE_CUT.match(line)
        if match:
            n = int(match.group(1))
            stack.append(op_cut(n))
            continue
        match = RE_DEAL_WITH_INCREMENT.match(line)
        if match:
            n = int(match.group(1))
            stack.append(op_deal_with_increment(n, size))
            continue
        match = RE_RESULT.match(line)
        if match:
            continue

    return stack

def simplify(size):
    def reducer(op1, op2): 
        op = ((op1[0] * op2[1] + op2[0])%size, (op1[1]*op2[1])%size)
        #print(f'simplify {op1} + {op2} -> {op}')
        return op
    
    return reducer

def simplify_calculation(ops, size):
    op = ft.reduce(simplify(size), reversed(ops))
    return (op[0] %  size, op[1] % size)

def calculate_original_x(op, y, size):
    (add, mul) = op
    return (y * mul + add) % size

def calculate(op, cards):
    xs = list(cards)
    size = len(xs)
    return [xs[calculate_original_x(op, i, size)] for i in range(size)]

def repeat_op(n, op, size):
    p_n = pow(op[1], n, size) - 1
    p_1 = mod_inverse(op[1] - 1, size)

    return((op[0] * p_n * p_1) % size, pow(op[1], n, size))

def shuffle_2(input, size, cards=None):
    cards = cards or range(size)
    op = simplify_input(input, size)
    return calculate(op, cards)


def simplify_input(input, size):
    return simplify_calculation(calculation(input, size), size)

def xgcd(a, b):
    """return (g, x, y) such that a*x + b*y = g = gcd(a, b)"""
    x0, x1, y0, y1 = 0, 1, 1, 0
    while a != 0:
        q, b, a = b // a, a, b % a
        y0, y1 = y1, y0 - q * y1
        x0, x1 = x1, x0 - q * x1
    return b, x0, y0
    
def mod_inverse(x, size):
	t = xgcd(x, size)
	return  t[1] % size

def repeat_shuffle(n, input, size):
    cards = range(size)
    for i in range(n):
        cards = shuffle(input, size, cards, verify=False)
    return cards

def repeat_shuffle_2(n, input, size):
    cards = range(size)
    calc = simplify_input(input, size)
    calc_n = repeat_op(n, calc, size)
    cards = calculate(calc_n, cards)
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

def test_shuffle_2():
    assert shuffle_2(test_input_1, 10) == parse_result('0 3 6 9 2 5 8 1 4 7')
    assert shuffle_2(test_input_2, 10) == parse_result('3 0 7 4 1 8 5 2 9 6')
    assert shuffle_2(test_input_3, 10) == parse_result('6 3 0 7 4 1 8 5 2 9')
    assert shuffle_2(test_input_4, 10) == parse_result('9 2 5 8 1 4 7 0 3 6')

def test_repeat_op():
    size = 11
    for i in range(1,10):
        op = (1,3)
        expected = simplify_calculation([op]*i, size)
        actual = repeat_op(i, op, size)
        assert actual == expected

def test_repeat_shuffle():
    for i in range(1,10):
        expected = repeat_shuffle(i, test_input_1,11)
        actual = repeat_shuffle_2(i, test_input_1,11)
        assert expected == actual

def test_calculation_deal_with_increment():
    size = 11
    
    for n in range(size):
        calc = calculation(f'deal with increment {n}', size)[0]
        actual = calculate(calc, range(size))
        expected = deal_with_increment(n, range(size))
        assert actual == expected

if __name__ == '__main__':
    pytest.main([__file__])

    with open('day22_input.txt', 'r') as f:
        day22_input = f.read()

    size = 10007

    cards = shuffle(day22_input, size)

    print(f'part1: {cards.index(2019)}')

    cards_2 = shuffle_2(day22_input, size)

    assert cards == cards_2

    part2_calc = simplify_input(day22_input, size)
    orig_x = calculate_original_x(part2_calc, 1234, size)
    print(f'part1: {orig_x}')

    # part2
    part2_size = 119315717514047
    shuffles   = 101741582076661

    single_shuffle = simplify_input(day22_input, part2_size)
    all_shuffles = repeat_op(shuffles, single_shuffle, part2_size)
    part2_answer = calculate_original_x(all_shuffles, 2020, part2_size)
    print(f'part2: {part2_answer}')