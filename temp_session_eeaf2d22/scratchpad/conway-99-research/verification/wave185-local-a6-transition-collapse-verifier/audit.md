# Independent hostile audit

## Verdict

**`VERIFIED_WITH_SCOPE`.**  No correction to the frozen Wave 185 conclusions
is required.  The source package and all five direct frozen inputs match their
declared hashes.  The contents named by all five direct prior-package
manifests also match.  Older transitive input freezes are preserved as hashed
package files but are not recursively reinterpreted.

## 1. Same-endpoint cell edges force an induced prism

Fix `x`, write its seven neighbor edges as
`V_i={i_0,i_1}`, and let

```text
y=(i_alpha,j_0),  y'=(i_alpha,j_1)
```

be two vertices in the same four-point cell.  If `y~y'`, then
`{i_alpha,y,y'}` and `{x,j_0,j_1}` are triangles.  Their cross edges are
exactly

```text
x i_alpha,  j_0 y,  j_1 y'.
```

There are no others: `x` is nonadjacent to residual vertices; different
mate pairs have no edges in `G[N(x)]`; and a residual vertex has precisely
the two base neighbors named by its label.  The induced graph is therefore
the triangular prism.  Endpoint prism-freeness excludes this edge.  The same
argument works after interchanging `i` and `j`.

Among the six pairs of corners of a `2 by 2` cell, four share an actual
endpoint and the remaining two are opposite corners.  Only the two disjoint
opposite-corner pairs can be internal edges, so the cell graph has maximum
degree one.  Wave 183 gives the cell shapes `4K1`, `2K2`, and `P4` for global
multiplicities five, six, and seven.  Since `P4` has vertices of degree two,

```text
n_7=0.
```

This deduction applies at every support vertex of a hypothetical
multiplicity-seven root, so there is no exceptional choice of local root.

## 2. Transition table

For a residual label `y` in the local root cell `Y_e`, let `d` be its
internal degree.  Summing the rooted endpoint-profile equation over the two
actual points in group `i` gives two neighboring labels in cells containing
`i`; the same holds for `j`.  An internal neighbor is counted in both sums.
Consequently the off-cell degree into root cells incident with `e` is

```text
4-2d.
```

Exactly two of these edges are the rooted transitions sharing one actual
endpoint with `y`, one at each endpoint.  The remaining incident-cell,
disjoint-label degree is `2-2d`.  Finally, every residual vertex has two
transition neighbors and ten disjoint-label neighbors.  Subtracting the
internal and incident-disjoint contributions gives:

| global type | internal | transition | incident disjoint | orthogonal |
|---|---:|---:|---:|---:|
| `m=5` | 0 | 2 | 2 | 8 |
| `m=6` | 1 | 2 | 0 | 9 |

Each row sums to residual degree 12.  These are aggregate degrees only; no
individual cell-pair regularity is inferred.

## 3. The incident-cell capacity is six

Take incident local roots `e={i,j}` and `f={i,k}`.  A disjoint-label edge
between their cells uses opposite actual endpoints in `V_i`.  For either
orientation, the four possible edges form a `K_{2,2}`.

All four cannot occur.  The two vertices on the `Y_e` side share their base
neighbor in `V_i` and, by the prism exclusion above, are nonadjacent.  If all
four cross edges were present, the two vertices on the other side would be
two further common neighbors.  This gives at least three common neighbors,
contradicting `mu=2`.  Thus each orientation contributes at most three and

```text
b_ef<=3+3=6.
```

For a type-five cell the transition table supplies eight such incident
disjoint edges in total; for a type-six cell it supplies zero.  Symmetry of
`b_ef` means a positive entry joins two type-five local roots.  Since one
neighbor can carry at most six of the total weight eight, every type-five
local root has at least two distinct type-five companions.

The argument proves cap six, not cap four.  A three-edge orientation is not
excluded by this common-neighbor argument.

## 4. Global companions and root profiles

A global type-five root `r` has support `X_r=5K1`.  At each of its five
vertices the local argument supplies two other type-five roots.  Companions
arising at different support vertices are distinct: if `s!=r` appeared with
`r` at two vertices `x,x'`, then `x,x'` would be nonadjacent and both roots
would lie in `R_x intersect R_x'`, contradicting the verified singleton
nonedge-root intersection.

Hence `r` has at least ten distinct companions and `n_5>=11`.  A type-five
root exists because, after `n_7=0`,

```text
5*n_5+6*n_6=2079
```

forces `n_5=3 mod 6`.  Combining the congruence with `n_5>=11` gives
`n_5>=15`.  All nonnegative solutions are exactly

```text
(n_5,n_6)=(15+6u,334-5u), 0<=u<=66.
```

Therefore `|R|=349+u`, so `349<=|R|<=415`.  These scalar profiles are
necessary conditions, not constructions.

## 5. Rainbow complement triangles

The complement of `srg(99,14,1,2)` has parameters
`srg(99,84,71,72)` and therefore

```text
99*84*71/6=98406
```

triangles.  Exact nonedge-root uniqueness colors each complement edge.
If two edges of a complement triangle have the same color `r`, their third
pair is another graph nonedge inside `X_r`, so it also has color `r`.
Thus every complement triangle is monochromatic or rainbow.

A type-five support contributes `binom(5,3)=10` monochromatic triangles.
A type-six support has color graph `K_{2,2,2}` and contributes eight.
Consequently

```text
mono=10*n_5+8*n_6
    =4158-4*n_6.
```

The exact profiles have `n_6>=4`, so `mono<=4142` and

```text
rainbow>=98406-4142=94264.
```

## Integrity and boundary

- The verifier imports no discovery module and never executes
  `attempts/wave185-local-a6-transition-collapse/exact_check.py`.
- The independent checker reconstructs the graph and arithmetic objects from
  definitions and validates the Wave 185 package, its input freeze, and the
  five directly referenced prior-package manifests.
- The calculations are small exact identities, not a graph, SAT, code, or
  isomorphism search.
- Wave 181 equality, rank 11, endpoint existence, external novelty, and
  Conway 99 remain `UNKNOWN`.
