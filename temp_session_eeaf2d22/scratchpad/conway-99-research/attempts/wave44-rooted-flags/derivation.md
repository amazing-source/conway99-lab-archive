# Exact derivation of the rooted flag rows

## 1. Frozen assumptions

Assume a hypothetical strongly regular graph with parameters

```text
(n,k,lambda,mu)=(99,14,1,2)
```

and the conditional endpoint `n3=4158`, equivalently zero induced triangular
prisms. The endpoint is used by the inherited unrooted six/seven-count right
hand sides. The rooted equations below use only the SRG parameters.

Let `x_J` denote the number of induced seven-subsets whose unrooted
isomorphism class is `J`.

## 2. One-vertex flags

Fix a root vertex `u`. Among the other 98 vertices, exactly 14 are adjacent
to `u` and 84 are not. If six further vertices are selected and exactly `d`
are neighbors of `u`, the number of choices is

```text
binom(14,d) binom(84,6-d).
```

Summing over all 99 roots gives

```text
sum_J v_d(J) x_J
  = 99 binom(14,d) binom(84,6-d),       d=0,...,6,
```

where `v_d(J)` is the number of vertices of degree `d` inside `J`.

Summing the seven equations gives `7 binom(99,7)` on both sides. Their
coefficient span adds exactly one dimension to the inherited 81-row system.

## 3. Ordered edge flags

Fix an ordered adjacent pair `(u,v)`. Excluding the two roots, the 97
remaining vertices split into four categories:

- adjacent to both: `lambda=1`;
- adjacent to `u` only: `k-1-lambda=12`;
- adjacent to `v` only: `12`;
- adjacent to neither: `97-1-12-12=72`.

For a signature `(a,b,c,d)` with sum five and `a<=1`, the number of ways to
choose the other five vertices is

```text
binom(1,a) binom(12,b) binom(12,c) binom(72,d).
```

There are `99*14` ordered adjacent roots. Therefore

```text
sum_J e_abcd(J) x_J
 = 99*14 binom(1,a) binom(12,b) binom(12,c) binom(72,d).
```

There are 36 possible signatures. Orientation is retained: interchanging
the roots interchanges `b` and `c`.

## 4. Ordered nonedge flags

For an ordered nonadjacent pair, the same category sizes are

```text
mu=2, k-mu=12, k-mu=12, 97-2-12-12=71.
```

There are `99*(99-1-14)=99*84` ordered nonedges. Hence for
`a+b+c+d=5`, `a<=2`,

```text
sum_J n_abcd(J) x_J
 = 99*84 binom(2,a) binom(12,b) binom(12,c) binom(71,d).
```

There are 46 signatures.

For every class `J`, the sum of all vertex-root coefficients is seven, and
the edge-root plus nonedge-root coefficient sum is `7*6=42`. Globally, the
right-hand sides sum to the same values:

```text
sum vertex RHS = 7 binom(99,7),
sum edge/nonedge RHS = 42 binom(99,7).
```

These are exact double-counting identities, not sampled estimates.

## 5. Strictness and feasibility

Appending the vertex, edge, and nonedge layers changes exact modular ranks

```text
81 -> 82 -> 87 -> 93
```

over three primes larger than every local coefficient. Thus at least twelve
independent constraints are new relative to the unrooted system.

The frozen Wave 43 witness fails every rooted row. A distinct 91-support
integer vector satisfies all inherited and rooted equations exactly at
`h11=16632`. This proves feasibility of this finite linear/integer
relaxation, not existence of a graph.

The four coefficient/RHS families and their order are frozen in
`row-system.json`. SHA-256 commitments are computed from UTF-8 compact JSON
with sorted keys and separators `(",",":")`, separately for each
`{"rows":...,"rhs":...}` family and once for their combined mapping. This
lets an independent implementation compare coefficients after freeze
without importing the discovery code. The solver-free `verify_frozen.py`
also replays all 170 residuals from that file using only standard-library
integer arithmetic.

## 6. Missing PSD bridge

These equations fix first moments of rooted flag types. A genuine flag
moment upgrade selects smaller rooted flags `F_i` and introduces joint
densities for pairs `(F_i,F_j)` glued along their labels. For any real
coefficients `c_i`, a completed graph would satisfy

```text
sum_{i,j} c_i c_j p(F_i,F_j) >= 0,
```

so the joint-density matrix is positive semidefinite.

The current `x_J` variables do not determine those joint densities: two
seven-subsets sharing roots can overlap in their unlabelled vertices and
reuse graph edges. Supplying a sound gluing table or explicit higher-order
variables is the missing bridge. Treating products of aggregate counts as
joint densities would be invalid.
