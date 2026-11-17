from pyeda.inter import *
from functools import reduce

# each node has 5 BDD variables, x[0] MSB ... x[4] LSB
x = bddvars('x', 5)

# minterm for node i over variables v
def node(i,v):
    bits = format(i, '05b') # conv 16 to binary -> 10000
    lits = [v[k] if b== '1' else ~v[k] # conv each bit to 1-> x_k and 0 -> ~x_k
        for k,b in enumerate(bits)]
    return reduce(lambda a,b: a & b, lits) # AND all literals together  

# 5 more BDD variables for the destination of an edge
y = bddvars('y', 5)

#BDD TRUE only for the pair (source i, destination j)
def edge(i,j):
    return node(i,x) & node(j,y)

#R: OR together all 64 edges in the graph; each node i has edges to i+3 and i+8, mod 32
RR = reduce(lambda a, b: a | b,
             [edge(i, (i + 3) % 32) | edge(i, (i + 8) % 32) for i in range(32)])

#EVEN: set of even nodes, encoded on the destination vars y
EVEN = reduce(lambda a,b : a | b, [node(i,y) for i in range(0,32,2)]) 

#PRIME: prime set given by prof (no 2) encoded on the source vars x
PRIME_NODES = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
PRIME = reduce(lambda a,b : a | b, [node(i,x) for i in PRIME_NODES])

#5 more vars for the midle node of a path of length 2
z = bddvars('z', 5)

# (A comp B )(x,y) = exists z. A(x,z) & B(z,y)
def compose_rel(A, B):
    A_xz = A.compose({y[k]: z[k] for k in range(5)})   # A's destination -> z
    B_zy = B.compose({x[k]: z[k] for k in range(5)})   # B's source -> z
    return (A_xz & B_zy).smoothing(z)

RR2 = compose_rel(RR, RR)

# transitive closure of RR2 (fixpoint iteration)
RR2star = RR2
rounds = 0
while True:
    new = RR2star | compose_rel(RR2star, RR2) 
    rounds += 1
    if new.equivalent(RR2star): #nothing new means reached a fixpoint
        break
    RR2star = new

# exists v: nodes u that reach some even node in an even # of steps (smooth away from y)
reachEven = (EVEN & RR2star).smoothing(y)

#Prime(u) -> reachEven(u) rewritten as  ~Prime(u) | reachEven(u)
body = ~PRIME | reachEven

#for all u: rewritten as ~(exists u, ~body) (smooth away x); resul is 0 or 1
StatementA = ~((~body).smoothing(x))  


#--- Helpers for testing BDD at specific points --------
#assignment that spells node i on vars v
def bits(i,v):
    return {v[k]: int(b) for k, b in enumerate(format(i, '05b'))}

#TRUE iff BDD f evaluates to 1 at the given point
def holds(f,point):
    return f.restrict(point).is_one()

# number of (x,y) pairs in relation f, unused vars are 'dont care' doubles the count
def count_pairs(f):
    return f.satisfy_count() * 2 **(10 - len(f.support))  







# -----TESTS-------

# --- Step 3.1 tests for RR ---
print("RR(27, 3)  =", holds(RR, {**bits(27, x), **bits(3, y)}))    # expect True
print("RR(16, 20) =", holds(RR, {**bits(16, x), **bits(20, y)}))   # expect False
print("edges in RR:", count_pairs(RR))                          # expect 64
# --- Step 3.1 tests for EVEN and PRIME ---
print("EVEN(14)  =", holds(EVEN, bits(14, y)))    # expect True
print("EVEN(13)  =", holds(EVEN, bits(13, y)))    # expect False
print("PRIME(7)  =", holds(PRIME, bits(7, x)))    # expect True
print("PRIME(2)  =", holds(PRIME, bits(2, x)))    # expect False
# --- Step 3.2 tests for RR2 ---
print("RR2(27, 6) =", holds(RR2, {**bits(27, x), **bits(6, y)}))   # expect True
print("RR2(27, 9) =", holds(RR2, {**bits(27, x), **bits(9, y)}))   # expect False
print("pairs in RR2:", count_pairs(RR2)) # expect 96
# --- Step 3.3 results for RR2star ---
print("closure rounds:", rounds)
print("pairs in RR2star:", count_pairs(RR2star)) #1024 expected

print("RR2star is constant TRUE:", RR2star.is_one())   # expect True
# --- Step 3.4 result ---
print("StatementA =", StatementA.is_one())   # expect True