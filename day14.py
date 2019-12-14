import pytest
from typing import AbstractSet, ClassVar, MutableMapping

class Substance():
    name: str
    substance_map: MutableMapping[str, Substance]

    def get(name: str) -> Substance:
        return substance_map.get(name, lambda: Substance(name))



class Reagent():
    substance: Substance
    quantity: int

    def parse(s: str) -> Reagent:
        [name, quantity] = s.strip().split(' ')
        return Reagent(Substance.get(name), quantity)



class Recipe():
    produced: Substance
    consumed: AbstractSet[Substance]



def parse_line(line):
    [inputs, result] = [s.strip() for s in line.split(" => ")]
# ---------------------

TEST_INPUT_1 = '''10 ORE => 10 A
1 ORE => 1 B
7 A, 1 B => 1 C
7 A, 1 C => 1 D
7 A, 1 D => 1 E
7 A, 1 E => 1 FUEL'''

def test_parse_line():
    line = '10 ORE => 10 A'
    recipe = parse_line(line)
    assert recipe.produced == Reagent('A', 10)
    assert recipe.consumed == {Reagent('ORE', 10)}


if __name__ == '__main__':
    pytest.main([__file__])
