''' Day 14 of Advent of Code'''
from typing import AbstractSet, ClassVar, Mapping, MutableMapping, NamedTuple
import pytest
from collections import defaultdict
import math


class Substance():
    '''A chemical compound used or produced by the nano factory'''
    name: str

    substance_map: ClassVar[MutableMapping[str, 'Substance']] = {}

    @classmethod
    def get(cls, name: str) -> 'Substance':
        '''Get the unique instance of a given substance.'''
        return Substance.substance_map[name] \
            if name in Substance.substance_map \
            else Substance(name)

    def __init__(self, name: str):
        self.name = name
        Substance.substance_map[name] = self

    def __repr__(self):
        return(f'S({self.name})')


FUEL = Substance.get('FUEL')
ORE = Substance.get('ORE')

CARGO_CAPACITY = 1000000000000

class Reagent(NamedTuple):
    ''' an amount of substance used or produced in a reaction'''
    substance: Substance
    quantity: int

    @classmethod
    def parse(cls, definition: str) -> 'Reagent':
        '''parse a reagent definition'''
        [quantity, name] = definition.strip().split(' ')
        return Reagent(Substance.get(name), int(quantity))

    def __str__(self):
        return f'R({self.substance},{self.quantity})'



class Recipe(NamedTuple):
    '''the description of inputs and outputs of a reaction.'''
    produced: Reagent
    consumed: AbstractSet[Reagent]

    @classmethod
    def parse(cls, line: str) -> Reagent:
        '''Parse a line with a reaction description.'''
        [inputs, result] = [s.strip() for s in line.split(" => ")]
        produced = Reagent.parse(result)
        consumed = {Reagent.parse(term) for term in inputs.split(", ")}
        return Recipe(produced, consumed)



    def __str__(self):
        return f'Recipe({self.produced}, {list(self.consumed)})'


class NanoFactory():
    '''Implementation of a nanofactory.'''

    recipes: Mapping[Substance, AbstractSet[Recipe]]
    consumed_by: Mapping[Substance, AbstractSet[Substance]]

    def __init__(self, recipes):
        self.recipes = recipes
        self.consumed_by = defaultdict(lambda: set())

        for substance in recipes:
            recipe = self.recipes[substance]
            for consumable in recipe.consumed:
                consumed = consumable.substance
                self.consumed_by[consumed].add(substance)
            self.deep_consumed_by = defaultdict(lambda:set())
            self.init_deep_consumed_by(ORE)

    def init_deep_consumed_by(self, substance):
        if substance in self.deep_consumed_by:
            return self.deep_consumed_by[substance]
        else:
            dependents = {s
                    for c in self.consumed_by[substance]
                    for s in self.init_deep_consumed_by(c)}
            self.deep_consumed_by[substance] = dependents.union(self.consumed_by[substance])
            return dependents

    @classmethod
    def parse(cls, recipe_book: str):
        recipes = {recipe.produced.substance: recipe
                   for line in recipe_book.splitlines()
                   for recipe in [Recipe.parse(line)]}
        return NanoFactory(recipes)

    def deep_needed_substances(self, substance: Substance) -> AbstractSet[Substance]:
        if substance == ORE:
            return set()
        recipe = self.recipes[substance]
        need = {reagent.substance
                for reagent in recipe.consumed}

        for s in set(need):
            need = need.union(self.deep_needed_substances(s))

        return need


    def ore_requirements(self, substance: Substance, quantity: int = 1) -> int:
        '''returns ore required for given substance'''
        needed_materials = defaultdict(lambda: 0)
        needed_materials[substance] = quantity
        needed_substances = self.deep_needed_substances(substance)
        needed_substances.add(substance)
        while needed_substances != {ORE}:
            for material in self.substances_not_needed_for_others(needed_substances):
                job = self.recipes[material]
                qty_needed = needed_materials[material]
                qty_per_job = job.produced.quantity
                jobs_needed = math.ceil(qty_needed/qty_per_job)
                for reagent in job.consumed:
                    needed_materials[reagent.substance] += jobs_needed * reagent.quantity
                del needed_materials[material]
                needed_substances.remove(material)
        ore_needed = needed_materials[ORE]
        print(f'{ore_needed} ore needed for {quantity} fuel')
        return ore_needed

    def substances_not_needed_for_others(self, substances: AbstractSet[Substance]):
        free =  [substance for substance in substances
                if self.deep_consumed_by[substance].isdisjoint(substances)]
        return free


    def calculate_fuel_production(self, amount: int):
        x = 1
        production = 0
        while True:
            production = self.ore_requirements(FUEL, x *2)
            if production > amount:
                break
            print(f' {x} - {production} - {production < amount}')
            x = x * 2

        a = x
        b = x * 2
        while b > a + 1:
            print(f'a: {a}, b: {b}')
            x = (a + b) // 2
            production = self.ore_requirements(FUEL, x)
            print(f' {x} - {production} - {production < amount}')
            if production < amount:
                a = x
            elif production > amount:
                b = x
            else:
                return x
        return a




# ---------------------

TEST_INPUT_1 = '''10 ORE => 10 A
1 ORE => 1 B
7 A, 1 B => 1 C
7 A, 1 C => 1 D
7 A, 1 D => 1 E
7 A, 1 E => 1 FUEL'''

