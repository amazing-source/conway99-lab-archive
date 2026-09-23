# Global short circuits from exact two-transversals

## 1. A cross circuit for every vertex pair

Assume the prism-free endpoint and the conditional centered rank `k=11`.
Wave 177 gives:

```text
edge xy:       a true cross-star relation of weight 4..8
nonedge xy:    a true cross-star relation of weight 4..9.
```

For an edge, the relation avoids the common triangle, so its support lies
in two six-column outer stars.  Every one-sided proper star subset is
independent; an inclusion-minimal subrelation is therefore a cross circuit.

For a nonedge, the relation support may contain an entire seven-column
star, so one extra justification is needed.  Work within its support and
choose a relation outside the span of the two individual star circuits
with minimal support.  If a proper dependent subset is cross-star, it
already contains the desired cross circuit.  If it is one-sided, subtract
a scalar multiple of that star circuit; this keeps the relation outside
the two-star span and strictly shrinks its support, contradicting
minimality.  Hence a cross circuit exists within the original support.

Wave 174 supplies the lower support bound four.  Thus every unordered pair
of original vertices indexes a cross circuit of size at most nine, and an
edge indexes one of size at most eight.

## 2. Realizing pairs are exact two-transversals

Fix a cross circuit support `C`, viewed as a set of graph-triangle blocks.
Say that an unordered vertex pair `{x,y}` **cross-realizes** `C` when:

1. every block in `C` contains exactly one of `x,y`; and
2. each of `x,y` occurs in at least one block of `C`.

Every circuit chosen in Section 1 is realized by its indexing pair.  For
edges, the deleted common block is why "exactly one" holds.

The requirement that both endpoints occur is essential: a full one-star
circuit may exact-hit many irrelevant pairs one-sidedly, but it
cross-realizes none of them.

Let `R_cross(C)` be the family of cross-realizing pairs.  We prove

```text
|R_cross(C)| <= 3.                                (1)
```

## 3. Pairwise-intersecting realizing pairs

First suppose every two members of `R_cross(C)` intersect.  A pairwise-
intersecting family of two-subsets is either a star or the three edges of
a triangle.

The triangle alternative is impossible.  If its ground vertices are
`a,b,c`, every support block would have to contain exactly one endpoint
of each of `{a,b}`, `{a,c}`, and `{b,c}`.  The three zero-one membership
conditions

```text
chi_a+chi_b=chi_a+chi_c=chi_b+chi_c=1
```

have no solution.

Therefore all realizing pairs share a center `x`; write them `{x,y}` for
`y` in a leaf set `Y`.  Because every realization is cross, some support
block avoids `x`.  Exact transversality then forces that one three-vertex
block to contain every member of `Y`.  Hence `|Y|<=3`, proving (1) in this
case.

## 4. Disjoint realizing pairs

Now suppose `R_cross(C)` contains disjoint pairs

```text
X={x_0,x_1},  Y={y_0,y_1}.
```

Every support block contains one `x_i` and one `y_j`.  There are only four
cross-pair patterns, and a fixed graph-vertex pair belongs to at most one
triangle because `lambda=1`.  Therefore `|C|<=4`.  Wave 174 gives
`|C|>=4`, so all four patterns occur:

```text
T_ij={x_i,y_j,t_ij},  i,j in {0,1}.               (2)
```

Neither `X` nor `Y` can be an edge.  If, for example, `X` were an edge,
then `y_0` and `y_1` would be two distinct common neighbors of it,
contradicting `lambda=1`.

It remains to exclude more than the two displayed realizations.  A third
realizing pair containing one of the four endpoints must be `X` or `Y`.
For example, if it contains `x_0`, its other endpoint must lie in both
`T_10` and `T_11`.  Those distinct triangles already meet at `x_1`; a
second common vertex would put two triangles on one graph edge.  Thus the
other endpoint is `x_1`.

A third realization avoiding all four endpoints could only use the third
vertices in (2).  Adjacent cells cannot share a third vertex, again because
that would put two triangles on one edge.  Covering all four blocks with
two third vertices would therefore require a diagonal repetition.  Even
one diagonal repetition is impossible.  For example, if

```text
t_00=t_11=a,
```

then the edge `x_0 y_1` has both `t_01` and `a` as common neighbors:
`t_01` is the third vertex of `T_01`, while `a` is adjacent to `x_0`
through `T_00` and to `y_1` through `T_11`.  The other diagonal is
symmetric.  This contradicts `lambda=1`.

Thus the disjoint case has exactly two realizations, and (1) follows.

## 5. Balanced edge circuits are globally isolated

Wave 178 gives, for every graph edge `xy`, a circuit with equally many
support blocks on its two sides.  Its size is `4`, `6`, or `8`, so there
are at least two blocks on each side.

Such a circuit cannot cross-realize a second vertex pair.  A disjoint pair
is impossible by Section 4 because one displayed pair, `xy`, is an edge.
If a second pair shares `x`, write it `{x,z}`.  Every support block on the
`y`-side avoids `x`, so cross-realization by `{x,z}` forces all those
blocks to contain `z`.  At least two distinct graph triangles would then
contain the edge `yz`, contradicting `lambda=1`.  The case sharing `y` is
symmetric.

Thus the 693 edge circuits from Wave 178 cross-realize no nonedge pair, as
well as being distinct from one another.

## 6. Global enumerator consequence

There are

```text
693 edges and 4158 nonedges.
```

The edges supply 693 globally isolated projective circuit supports.  Assign
a circuit from Section 1 to each nonedge.  By (1), each remaining support
receives at most three nonedge assignments.  The nonedges therefore require

```text
4158/3=1386
```

additional projective circuit supports.  Altogether there are at least

```text
693+1386=2079
```

distinct projective circuits of sizes `4..9`.

The columns represent a projective matroid.  A circuit support has a
one-dimensional coefficient kernel, so over `F_3` it contributes exactly
two nonzero scalar words.  Writing `B_i` for the dual weight distribution,

```text
B_4+B_5+B_6+B_7+B_8+B_9 >= 2*2079 = 4158.         (3)
```

Wave 178 separately identifies 693 of the projective classes as
edge-unique, even, and balanced, retaining

```text
B_4+B_6+B_8 >= 1386.                               (4)
```

## Boundary

Equations (3)--(4) are new necessary conditions for the conditional
rank-11 endpoint, not an inconsistency.  Average circuit incidence does not
give all-coordinate disjoint availability, and ordinary circuit-count
bounds discard the exact two-transversal and signed-balance data.

No rank-11 contradiction, strict `n3` improvement, graph construction, or
Conway-99 resolution follows.
