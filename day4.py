import numpy as np

def to_digits(n):
	digits = [int(d) for d in str(n)]
	return np.array(digits)
	
	
start=124075
end=580769

def is_increasing(xs):
	return np.all(xs[:-1] <= xs[1:])
	
def has_double(xs):
	return np.any(xs[:-1] == xs[1:])
	
def has_strict_double(ds):
	xs = np.append(ds,[0])
	xs = np.insert(xs, 0, 0) # add sentinel
	dbls = xs[1:-2] == xs[2:-1]
	begs = xs[:-3] != xs[1:-2]
	term = xs[2:-1] != xs[3:]
	sd = np.logical_and(dbls,begs)
	sd = np.logical_and(sd,term)
	return np.any(sd)
	
def test_predicates(n):
	ds = to_digits(n)
	ii = is_increasing(ds)
	hd = has_double(ds)
	sd = has_strict_double(ds)
	print(f'{n}: {ii}, {hd}, {sd}')
	
	
test_predicates(111111)
test_predicates(122345)
test_predicates(223450)
test_predicates(123789)

candidates = [n for n in range(start, end+1)
                for digits in [to_digits(n)]
                if is_increasing(digits) and has_double(digits)]
                

print(len(candidates))

strict_cands = [n for n in range(start, end+1)
                for digits in [to_digits(n)]
                if is_increasing(digits) and has_strict_double(digits)]
                
print(len(strict_cands))
