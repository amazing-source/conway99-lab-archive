# Invariant-space derivation

Write the symmetrized enumerator as `P(u,v,w)` in state order
`(nI,nY,nR)`. Let `S` be the normalized self-dual MacWilliams substitution
and `P_y` the reflection `v -> -v`.

Direct matrix multiplication gives

```text
S^2=P_y^2=1,  (S P_y)^3=1.
```

Their traces on the linear variables are respectively `1,1,0` for a
transposition, transposition, and three-cycle. This is the three-dimensional
permutation representation of `S3`.

The forms

```text
x1=u+v+2w,
x2=u-v+2w,
x3=2u
```

are permuted: parity swaps `x1,x2`, while MacWilliams swaps `x1,x3`.
Consequently the common fixed ring is the symmetric polynomial ring in
`x1,x2,x3`, with generator degrees `1,2,3`.

At total degree 99, a basis is

```text
m_lambda(x1,x2,x3),
```

over partitions `lambda` of 99 into at most three parts. There are exactly
867 such partitions. Since even `nY` supplies 2,550 coordinates, the
restricted self-duality/parity equality rank is `2550-867=1683`.

`gf4_model.py` expands every basis coefficient with integer arithmetic and
checks representative columns by evaluation at `(u,v,w)=(1,1,1)`.
