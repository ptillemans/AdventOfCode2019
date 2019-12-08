import numpy as np
from typing import NamedTuple


class Segment(NamedTuple):
	is_horizontal: bool
	is_normal: bool
	x: int
	y: int
	length: int
	cumul: int

def read_wires(fname):
	with open(fname,'r') as f:
		return f.read().splitlines()
		

def parse_segment(x, y, l, s):
	direction = s[0]
	length = int(s[1:])
	cl = l + length
	if direction == 'R':
		return x + length, y, cl, Segment(True, True, x, y, length, l)
	elif direction == 'L':
		return x - length, y, cl, Segment(True, False, x-length, y, length, l)
	elif direction == 'U':
		return x, y + length, cl, Segment(False, True, x, y, length, l)
	elif direction == 'D':
		return x, y - length, cl, Segment(False, False, x, y-length, length, l)
	else:
		raise Error('Unknown direction')
		
		
def wire_to_segments(line):
	x = 0
	y = 0
	cl = 0
	for dir in line.split(','):
		x, y, cl, segment = parse_segment(x, y, cl, dir)
		yield segment
		
		
def crossing(seg1, seg2):
	if seg1.is_horizontal:
		if seg2.is_horizontal:
			return None
		if seg1.x <= seg2.x and seg2.x <= seg1.x + seg1.length and seg2.y <= seg1.y and seg1.y <= seg2.y + seg2.length:
			d1 = seg2.x - seg1.x if seg1.is_normal else seg1.x + seg1.length - seg2.x
			d2 = seg1.y - seg2.y if seg2.is_normal else seg2.y + seg2.length - seg1.y
			c = (seg2.x, seg1.y, seg1.cumul + d1, seg2.cumul + d2)
			print(f'crossing: {seg1, seg2, c, d1, d2}')
			return c
		else:
			return None
	else:
		if not seg2.is_horizontal:
			return None
		if seg1.y <= seg2.y and seg2.y <= seg1.y + seg1.length and seg2.x <= seg1.x and seg1.x <= seg2.x + seg2.length:
			d1 = seg2.y - seg1.y if seg1.is_normal else seg1.y + seg1.length - seg2.y
			d2 = seg1.x - seg2.x if seg2.is_normal else seg2.x + seg2.length - seg1.x
			c = (seg1.x, seg2.y, seg1.cumul + d1, seg2.cumul + d2)
			print(f'crossing: {seg1, seg2, c, d1, d2}')
			return c
		else:
			None
		  
		  
	
		
examples = read_wires('examples_day3.txt')

print(examples)

print(list(wire_to_segments(examples[3])))
def find_crossings(wire1, wire2):
	segs1=list(wire_to_segments(wire1))
	segs2=list(wire_to_segments(wire2))

	crossings = [c for s1 in segs1 for s2 in segs2 for c in [crossing(s1, s2)] if c and c[:2] != (0,0)]

	print(crossings)
	
	return crossings
	

def min_distance(crossings):
	return min([abs(c[0]) + abs(c[1]) for c in crossings])
	
	
def min_cumul_distance(crossings):
	return min([abs(c[2]) + abs(c[3]) for c in crossings])
	
ex1_xs = find_crossings(examples[0], examples[1])
ex2_xs = find_crossings(examples[2], examples[3])
print(min_distance(ex1_xs))
print(min_distance(ex2_xs))

[w1, w2] = read_wires('input_day3.txt')
w1_w2_xs = find_crossings(w1, w2)
print(min_distance(w1_w2_xs))

print(min_cumul_distance(ex1_xs))
print(list(wire_to_segments(examples[2])))
print(list(wire_to_segments(examples[3])))
ex2_xs = find_crossings(examples[2], examples[3])
print(min_cumul_distance(ex2_xs))
print()
print(min_cumul_distance(w1_w2_xs))
