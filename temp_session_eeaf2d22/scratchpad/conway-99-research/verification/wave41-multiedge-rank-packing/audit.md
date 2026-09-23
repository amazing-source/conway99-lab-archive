# Wave 41 multiedge rank packing: independent audit

Date: 2026-07-27 UTC

Verdict:

```text
all-odd edge type => rank_F7(M)>=26:  VERIFIED_SCOPED
universal rank_F7(M)>=26:             NOT PROVED
universal verified rank floor:        25
seven even-part edge types:           UNKNOWN
discovery "five even-part types":      REFUTED_FIELD
```

The refuted field is a count typo in the discovery JSON limitations. It does
not affect the scoped theorem.

## Independence

The verifier froze the task, verified Wave 39/40 inputs, and opaque hashes of
all eight discovery files before opening or running the Wave 41 discovery
package. It then wrote an independent 39-block constructor, exact `F_7`
elimination, matching enumerators, Schur checker, rank transport record, and
status validator. The pre-comparison artifacts were frozen at:

```text
b0d71926dbb1bb6988b603a4adf7ea69489866702433e4250034bd8218103747  independent_check.py
20cfac8928e1a9d52a586a833d8e52cc7f64f7998bdd641467ded5121e2da133  independent-results.json
6e463acd4f994faf330cfa8d584cc91f70921e07ac352bbad4995d646aa516e7  protocol-freeze.md
cab2abb752837fb7cae5e7e0c01a32421a8a053d1a40efa44529bb5184416ff8  precomparison-method-addendum.md
```

Only then were discovery results compared and their tests replayed.

## Complete 39-point normal form

Fix a triangle `T={x,y,z}` and put

```text
X=N(x)-T, Y=N(y)-T, Z=N(z)-T.
```

Each fibre has twelve points and induces a perfect matching. Every pair of
fibres is joined by a perfect matching. Relabeling locally, without assuming
any automorphism of a completed graph, fixes the `X` matching and the `X-Y`
and `X-Z` cross matchings. The remaining data are:

- the `Y` matching, whose alternating cycle partition is one of the eleven
  positive partitions of six;
- an arbitrary `Y-Z` permutation;
- an arbitrary `Z` perfect matching.

The verifier recursively generated all

```text
(12-1)!! = 10,395
```

labelled perfect matchings, with no duplicates, and audited every constructed
39-vertex graph: the triangle vertices have induced degree 14, every fibre
vertex has induced degree four, and all six within/cross relations are
perfect matchings.

For every dense cross-check it independently confirmed

```text
K39=(J-I-2A)[T union N(T)],
rank_F7(K39)=1+rank_F7(3I-A_core).
```

The latter is the exact full-block identity, not a quotient heuristic.

## Independent equality obstruction

For a selected base edge, split the 39-block as

```text
K39 = [ S   U ]
      [ U^T W ],
```

where `S` is the previously verified 27-point block and `W` is the exact
`Z`-fibre block. For each all-odd type

```text
1^6, 1^3+3, 1+5, 3+3,
```

exact elimination gives

```text
rank_F7(S)=25, dim ker(S)=2.
```

All 144 possible individual border columns lie in `im(S)`. Hence, for every
`Y-Z` permutation, solve `S X=U` and use exact singular Schur elimination:

```text
rank_F7(K39)=25+rank_F7(W-U^T X).                  (1)
```

Rank 25 would force the residual in (1) to vanish. Since every legal `W` has
zero diagonal, each selected `(X,Y)` border pair must have zero Schur
quadratic value. The verifier built the full twelve-by-twelve bipartite graph
of such pairs. Exact maximum matchings and equal-size Konig vertex-cover
certificates give:

| type | zero edges | matching number | perfect candidates |
| --- | ---: | ---: | ---: |
| `1^6` | 0 | 0 | 0 |
| `1^3+3` | 6 | 6 | 0 |
| `1+5` | 20 | 10 | 0 |
| `3+3` | 12 | 12 | 1 |

This compresses all `12!` permutations without restricting them: every
rank-25 completion must be a perfect matching in this necessary-condition
graph.

For `3+3`, the one perfect candidate was reconstructed. Its Schur target has
field values outside the legal `Z`-block alphabet

```text
diagonal 0; off-diagonal 1 or -1,
```

so it is not induced by any perfect matching. Therefore no all-odd
completion has rank 25, and every such 39-block has rank at least 26.

## Rank transport

The frozen incidence identities are

```text
N M N^T=J-I-2A,
N^T N M=3M
```

over `F_7`. If `v=Mw` and `Nv=0`, then

```text
0=N^T Nv=3v.
```

Because `3^-1=5` in `F_7`, `v=0`; thus `N` is injective on `im(M)`.
Symmetry on the other side gives

```text
rank_F7(N M N^T)=rank_F7(M).
```

A principal K39 block of rank at least 26 therefore proves the scoped global
implication

```text
if any edge has an all-odd type, rank_F7(M)>=26.
```

It does not show that every hypothetical graph has such an edge.

## Universal compact kernel

For constants `a_i` on the three triangle vertices and `b_i` on their
twelve-point fibres, the six quotient equations for `K39 v=0` reduce to

```text
A=-B, b_i=2(B-a_i).
```

The three `a_i` are free, giving a three-dimensional fibre-constant kernel
for every admissible K39 block, independent of its six matchings.

Globally these are the restrictions of

```text
h_v=(A+4I)e_v.
```

Using `A^2=12I-A+2J`,

```text
(J-I-2A)(A+4I)=14J-7A-28I=0 mod 7.
```

For a vertex outside `T union N(T)`, its K-column dot product with a triangle
star is exactly

```text
(4+1+1)+(10-2)=14=0 mod 7.
```

Thus the three independent compact vectors are also killed by all 60 outside
columns. They are a genuine obstruction to naively adding ranks from
overlapping triangle blocks.

## Positive controls

After the independent result was frozen, the verifier decoded discovery's
two matching certificates and rebuilt both graphs without importing
discovery code:

| control | components | core triangles | `rank(3I-A_core)` | `rank(K39)` |
| --- | --- | ---: | ---: | ---: |
| generic | `12+12+12` | 6 | 27 | 28 |
| triangle-free | `18+18` | 0 | 28 | 29 |

Both exact ranks, nullities, component counts, compact-kernel checks, and the
full 39-block identity reproduced. These are local controls, not 99-vertex
partial graphs. They rule out stronger claims based only on forced one-block
data.

## Discovery comparison and discrepancy

The discovery package manifest and frozen inputs all match their current
bytes. Its stored JSON regenerates exactly, and all ten discovery tests pass.
Independent invariant comparison agrees on all four types, all 576 diagonal
assignment checks, the rank-26 implication, compact-kernel obstruction, and
the two controls.

One ancillary discovery JSON line says:

```text
The five even-part edge types are not excluded from rank 25 by this package.
```

This is false as a count. The eleven partitions split into four all-odd and
seven containing an even part:

```text
6, 2+4, 1^2+4, 1+2+3, 2^3, 1^2+2^2, 1^4+2.
```

All seven remain `UNKNOWN` in this audit. No result from any separate
even-part lane is imported.

## Scope wall

```text
all-odd rank-26 implication:          VERIFIED_SCOPED
seven even-part equality questions:  UNKNOWN
universal rank floor:                 VERIFIED 25 only
endpoint n3=4158:                     UNKNOWN
best general n3 upper bound:          4158
Conway-99 existence:                  UNKNOWN
literature novelty:                   UNKNOWN
99-vertex construction:               NONE
```
