# Derivation

Let `S` be a six-set with induced graph `H`, and let

```text
z_P = #{x outside S : N(x) intersect S = P}.
```

Wave 144 imposed the total, degree, pair-common-neighbor, and output parity
equations on these 64 cells.

## Seventh-vertex admissibility

Fix one cell `P` and regard its outside vertex as a new root `x`.  For each
`u in S`, the number of common neighbors of `x` and `u` already visible in
`S` is

```text
c_P(u) = #{v in P : uv is an edge of H}.
```

If `u in P`, then `xu` is an edge and local admissibility requires
`c_P(u)<=lambda=1`.  If `u not in P`, then `xu` is a nonedge and it requires
`c_P(u)<=mu=2`.

There is one further condition for pairs inside `S`.  If `u,v in P`, the new
root is an additional common neighbor of `u,v`, so the frozen pair residual
for `{u,v}` must be positive.  Together these conditions are equivalent to
local admissibility of the induced rooted seven-vertex graph.  The test suite
checks this equivalence for all `62*64` class/pattern pairs.

## Rooted orbit variables

For a canonical representative `H`, a pattern is intrinsic only up to
`Aut(H)`.  Write `[P]` for its automorphism orbit and define

```text
X_(H,w,P)
```

as the aggregate number of oriented pairs `(S,x)` having class `H`, output
weight `w`, and canonical pattern `P`.  For every `(H,w)` cell, the `X`
variables obey the Wave 144 total, degree, pair, and odd-pattern equations,
with the corresponding class/weight count `B_(H,w)` on the right.

Every induced seven-set of class `K` has seven distinguished deletions.
Enumerating them gives exact multiplicities

```text
m(K; H,[P]).
```

If `Y_K` is the count of seven-sets of class `K`, double counting ordered
pairs `(S,x)` gives

```text
sum_w sum_(P in [P0]) X_(H,w,P)
  = sum_K m(K;H,[P0]) Y_K.                 (1)
```

Equation (1) supplies 944 rooted orbit rows.  The ordinary 62 deletion rows
and 19 Hamiltonian rows constrain the same `Y_K`.

## Global six-weight rows

The `B_(H,w)` variables satisfy:

1. all 62 exact six-class marginals at `n3=4158`;
2. the Wave 141 Krawtchouk reciprocity rows for input weights `0,1,2,3`; and
3. the exact signed row
   `sum (-1)^(w/2) B_(H,w) = 2,734,116`.

After the seventh-vertex filter there are 343 possible `B` cells.

## Exact endpoint witness

The stored sparse vector assigns nonnegative rational values to all `Y`,
`h11/4`, `B`, and `X` variables.  Its denominators divide four.  Direct
integer-coefficient replay verifies all 8,981 equations, including (1), and
the endpoint range for `h11`.

This proves feasibility only of the stated rational aggregate relaxation.
