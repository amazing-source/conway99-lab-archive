# Boundary and failed continuations

## Ordinary finite-polar point counts are far too large

The ambient 11-dimensional orthogonal space has vastly more than 415
projective norm-one points.  The new bound

```text
231<=|mathcal R|<=415
```

comes from star support and SRG incidence, not from exhausting the ambient
quadric.  A polar pigeonhole argument does not close the branch.

## Four-regular color classes survive

Every global root support carries a 4-regular complement graph on between
five and ten vertices.  The parameter bound `mu=2` gives the sharp easy
ceiling ten, but 4-regular graphs exist throughout the relevant range.  No
classification of these tiny graphs is used or needed, and their local
existence would not ensure simultaneous global gluing.

## The 231-root incidence spectrum is positive

At the lower extreme, the star--root incidence matrix has

```text
F F^T=20I+5A+J
```

with real spectrum `189^1,35^54,0^44`.  The matrix is positive semidefinite
with the expected rank 55, so the first real spectral test supplies no
contradiction.

## The root-frame sum dies coefficientwise

The global identity

```text
sum_r m_r r tensor r=0
```

looks restrictive away from the lower extreme.  At 231 roots, however,
every multiplicity is nine and hence zero in characteristic three.  The
identity becomes termwise trivial rather than excluding the design.

## Square-complex exactness is not available

Alternating square relations are ordinary signed-cycle constraints on edge
labels, whereas a representation `ell_uv=p_u+p_v` uses the unsigned
incidence map.  Vertex sign-switching between the two requires bipartiteness,
but the target graph contains 231 triangles.

Equivalently, if `B_edge` is the unsigned vertex--edge incidence matrix and
`Q_square` is the span of alternating square vectors, the missing theorem is

```text
Q_square=ker(B_edge).
```

No checked partial-quadrangle, generalized-quadrangle, rectagraph, or graph
cohomology theorem proves this equality for `PQ(2,6,2)`.  Rectagraph cover
theorems explicitly require triangle-freeness.

## Remaining analytic bridge

A continuation must constrain the simultaneous 4-regular color graphs, the
orthogonality pairing between their edges, or the extremal two-class
incidence design.  A raw count of roots, first incidence spectrum, or first
projector moment is insufficient.
