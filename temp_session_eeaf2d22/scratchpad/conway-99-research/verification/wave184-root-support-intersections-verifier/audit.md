# Hostile proof audit

## Verdict

**VERIFIED_WITH_SCOPE.**  No correction to the frozen Wave 184 conclusions
is required.

## 1. Pairwise support intersections

For a global projective root `r`, write
`X_r={x : r in R_x}`.  Take distinct roots `r,s`.  If two vertices
`x,y in X_r intersect X_s` were nonadjacent, then both roots would belong
to `R_x intersect R_y`.  Verified exact nonedge-root uniqueness says this
intersection is the singleton `{rho_xy}`, contradicting `r!=s`.

Thus `X_r intersect X_s` is a clique.  Every possible support graph from
Wave 183 (`5K1`, `3K2`, or `C7`) is triangle-free.  A clique contained in
either support therefore has size at most two, and size two is necessarily
a graph edge:

`|X_r intersect X_s|<=2`.

This also proves the exact pair identity.  If
`c_xy=|R_x intersect R_y|` for a graph edge `xy`, each unordered pair among
those `c_xy` roots has support intersection exactly `{x,y}`.  Conversely,
every root pair with two common support vertices determines its unique
common graph edge.  Hence the number of root pairs meeting twice is
`sum_(xy in E(G)) binom(c_xy,2)`.

## 2. One edge-root incidence gives a weight-four circuit

Let `xy` be an internal graph edge of `X_r`.  At either endpoint, a local
root is the projective difference of two distinct point-star columns.
The verified adjacent-star lemma excludes the shared triangle `T_0` from
both representations:

- if both representations used `T_0`, equating them would give duplicate
  columns or a nonzero relation of weight at most three;
- if only one used `T_0`, pairing the alleged relation with `z_(T_0)` gives
  `-1`, so it is not a relation.

The two remaining columns at `x` are distinct, as are the two at `y`.
The two pairs are mutually disjoint: a triangle appearing in both stars
would contain the edge `xy`, but its unique triangle is `T_0`, already
excluded.  Therefore equating the two projective difference
representations produces a relation on exactly four distinct columns.
Every coefficient is nonzero because each difference has coefficients
`1,-1` and the projective comparison scalar is nonzero.

The verified dual distance is at least four, so no proper subset of these
four columns is dependent.  The relation is consequently a genuine
weight-four matroid circuit, not merely a Gram-kernel vector.

## 3. Injectivity and separation

Fix the edge `xy`.  The projective four-coordinate relation determines its
restriction to the two `x`-star columns, hence determines their projective
difference `r`.  Two distinct roots on the same edge therefore cannot
produce the same projective circuit.

Every constructed circuit has exactly two outer columns on each side of
its indexing edge, so it satisfies the balance and cross-support hypotheses
of the verified Wave 178--179 isolation results.  Those results prove that
one circuit support serves at most one graph edge.  Equality of projective
relations implies equality of supports, so circuits belonging to different
graph edges are also distinct.

Finally, a canonical quadrilateral circuit realizes its nonedge diagonal.
Wave 179 proves that a balanced edge circuit realizes only its indexing
graph edge and cannot equal a nonedge-realizing circuit.  The new family is
therefore disjoint from all 2,079 canonical nonedge conics.

All three collision modes requested by the verification protocol are thus
excluded.

## 4. Exact edge-root count

Count incidences `(r,xy)` where `xy` is a graph edge internal to `X_r`.
The support graphs `5K1`, `3K2`, and `C7` contain respectively `0`, `3`,
and `7` graph edges.  Therefore the injective family has exactly

`E=3*n6+7*n7`

projective circuits.  Equivalently,
`E=sum_(xy in E(G)) |R_x intersect R_y|`.

The root-incidence equation is

`5*n5+6*n6+7*n7=2079`.

Modulo five this becomes

`n6+2*n7=4 (mod 5)`.

If `E<12`, then `n7<=1`.  For `n7=0`, the inequality gives `n6<=3`, while
the congruence requires `n6=4 (mod 5)`, impossible.  For `n7=1`, it gives
`n6<=1`, while the congruence requires `n6=2 (mod 5)`, also impossible.
Hence `E>=12`.

The nonnegative integer triple `(n5,n6,n7)=(411,4,0)` satisfies the
incidence equation and has `E=12`, so 12 is sharp for these scalar
constraints alone.  It is not asserted to realize the geometry.

## 5. Projective classes versus words

Wave 181 equality supplies 2,079 distinct canonical projective
weight-four conics.  The preceding injectivity and separation supply at
least 12 additional projective weight-four circuits, for at least

`2079+12=2091`

projective classes.

A circuit has a one-dimensional relation space.  Over `F_3`, each
projective class has exactly two nonzero scalar representatives, both of
weight four.  Thus

`B4>=2*2091=4182`.

## Limitations

- Every conclusion is conditional on the Wave 181 equality face and its
  verified Wave 182--183 consequences.
- The lower bound has no known incompatible upper bound.
- The scalar sharpness triple is not a graph, code, or root-system
  construction.
- No rank-11 exclusion, strict `n3` improvement, endpoint contradiction, or
  Conway-99 resolution follows.
