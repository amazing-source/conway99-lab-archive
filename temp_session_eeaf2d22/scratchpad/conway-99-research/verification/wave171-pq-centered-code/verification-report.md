# Independent verification report

## Verdict

`VERIFIED_WITH_SCOPE`.

The discovery theorem is correct after two repairs:

1. the Wave 20/35 scaled projector is denoted `M0=21E0`, avoiding a
   dimensional collision with Wave 170's `M=B*B^T`; and
2. the centered-code identity and rank theorem are stated without the
   unnecessary `P=0` hypothesis.

## Exact reconstruction

Let `B` be the `99 x 231` point--triangle incidence matrix and
`K=B^T*B-3I`.  Over `F_3`, `K=B^T*B`.  From

```text
(B*B^T)^2=B*B^T-J,
J*B=0,
```

one obtains `K^3=K^2`.  Therefore

```text
X=K-K^2,
X^2=0,
B*X=0.
```

For a triangle block `L`, an intersecting block has five common neighbors in
`K`, while a disjoint block `M` has `j(L,M)` common neighbors.  Combining
this with the Wave 170 block profile gives

```text
(n0(X_L),n1(X_L),n2(X_L))
  =(33,36-3*p_L,162+3*p_L).
```

Every row has Hamming weight 198 and `X` is nonzero.  If `s_x` is a
seven-block point-star vector, symmetry and `B*X=0` give `X*s_x=0`.

Three pairwise-intersecting triangle blocks must share one point; otherwise
their three pairwise intersections would form a second triangle through an
edge.  Hence every triangle of `K` belongs to a point-star.  The spectral
count

```text
trace(K^3)/6=3465=99*binomial(7,3)
```

cross-checks that these are all the triangles.  Thus the 99 maximal `K7`s,
and hence `B`, are intrinsic in the block graph arising from the putative
SRG.

Finally, the exact projector identity

```text
M0=21E0=21I+4K-K^2+J
```

and `C=2M0-21I` give over `F_3`

```text
X+C=2J,
X=2(C+J).
```

For a point-star `s_x`, `C*s_x=2*1`.  Therefore `1` lies in `row(C)` and
`ker(C)` lies in `1^perp`.  Since `1^T*s_x=1`, adding `J` increases the
kernel dimension by exactly one:

```text
ker(C+J)=ker(C) direct_sum <s_x>,
rank_F3(X)=rank_F3(C)-1.
```

Wave 38's centered matrix is `D=C+J`, so `X=2D`.  The code is precisely the
existing centered code up to a nonzero scalar.  Only after also imposing
the endpoint hypotheses and `r3=12` does it become the projective
`[231,11]_3` lane of Wave 39.

## Scope boundary

- The intrinsic recovery statement assumes `K` is the actual
  triangle-intersection graph of a putative SRG with `lambda=1`; cospectrality
  alone is insufficient.
- Projectivity and the Wave 54 enumerator are not generalized beyond their
  endpoint hypotheses.
- The theorem provides no forbidden rank, construction, endpoint exclusion,
  or improved `n3` bound.
