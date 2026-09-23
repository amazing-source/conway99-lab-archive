# Independent audit

## Verdict

`VERIFIED_WITH_SCOPE`.

All Wave 182 claims survive under the frozen Wave181 equality hypothesis.

## Local roots and nonedge intersections

At a vertex `x`, the local graph on its 14 neighbors is seven disjoint
edges, corresponding to the seven star triangles.  Choosing two neighbors
from different pairs gives `84` unordered pairs.  They are nonadjacent and
have, besides `x`, a unique second common neighbor `y`.  Conversely, the two
common neighbors of every nonneighbor `y` of `x` lie in different star
pairs.  This is a bijection.

For each pair of star blocks there are four choices of their neighbor
representatives, all labeled by the same projective difference
`<z_i-z_j>`.  The 21 projective differences are distinct because any
different equality would give a star relation on at most four columns,
whereas the only star relation has support seven.  Every root has norm one
and labels exactly four nonedges at `x`.

For a nonedge `xy`, the canonical square relation gives
`rho_xy in R_x intersect R_y`.  A second common root would equate two
differences on the disjoint `x`- and `y`-stars, producing a true weight-four
circuit cross-realizing `xy`.  It differs from the canonical circuit unless
the root is `rho_xy`; local root representations are unique.  Wave181
equality allows no other nonedge-realizing short circuit.  Therefore

```text
R_x intersect R_y={rho_xy}.
```

## Color supports

For a global root `r`, let `X_r={x:r in R_x}`.  Each `x in X_r` has exactly
four nonedges colored `r`.  Conversely, if two vertices of `X_r` are
nonadjacent, exact nonedge intersection forces their label to be `r`.
Thus the color graph is precisely `complement(G[X_r])` and is 4-regular.
Hence `m_r=|X_r|>=5`.

For an edge `uv` of this color graph, at most six other vertices are color
neighbors of `u` or `v`.  At least `m_r-8` remaining vertices are therefore
common graph neighbors of the nonedge `uv`.  Since `mu=2`,

```text
5<=m_r<=10.
```

Also `sum_r m_r=99*21=2079`, giving the upper root count
`floor(2079/5)=415`.

## Adjacent common roots

For adjacent `x,y`, their stars share the triangle `T_0`.  A common root
cannot use `T_0` in both representations: equal projective differences
would produce duplicate columns or a relation of weight at most three.  If
only one representation uses `T_0`, pairing the resulting relation with
`z_(T_0)` gives `-1`, independently of projective sign.

Thus every common root uses two outer blocks on each side and yields a true
balanced weight-four outer circuit.  Wave178's local projective capacities
are `0,1,6,3` for cycle types `6,4+2,3+3,2+2+2`; the source word counts
`0,2,12,6` include the two ternary scalars.  Therefore every graph edge has
at most six common projective roots.

## Second moment and root count

Incidence double counting gives

```text
sum_r binom(m_r,2)
 =sum_(x<y)|R_x intersect R_y|
 <=4158+6*693
 =8316.
```

Hence

```text
sum_r m_r^2<=2*8316+2079=18711=9*2079.
```

Cauchy–Schwarz yields

```text
2079^2<=|R|*18711,
|R|>=231.
```

Together with the support bound, `231<=|R|<=415`.

## The 231-root equality case

At 231 roots, both the second-moment inequality and Cauchy–Schwarz are
equalities.  Therefore every multiplicity is nine and every graph edge has
six common roots.  Wave178 then forces cycle type `3+3` on every edge and
all six eligible projective weight-four directions to be true.

For the `99 by 231` star-root incidence matrix `F`, row sums are 21, column
sums are nine, and pair intersections are six on edges and one on
nonedges.  Thus

```text
F F^T=20I+5A+J.
```

The SRG adjacency spectrum `14^1,3^54,(-4)^44` gives

```text
spec(F F^T)=189^1,35^54,0^44,
rank_R(F)=55.
```

This is positive semidefinite and supplies no contradiction.

The canonical-square Gram also gives orthogonal norm-one roots on opposite
nonedges.  Locally,

```text
sum_(r in R_x) r tensor r=-P_x.
```

Summing gives `sum_r m_r r tensor r=0`.  At the extremal case `m_r=9=0`
in `F_3`, so the identity is termwise zero rather than contradictory.

## Integrity and boundary

- all eight frozen inputs and all nine discovery entries matched;
- discovery replay and all seven discovery tests passed;
- the independent checker reproduced local counts, projective edge caps,
  second moments, extremal spectrum, and frame cancellation;
- all eight independent tests passed.

No contradiction, graph construction, rank-11 exclusion, or strict `n3`
improvement follows.

