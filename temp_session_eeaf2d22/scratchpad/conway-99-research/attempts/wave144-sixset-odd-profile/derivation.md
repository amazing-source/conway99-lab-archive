# Derivation of the six-set outside-profile lift

Fix a six-set `S` and write `H=G[S]`.  Every vertex outside `S` belongs to
exactly one cell

```text
P = N(x) intersect S.
```

There are 64 possible subsets, so their counts `z_P` sum to 93.

For `v` in `S`, exactly `14-deg_H(v)` of its neighbors lie outside `S`.
This gives the six degree equations.  For a pair `u,v`, the strongly regular
graph parameters prescribe one common neighbor when `uv` is an edge and two
when it is not.  Subtracting the common neighbors already inside `H` gives
the fifteen pair equations.

For vertices in `S`, the coordinate of `A 1_S` is `deg_H(v)` modulo two.
For a vertex in cell `P` outside `S`, that coordinate is `|P|` modulo two.
This proves the output-weight formula used by the checker.

## Why the support enumeration is exhaustive

A cell `P` with `|P|>=3` consumes one unit from every pair contained in `P`.
Each pair budget is only `0`, `1`, or `2`; hence every such cell has a finite
explicit upper bound.  The checker recursively visits every value from zero
through that bound.

After those choices:

1. `z_{u,v}` is the unused budget of pair `u,v`;
2. `z_{v}` is the unused degree budget of `v`; and
3. `z_empty` is the unused outside-vertex total.

These are the only remaining variables and are uniquely determined.  A leaf
is feasible exactly when all forced values are nonnegative.  Therefore the
reported weight lists are exact sets, not intervals inferred from extrema.

## Global coupling

Let `x_(i,w)` count six-sets in Wave21 source class `i` whose image has
weight `w`.  The certificate checks

```text
sum_w x_(i,w) = N_i(n3)
```

for all 62 classes and

```text
sum_(i,w) K_t(w) x_(i,w)
  = sum_b K_6(b) B[t,b]
```

for `t=0,1,2,3`.

The stored endpoint table has 65 nonzero integral cells.  Its exact moment
values are

```text
t=0:  1120529256
t=1: 12854346120
t=2: 55869122232
t=3: 84712070520.
```

It also replays the Wave141 signed row `S_6=2734116`.
