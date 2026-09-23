# Wave 42 proof/construction agent B: joint incidence

## Assignment

Attack the scoped branch

```text
n3=4158,
r3=12,
all edges type 222,
canonical rank-33 Wave 41 local lift,
```

using simultaneous `BB^T`, `BH`, `B^TB+H^2`, and SRG common-neighbor
identities. No symmetry assumption was permitted.

## Derived exact reduction

The mask-`51739` core has connected components of sizes `12+24`, balanced
`4+8` in every fibre. The component-indicator moments in the forced Gram
meet Cauchy--Schwarz with equality, forcing every outside block to use
exactly two small-component points.

Same-fibre Gram entries force every one of the sixty nonmatching pairs in
each fibre exactly once. Hence a full incidence matrix is precisely a
three-way matching of three labelled 60-pair sets. Its component patterns
are forced to occur with multiplicities

```text
4,4,4,16,16,16
```

for the three permutations of `(2,0,0)` and `(1,1,0)`.

Complete enumeration gives

```text
216000 raw pair triples
118718 positive-Gram-support triples
 49736 after component equality
 45032 after mixed BH nonnegativity.
```

This is an exhaustive reduction, not a restricted search.

## Positive and hostile controls

A retained 60-entry permutation realizes the entire first two-fibre
concurrence matrix exactly. It proves the two-fibre projection is feasible
and blocks any attempted contradiction at that level.

A generic MILP timeout and one proofless UNSAT result for a fixed
first-stage model are recorded only as failed routes. Neither is evidence.

## Outside graph boundary

The core has ten four-cycles. Any completion has block overlaps
`458/1004/308` at sizes `0/1/2`. A compatible eight-regular `H` must use
`96/144/0` edges of those overlap types and have 32 triangles and 181
four-cycles.

No full `B` or `H` was constructed or excluded. The scoped branch,
prism-free endpoint, general upper bound, Conway-99, and novelty remain
`UNKNOWN`.

