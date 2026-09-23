# Root-support girth and multiplicity collapse

## 1. Frozen setting

Assume the independently verified Wave 182 hypotheses and conclusions.
Thus Wave 181 equality `Q=2079` holds, every nonedge `xy` has a norm-one
projective label `rho_xy`, and

```text
R_x intersect R_y={rho_xy}.                       (1)
```

For a global root `r`, define

```text
X_r={x:r in R_x},  m=|X_r|.
```

The color-`r` graph is exactly the complement of `G[X_r]` and is
4-regular.  Therefore

```text
5<=m<=10,
G[X_r] is (m-5)-regular.                          (2)
```

The canonical quadrilateral relation also says that the roots on its two
opposite graph nonedges are orthogonal and have norm one.

## 2. No pair has two common neighbors inside one support

Let `u,v in X_r`.

If `u~v`, the global strongly regular parameter `lambda=1` already says
that they have at most one common neighbor in `X_r`.

If `u` and `v` are nonadjacent, (1) gives

```text
rho_uv=r.
```

Let `c,d` be their two common graph neighbors.  They are nonadjacent:
otherwise the edge `cd` would have the two distinct common neighbors
`u,v`, contradicting `lambda=1`.

If both `c,d` belonged to `X_r`, then (1) would also give

```text
rho_cd=r.
```

But `uv` and `cd` are the opposite nonedges of their canonical
quadrilateral, so Wave 182 gives

```text
rho_uv perpendicular rho_cd.
```

This would make the norm-one root `r` orthogonal to itself, impossible.
Hence every unordered vertex pair in `X_r` has at most one common neighbor
inside `X_r`.                                             (3)

## 3. The two-path bound excludes multiplicities nine and ten

Put `d=m-5`.  Count unordered internal two-paths by their middle vertex.
Equation (3) makes their endpoint map injective, so

```text
m*binomial(d,2)<=binomial(m,2).                   (4)
```

Equivalently,

```text
(m-5)(m-6)<=m-1.
```

For the Wave 182 range `5<=m<=10`, inequality (4) leaves only

```text
m in {5,6,7,8}.                                   (5)
```

In particular, this excludes every multiplicity-nine support, not merely
the earlier all-nine 231-root equality design.

## 4. The cubic eight-point case is impossible

Suppose `m=8`.  Then `G[X_r]` is cubic.  It has

```text
8*binomial(3,2)=24
```

internal two-paths with distinct endpoint pairs by (3).  There are only
16 graph nonedges inside `X_r`, because the complement is 4-regular.
Therefore at least eight adjacent endpoint pairs have a common neighbor
inside `X_r`.

An adjacent pair has an internal common neighbor exactly when its edge lies
in an internal triangle.  Every such triangle accounts for three adjacent
endpoint pairs, and no edge can lie in two triangles because `lambda=1`.
The number of adjacent endpoint pairs counted above is consequently a
multiple of three and at least nine.  Thus `G[X_r]` contains at least three
triangles.

Distinct triangles in a cubic graph satisfying `lambda=1` are
vertex-disjoint.  They cannot share an edge by `lambda=1`; if they shared
only one vertex, that vertex would have four incident triangle edges.
Three such triangles would require at least nine vertices, contradicting
`m=8`.  Hence

```text
m != 8.                                           (6)
```

Combining (5)--(6),

```text
m_r in {5,6,7} for every global root r.           (7)
```

## 5. Exact support shapes

By (2), the three remaining induced degrees are zero, one, and two.
Therefore:

```text
m=5: G[X_r]=5K1,
m=6: G[X_r]=3K2.
```

For `m=7`, the induced graph is 2-regular.  A simple 2-regular graph on
seven vertices is either `C7` or `C3 disjoint_union C4`.  The latter has
two opposite vertices of the `C4` with two internal common neighbors,
contradicting (3).  Thus

```text
m=7: G[X_r]=C7.                                   (8)
```

In particular, no root support contains a graph triangle.

## 6. Root count and frame consequence

Every one of the 99 local root systems has 21 roots, so Wave 182 gives

```text
sum_r m_r=2079.
```

Using (7),

```text
ceil(2079/7)<=|mathcal R|<=floor(2079/5),
297<=|mathcal R|<=415.                            (9)
```

If `n_i` counts roots of multiplicity `i`, then

```text
5*n_5+6*n_6+7*n_7=2079,
7*|mathcal R|-2079=2*n_5+n_6.                    (10)
```

Finally, Wave 182's global root-frame identity is

```text
sum_r m_r r tensor r=0.
```

Reducing the three coefficients in (7) modulo three gives the nontrivial
split

```text
sum_(m_r=7) r tensor r
  =sum_(m_r=5) r tensor r.                        (11)
```

Multiplicity-six roots disappear from this first tensor moment.

## Boundary

The support interval and shapes (7)--(9) are necessary only under Wave 181
equality.  They do not exclude that equality.  Equation (11) is a new
finite-orthogonal target, not a contradiction: neither side is currently
known to have full or incompatible rank.

No strict improvement to `n3<=4158`, rank-11 exclusion, graph construction,
or Conway-99 resolution follows.

