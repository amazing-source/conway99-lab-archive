# Wave 33 rooted-extension retained failures and boundaries

## No rooted extension or exclusion

The full rooted graph-extension problem is equivalent to the finite binary
`(D,B)` block system recorded in the report and checker.  No satisfying
pair is constructed.  No complete enumeration, proof of infeasibility, or
checkable solver certificate is supplied.  Therefore neither the rooted
branch nor `n3=708` is excluded.

Even a pair passing the graph block system would still need the frozen
projector, lattice, tensor, and Schur endpoint conditions.  The finite
criterion is necessary and sufficient for extending the signed support to
an `srg(99,14,1,2)` graph, not sufficient for the complete endpoint
package.

## The abstract `2-(15,3,2)` design is not contradictory

The checker constructs 70 distinct triples by taking two disjoint copies
of the line design of `PG(3,2)`.  Their incidence matrix satisfies

```text
B^T B=12I+2J.
```

Thus the simple `2-(15,3,2)` condition by itself is consistent.  Under the
checker’s deliberately arbitrary ordering of those 70 blocks against the
fixed `O` labels, 135 of the 210 entries of `FB` differ from two.  This is
a hostile design-only control, not a near-extension and not evidence that
the required coupled design exists.

## A heuristic attempt to couple that design was inconclusive

For route finding only, the two disjoint `PG(3,2)` systems were resolved
into seven ten-block classes, giving the required point degree two for one
side of the `7 x 7` support-label table.  Random within-class swaps then
tried to impose the second resolution with cell multiplicities one on the
28 Fano-complement pairs and two on the other 21 pairs.

Two non-certifying searches used deterministic seeds `3301` and `3302`.
The first ran 80 restarts of 60,000 two-block simulated-annealing swaps;
the second varied disjoint point permutations and added three-cycles for
about 110 seconds.  Both reached squared degree-defect 12 and did not reach
zero.  The exploratory scripts and transient logs were not frozen, so this
route is not part of the evidentiary computation.  A heuristic nonhit says
nothing about existence or nonexistence.

## The forced spectrum is compatible with integrality

The induced 70-vertex `O` graph would have characteristic polynomial

```text
(x-9)(x+1)^14(x^2+2x-1)^6(x-3)^27(x+4)^16.
```

It has integral coefficients, integral spectral moments, determinant
`2^32 3^29`, 56 triangles, and 294 four-cycles.  None of these values is
contradictory.  Spectral feasibility is not graph existence.

## Local matchings do not determine the outside graph

The 42 `D` edges whose unique common neighbor lies in the signed support
are forced only up to a perfect matching on each six-vertex support star.
Likewise, each of the 15 support-free neighborhoods induces a seven-edge
matching in `D`, but neither those matchings nor the associated 2-factors
are globally classified here.  Choosing canonical matchings would be an
extra symmetry assumption and was not used.

## Cycle types stop at four cases

For each support-free vertex, its 14 support labels form a spanning simple
2-regular bipartite graph.  The possible cycle types are

```text
14;
10+4;
8+6;
6+4+4.
```

All four pass the elementary degree screen.  No unsupported claim that one
type is canonical, transitive, or forced is made.

## Root reflection remains non-combinatorial

Wave 32’s lattice root reflection preserves a factorization but is not a
coordinate permutation or graph automorphism.  It cannot be used to
identify `O` or `Q` vertices, force design orbits, or reduce the binary
search without an additional proved argument.

## Strongest self-objection

The spectral decomposition uses that `im(F^T)` and `im(B)` intersect only
in the constant vector and that their nonconstant parts are orthogonal.
This must be reconstructed from `rank(F)=13`, `rank(B)=15`, and `FB=2J`;
dimension counting without those facts would be circular.  It also uses
the zero diagonal of `D` to determine the residual multiplicities.  An
independent verifier should rebuild these subspaces and all six block
equations rather than trusting the stated spectrum.

## Status wall

No automorphism is assumed beyond relabeling the already-forced Fano
support.  No catalog, floating-point feasibility, timeout, heuristic
nonhit, or absence-of-witness inference is used.  Rooted endpoint
existence, `n3=708`, Conway-99 existence/nonexistence, and novelty remain
`UNKNOWN`.
