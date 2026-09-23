# Derivation

All matrices in Sections 1--4 are reduced modulo three unless an integer
lift is explicitly mentioned.

## 1. The block graph and its nilpotent polynomial

Let `B` be the point--triangle incidence matrix.  Every triangle has three
points and every point belongs to seven triangles.  The block-intersection
graph has adjacency matrix

```text
K=B^T*B-3I,
```

so over `F_3`,

```text
K=B^T*B.
```

On the point side,

```text
G=B*B^T=A+7I=A+I.
```

The strongly regular graph identity

```text
A^2=12I-A+2J
```

gives

```text
G^2=G-J.
```

Because every column of `B` has sum three,

```text
J*B=0.
```

Consequently

```text
B*(K-K^2)
 =G*B-G^2*B
 =J*B
 =0.                                               (1)
```

Put `X=K-K^2`.  Multiplying (1) on the left by `B^T` gives `K*X=0`, or
equivalently `K^2=K^3`.  Hence `K^4=K^2` and

```text
X^2
 =K^2-2K^3+K^4
 =0.                                               (2)
```

The matrix is symmetric because it is a polynomial in the symmetric matrix
`K`.

## 2. Exact row composition

Fix a triangle block `L`.  For a disjoint block `M`, let `j(L,M)` be the
number of cross edges between their point triples.  Wave 170 proves that, if
`p_L` counts the blocks with `j=3`, then the numbers of disjoint blocks with
`j=0,1,2,3` are

```text
(32-p_L, 144+3*p_L, 36-3*p_L, p_L).               (3)
```

There are 18 blocks meeting `L`.  Two intersecting blocks have exactly five
common block neighbors: the five other blocks through their common point.
There is no further common neighbor, because that would give an adjacent
point pair two common neighbors in the original graph.

For disjoint blocks, a common block neighbor is the unique triangle through
one cross edge.  Thus `(K^2)_(L,M)=j(L,M)`.  Reducing `X=K-K^2` modulo three
gives the following table.

| relation to `L` | number | `X_(L,M)` |
|---|---:|---:|
| `M=L` | 1 | 0 |
| intersects `L` | 18 | `1-5=2` |
| disjoint, `j=0` | `32-p_L` | 0 |
| disjoint, `j=1` | `144+3*p_L` | 2 |
| disjoint, `j=2` | `36-3*p_L` | 1 |
| disjoint, `j=3` | `p_L` | 0 |

Therefore every row has composition

```text
(0,1,2)=(33,36-3*p_L,162+3*p_L)                  (4)
```

and constant Hamming weight 198.  In particular `X` is nonzero.

If `s_x=B^T e_x` is the incidence vector of the seven blocks through an
original point `x`, equation (1) and symmetry give

```text
X*s_x=0.                                          (5)
```

The row space of `X` is consequently a ternary self-orthogonal code, and the
99 point-stars lie in its dual.

## 3. Intrinsic recovery of the incidence geometry

Three vertices of `K` are three pairwise-intersecting triangle blocks.
Suppose their three pairwise intersection points were distinct.  Those
points would be pairwise adjacent in the original graph.  Since every edge
lies in a unique triangle, each of the three blocks would then be the unique
triangle on the same three points, a contradiction.  Thus every triangle of
`K` consists of three blocks through one common point.

As a spectral cross-check,

```text
spec(K)=18^1,7^54,0^44,(-3)^132
```

gives

```text
trace(K^3)/6=3465=99*binomial(7,3).
```

Every edge of `K` is contained in the seven-block star of its intersection
point.  Therefore the maximal cliques of `K` are exactly the 99 point-star
`K7`s.  Taking these cliques as rows recovers `B` from `K`, up to row
permutation.  This uses no automorphism assumption.

## 4. Exact identification with the centered code

Write `E0` for the primitive idempotent of `K` belonging to eigenvalue zero.
The verified Wave 20/35 scaled spectral projector and reflection are

```text
M0=21E0=21I+4K-K^2+J,
C=2M0-21I.
```

This notation avoids collision with Wave 170's use of `M=B*B^T`.  Reducing
the two identities modulo three gives

```text
M0=X+J,
C=2(X+J),
X+C=2J,                                           (6)
X=2(C+J).                                         (7)
```

Let `s` be any point-star vector.  Since `1^T*s=7=1` and `X*s=0`,
equation (6) gives

```text
C*s=2*1.                                          (8)
```

Thus `1` belongs to `row(C)`.  Since `C` is symmetric,

```text
ker(C) subset 1^perp.                             (9)
```

Equations (6)--(7) give

```text
row(C)=row(X)+<1>.
```

The sum is direct: if `1` belonged to `row(X)`, then `1^T*s=1` would
contradict `X*s=0`.  Hence

```text
row(C)=row(X) direct_sum <1>,
rank_F3(X)=rank_F3(C)-1.                          (10)
```

Equivalently, put `phi=1^T` and `T=I-s*phi`.  This is the projection onto
`1^perp` with kernel spanned by `s`.  Equations (6)--(8) give `X=-C*T`;
then (9) gives (10) again.  These identities hold for every putative target
graph and do not require the prism-free endpoint.

Now assume `P=0`, equivalently `n3=4158`.  Writing
`r3=rank_F3(C)`, the verified Wave 36 endpoint bound `12<=r3<=44` yields

```text
11<=rank_F3(X)<=43.
```

Indeed Wave 38's centered Gram matrix is `D=C+J`, so `X=2D`.  For `r3=12`,
the row code of `X` is exactly the centered `[231,11]_3` block-code lane
studied in Waves 39 and 54, up to multiplication by two.  The ordinary
enumerator in that lane is formally feasible, so (10) is an identification
rather than an endpoint contradiction.

## 5. Partial-quadrangle translation

Because `lambda=1`, the maximal cliques of the original graph are its unique
edge-triangles.  The graph is exactly the point graph of a partial quadrangle

```text
PQ(2,6,2).
```

The Makhnev--Nirova `t<=6` theorem retains the `(99,14,1,2)` case explicitly.
Pech proves that every partial-quadrangle point graph satisfies the 5-vertex
condition, but not that it is 3-isoregular.

There are 98,406 independent triples.  Exactly

```text
99*binomial(7,3)*2^3=27,720
```

have a common neighbor, and no independent triple can have two common
neighbors.  Thus the triad-center average is

```text
27720/98406=20/71,
```

so the triad-center count is necessarily nonuniform.  A route that tries to
deduce 3-isoregularity from the parameters, or from `P=0` without an
additional theorem, is therefore invalid.

## Boundary

The polynomial code exposes the endpoint's existing centered ternary
structure directly from the intrinsic block graph.  It supplies no forbidden
rank, weight enumerator, partial-quadrangle classification, strict upper
bound, construction, or nonexistence proof.
