# Wave 171: partial-quadrangle and centered block-code reformulation

Status: `VERIFIED` as a reformulation; it is not a new obstruction.

This checkpoint deliberately avoids graph search and large optimization.  It
recasts the target in two human-scale languages:

1. the incidence geometry `PQ(2,6,2)`; and
2. a ternary self-orthogonal code obtained as a polynomial in the
   triangle-block graph.

Let `B` be the `99 x 231` point--triangle incidence matrix and let

```text
K = B^T*B - 3I
```

be the intersection graph of the 231 triangle blocks.  Over `F_3`, put

```text
X = K-K^2.
```

The exact conclusions are:

```text
X^T=X,
X^2=0,
B*X=0.
```

If `p_L` is the number of disjoint blocks joined to a fixed block `L` by
three cross edges, the `L`-row of `X` has symbol composition

```text
(number of 0s, number of 1s, number of 2s)
 = (33, 36-3*p_L, 162+3*p_L).
```

Every row therefore has Hamming weight 198.  Every seven-block point-star
lies in the kernel of `X`.  Moreover, every triangle of `K` lies in one
point-star `K7`; the 99 original points and the incidence matrix `B` can
therefore be recovered intrinsically from `K`, up to row permutation.

For every putative target graph, compare `X` with the verified Wave 35
scaled spectral projector and reflection

```text
M0=21E0,
C=2M0-21I.
```

The exact integral identity `M0=21I+4K-K^2+J` gives, over `F_3`,

```text
X+C=2J.
```

For any point-star vector `s`, one has `X*s=0`, `1^T*s=1`, and hence
`C*s=2*1`.  This yields the exact rank identity

```text
rank_F3(X)=rank_F3(C)-1=r3-1.
```

This rank identity does not require `P=0`.  At the prism-free endpoint, the
previously verified range `12<=r3<=44` becomes

```text
11<=rank_F3(X)<=43.
```

In particular, the difficult endpoint branch `r3=12` is precisely an
explicit `[231,11]_3` centered-code branch.  In fact `X=2(C+J)` over `F_3`,
so this is exactly the Wave 38/39 centered code up to nonzero scalar
multiplication, not a new rank obstruction.

The accompanying source audit also closes a literature ambiguity.  The
Makhnev--Nirova classification for partial quadrangles with `t<=6`
explicitly lists the graph with parameters `(99,14,1,2)` among the remaining
cases; it does not construct or exclude it.  Pech's theorem that partial
quadrangle point graphs satisfy the 5-vertex condition is applicable, but it
does not force 3-isoregularity.  The parameter-forced triad-center
distribution is nonuniform.

No graph, nonexistence proof, strict improvement to `n3<=4158`, or novelty
claim is supplied.  Conway-99 remains `UNKNOWN`.
