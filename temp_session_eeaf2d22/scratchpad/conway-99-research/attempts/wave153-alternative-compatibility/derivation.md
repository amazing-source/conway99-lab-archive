# Derivation of the Wave153 finite projection

## 1. Conditional fixed-triangle data

In the frozen `kappa=3` endpoint lane, the 36 neighbour-core vertices are
partitioned in two ways:

- three 12-vertex components;
- three 12-vertex fibres, with four vertices from each component in each
  fibre.

Each classified component is cubic: every vertex has degree three. For a
chosen unordered triple of component types, let `A_X` be the adjacency matrix
of their disjoint union. The required Gram matrix for a hypothetical
`36 x 60` binary incidence matrix `B` is

```text
G = B B^T
  = 12I - A_X + 2J - blockdiag(J12,J12,J12) - A_X^2.
```

The diagonal entries of `G` are 10. Thus each of the 36 rows of `B` must occur
in ten columns. Off-diagonal entry `G_ij` is the required number of columns
containing both rows `i` and `j`.

## 2. Allowed columns

Every column of `B` must be a six-set with:

- exactly two vertices from every component;
- exactly two vertices from every fibre;
- no pair whose target entry in `G` is zero.

Wave153 enumerates every distinct six-set satisfying those rules. For one
such column `s`, define `a_s` in `{0,1}^630` by

```text
(a_s)_{ij} = 1 if {i,j} is contained in s, and 0 otherwise,
```

for all `0 <= i < j < 36`. Each `a_s` has exactly `C(6,2)=15` ones.

## 3. Rational column polytope

A binary design would choose 60 distinct columns. Its indicator vector would
therefore satisfy

```text
sum_s x_s a_s = (G_ij)_{i<j},       x_s in {0,1}.
```

Wave153 retains the full pair equality but relaxes integrality:

```text
sum_s x_s a_s = (G_ij)_{i<j},       0 <= x_s <= 1.
```

The upper bound is important: it is the fractional remnant of the requirement
that a column may be selected at most once. It makes this system stronger
than a plain nonnegative cone.

The row margins and total weight follow from the pair equations but are
replayed separately as consistency checks. Every selected six-set contributes
five pairs incident with each of its rows, so

```text
5 * sum_{s contains i} x_s = sum_{j != i} G_ij = 50,
```

hence every row margin is 10. Summing all row margins and dividing by six
gives total column weight 60.

## 4. Orbit reduction

Wave60 froze a safe coordinate action: simultaneously relabel the three
fixed-triangle vertices, the three fibres, and the corresponding coordinates
inside every component. This is a change of labels, not an assumed
automorphism of an unknown target graph.

The action partitions the 1,140 unordered triples of the 18 component types
into 275 orbits. Feasibility is invariant under this coordinate permutation,
so one exact witness per representative transfers to every triple in its
orbit.

## 5. Exactification

For each representative:

1. HiGHS dual simplex finds a bounded floating feasible point.
2. Coordinates numerically at one are fixed to one.
3. A full-rank square row minor for the remaining support is selected by
   pivoted QR.
4. FLINT solves that minor over the rational numbers with a Dixon solve.
5. All 630 pair equations, all 36 row margins, total weight 60, candidate
   uniqueness, and every bound `0 < x_s <= 1` are replayed exactly.

No solver success code is accepted as a certificate. A lane is labeled
`CANDIDATE` only after the exact replay succeeds.

## 6. Meaning of the null witness

The 275 witnesses prove only that this finite rational projection does not
separate any orbit representative. They do not prove that a binary `B`
exists. Pair marginals can be mutually compatible over the rationals while
failing to arise from one integral family of 60 six-sets.

Consequently, further work should add a compatibility condition absent here:
triple-intersection variables, integral block coupling, or a proof-producing
binary feasibility/exclusion method.

