# Wave 39 simultaneous B/H and centered-boundary checks

This package attacks the conditional prism-free endpoint

```text
n3=4158, hence P=0.
```

It makes two exact advances without claiming an endpoint contradiction.

## 1. The surviving ternary equality case is projective after centering

At `r3=12`, write the verified factorization as

```text
C=V H V^T,
w=sum of the seven factor rows through any original vertex,
z_T=v_T-w,
D=C+J.
```

Wave 38 proved

```text
(z_T,z_U)=D_TU,
rank_F3(D)=11,
sum_(T contains x) z_T=0.
```

The new point is that the 231 centered isotropic rows are nonzero and
pairwise nonproportional.

Equality `z_i=z_j` gives the already familiar impossible integer row
difference:

```text
forced norm squared 450, but C^2=441I requires 882.
```

Antipodality is more delicate.  If `z_i=-z_j`, then `C_ij=+2`.  At each of
the other 229 coordinates, the two integer entries must be either

```text
(+2,+2) or (-2,0) in either order.
```

The two row sums force 73 coordinates of the first kind and 156 of the
second.  The integer row sum then has squared norm

```text
2*11^2 + 73*4^2 + 156*2^2 = 2034,
```

whereas orthogonality of distinct rows of `C` requires `882`.  This rejects
antipodality exactly.

The centered rows therefore give 231 distinct oriented isotropic
projective points in the nonsquare eleven-dimensional quadratic space over
`F_3`.  Their inner distribution is

```text
equal, antipodal, inner 0, inner 1, inner 2
  1,       0,       32,      162,      36.
```

The checker reconstructs the full five-relation association scheme by
coordinate dynamic programming.  Its Delsarte transforms on this
distribution are

```text
231, 209/135, 13/27, 493/1107, 23/9.
```

All are positive.  Thus projective centering is a genuine new restriction,
but the ordinary association-scheme positivity test does not exclude the
rank-twelve boundary.

The centered frame also gives a projective self-orthogonal ternary
`[231,11]` code `W`.  Its dual contains the 99 vertex-star rows.  Direct
support recovery gives the necessary low-weight bounds

```text
B_7  >=   198,
B_12 >=  1386,
B_13 >=  1386,
B_14 >= 16632.
```

These are code constraints, not a classification or contradiction.

## 2. What a simultaneous B/H completion must look like

For one base triangle, retain the exact block equations

```text
BB^T       = 12I-A_X+2J-RR^T-A_X^2,
BH         = (J/3-I-A_X)B,
B^TB+H^2  = 12I-H+2J.
```

Let `c4=C4(A_X)`.  If the sixty columns of `B` exist simultaneously, the
unordered pairs of columns have intersection sizes zero, one, and two in
the exact numbers

```text
438+2c4, 1044-4c4, 288+2c4.
```

Compatibility with a simple 8-regular `H` then forces its 240 edges to
split as

```text
96 edges joining disjoint B-columns,
144 edges joining B-columns with intersection one.
```

The `YY` equation has the pointwise form

```text
common_H(y,z)=1-|b_y intersect b_z|  if yz is an H-edge,
common_H(y,z)=2-|b_y intersect b_z|  otherwise.
```

Consequently:

- the 96 overlap-zero edges are exactly the edge-disjoint union of the
  32 triangles of `H`;
- none of the 144 overlap-one edges lies in an `H` triangle;
- for each of the 36 points `x in X`, the ten blocks containing `x` induce
  a four-edge matching in `H`; these matchings partition the 144
  overlap-one edges; and
- if `e_y` is the number of `A_X` edges induced by block `b_y`, then `y`
  lies in `1+e_y` of the 32 edge-disjoint triangles.

For the frozen Wave 38 rank-ten core, `C4(A_X)=4`.  A completion would
therefore have

```text
block overlaps 0/1/2:       446 / 1028 / 296,
H-edge overlaps 0/1:         96 / 144,
H-nonedge overlaps 0/1/2:   350 / 884 / 296,
triangles(H):                 32,
four-cycles(H):              175.
```

No simultaneous `B` or compatible `H` is constructed or excluded.  These
counts narrow the next finite model beyond the individual-column census.

## Reproduction

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave39-simultaneous-bh\exact_check.py `
  --verify attempts\wave39-simultaneous-bh\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave39-simultaneous-bh\test_exact_check.py
```
