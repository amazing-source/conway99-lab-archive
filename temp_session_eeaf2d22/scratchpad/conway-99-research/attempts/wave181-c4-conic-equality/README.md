# Wave 181: the canonical-C4 conic equality boundary

Status: `DERIVED_PENDING_VERIFICATION`.

Assume the verified conditional rank-11 endpoint model.  Wave 180 gives at
least 2,079 projective circuits cross-realizing nonedges.  This wave
classifies equality in that lower bound.

First, a star-projector argument excludes a circuit that serves exactly two
nonedges with a shared endpoint.  Therefore every multiplicity-two support
comes from the two diagonals of the canonical induced quadrilateral attached
to one nonedge.

The four edge-triangle columns on such a quadrilateral have a fixed Gram
matrix.  If they are dependent, their unique relation is the checkerboard
equation

```text
z_00-z_01-z_10+z_11=0,
```

and the four switched columns are the complete conic `Q(2,3)`.

Consequently equality in Wave 180's nonedge bound can hold only if all 2,079
canonical induced quadrilaterals are checkerboard conics and there are no
other nonedge-realizing short circuits.

This exposes a concrete continuation.  Let `R_square` be the signed
`2079 by 231` quadrilateral--triangle matrix.  Equality forces

```text
row(R_square) subset W^perp,
rank_F3(R_square)<=220,
R_square^T R_square=2K+L mod 3.
```

An analytic lower bound `rank_F3(R_square)>=221` would make the Wave 180
enumerator bound strict.  No such lower bound is proved here, and even that
one-unit improvement would not by itself exclude the endpoint.

No graph, code, SAT, configuration, or isomorphism search is used.  Rank 11,
the endpoint, a strict `n3` improvement, and Conway-99 remain `UNKNOWN`.