TEST_INPUT_2 = '''9 ORE => 2 A
8 ORE => 3 B
7 ORE => 5 C
3 A, 4 B => 1 AB
5 B, 7 C => 1 BC
4 C, 1 A => 1 CA
2 AB, 3 BC, 4 CA => 1 FUEL'''

TEST_INPUT_3 = '''157 ORE => 5 NZVS
165 ORE => 6 DCFZ
44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
179 ORE => 7 PSHF
177 ORE => 5 HKGWZ
7 DCFZ, 7 PSHF => 2 XJWVT
165 ORE => 2 GPVTF
3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT'''

TEST_INPUT_4 = '''2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
17 NVRVD, 3 JNWZP => 8 VPVL
53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
22 VJHF, 37 MNCFX => 5 FWMGM
139 ORE => 4 NVRVD
144 ORE => 7 JNWZP
5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
145 ORE => 6 MNCFX
1 NVRVD => 8 CXFTF
1 VJHF, 6 MNCFX => 4 RFSQX
176 ORE => 6 VJHF'''

TEST_INPUT_5 = '''171 ORE => 8 CNZTR
7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
114 ORE => 4 BHXH
14 VRPVC => 6 BMBT
6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
5 BMBT => 4 WPTQ
189 ORE => 9 KTJDG
1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
12 VRPVC, 27 CNZTR => 2 XDBXC
15 KTJDG, 12 BHXH => 5 XCVML
3 BHXH, 2 VRPVC => 7 MZWV
121 ORE => 7 VRPVC
7 XCVML => 6 RJRHP
5 BHXH, 4 VRPVC => 5 LTCX'''

def test_parse_recipe():
    line = '10 ORE => 10 A'
    recipe: Recipe = Recipe.parse(line)
    assert recipe.produced == Reagent(Substance.get('A'), 10)
    assert recipe.consumed == {Reagent(ORE, 10)}

def test_parse_factory():
    factory: NanoFactory = NanoFactory.parse(TEST_INPUT_1)
    assert len(factory.recipes) == 6

def test_substances_not_needed_for_others():
    factory: NanoFactory = NanoFactory.parse('1 ORE => 1 FUEL')
    reagents = set(factory.substances_not_needed_for_others([ORE, FUEL]))
    assert reagents == {FUEL}

def test_ore_requirements_trivial():
    factory: NanoFactory = NanoFactory.parse('1 ORE => 1 FUEL')
    assert factory.ore_requirements(FUEL) == 1


def test_ore_requirements_trivial2():
    factory: NanoFactory = NanoFactory.parse('1 ORE => 1 A\n1 A => 1 FUEL')
    assert factory.ore_requirements(FUEL) == 1

def test_ore_requirements_trivial3():
    factory: NanoFactory = NanoFactory.parse('1 ORE => 1 A\n4 A => 1 FUEL')
    assert factory.ore_requirements(FUEL) == 4

def test_ore_requirements_trivial4():
    factory: NanoFactory = NanoFactory.parse('1 ORE => 2 A\n4 A => 1 FUEL')
    assert factory.ore_requirements(FUEL) == 2

def test_ore_requirements_trivial5():
    factory: NanoFactory = NanoFactory.parse('1 ORE => 2 A\n1 ORE => 2 B\n4 A, 1 B => 1 FUEL')
    assert factory.ore_requirements(FUEL) == 3

def test_ore_requirements_input_1():
    factory: NanoFactory = NanoFactory.parse(TEST_INPUT_1)
    assert factory.ore_requirements(FUEL) == 31

def test_ore_requirements_input_2():
    factory: NanoFactory = NanoFactory.parse(TEST_INPUT_2)
    assert factory.ore_requirements(FUEL) == 165

def test_ore_requirements_input_3():
    factory: NanoFactory = NanoFactory.parse(TEST_INPUT_3)
    assert factory.ore_requirements(FUEL) == 13312

def test_ore_requirements_input_4():
    factory: NanoFactory = NanoFactory.parse(TEST_INPUT_4)
    assert factory.ore_requirements(FUEL) == 180697

def test_ore_requirements_input_5():
    factory: NanoFactory = NanoFactory.parse(TEST_INPUT_5)
    assert factory.ore_requirements(FUEL) == 2210736

def test_fuel_example1():
    '''The 13312 ORE-per-FUEL example could produce 82892753 FUEL.'''
    factory: NanoFactory = NanoFactory.parse(TEST_INPUT_3)
    assert factory.calculate_fuel_production(CARGO_CAPACITY) == 82892753

def test_fuel_example2():
    '''The 180697 ORE-per-FUEL example could produce 5586022 FUEL.'''
    factory: NanoFactory = NanoFactory.parse(TEST_INPUT_4)
    assert factory.calculate_fuel_production(CARGO_CAPACITY) == 5586022

def test_fuel_example3():
    '''The 2210736 ORE-per-FUEL example could produce 460664 FUEL.'''
    factory: NanoFactory = NanoFactory.parse(TEST_INPUT_5)
    assert factory.calculate_fuel_production(CARGO_CAPACITY) == 460664

if __name__ == '__main__':
    pytest.main([__file__])

    if True:
        with open('day14_input.txt', 'r') as f:
            factory = NanoFactory.parse(f.read())
            ore_required = factory.ore_requirements(FUEL)
            print(f'Ore needed: {ore_required}')

            fuel_production = factory.calculate_fuel_production(CARGO_CAPACITY)
            print(f'Fuel produced: {fuel_production}')
