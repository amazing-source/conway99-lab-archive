# Exact derivation

## 1. Frozen endpoint structure

Assume the conditional endpoint from Wave35.  Fix an arbitrary triangle
`T={t0,t1,t2}` and define `Xi=N(ti)\T`, `X=X0 union X1 union X2`, and
`Y=V\(T union X)`.  The cell sizes are `(3,36,60)`, and the equitable
quotient is

```
Q = [2 12  0
     1  3 10
     0  6  8].
```

No symmetry of the fixed triangle or any other automorphism is assumed.

The characteristic polynomial is

```
det(xI-Q) = x^3 - 13x^2 - 26x + 168
           = (x-14)(x-3)(x+4).
```

## 2. Two-dimensional eigenspaces supported on U

Put `U=T union X`.  Choose numbers `beta_0,beta_1,beta_2` with
`beta_0+beta_1+beta_2=0`.  Give every vertex of `Xi` value `beta_i`,
give `ti` value `alpha_i=lambda beta_i`, and give every vertex of `Y`
value zero.

Every `y in Y` has two neighbours in each `Xi`, so its adjacency sum is
`2(beta_0+beta_1+beta_2)=0`.  The `X` coordinate equation reduces to
`lambda beta_i=alpha_i`.  The `T` equation is

```
lambda alpha_i = -alpha_i + 12 beta_i.
```

Consequently `lambda(lambda+1)=12`, so `lambda` is `3` or `-4`.
The plane `beta_0+beta_1+beta_2=0` has dimension two.  Thus each of the
full `3`- and `-4`-eigenspaces contains an explicit two-dimensional
subspace supported on `U`.

## 3. Projector ranks and exact supported-kernel dimensions

For `srg(99,14,1,2)`,

```
A^2 = 12I - A + 2J
```

and the nontrivial spectral projectors are

```
E_3  = ( A + 4I - (2/11)J)/7,
E_-4 = (-A + 3I + (1/9)J)/7.
```

Let `A_Y` be the adjacency matrix of `G[Y]`.  It is 8-regular.  Restricting
the projectors to the 60 coordinates in `Y` gives

```
E_3[Y,Y]  = ( A_Y + 4I - (2/11)J)/7,
E_-4[Y,Y] = (-A_Y + 3I + (1/9)J)/7.
```

On the all-one vector these blocks have eigenvalues `12/77` and `5/21`,
respectively, so neither loses the regular direction.  On a vector
orthogonal to one with `A_Y`-eigenvalue `theta`, the two block eigenvalues
are `(theta+4)/7` and `(3-theta)/7`.  If

```
a = mult_Y(3),   b = mult_Y(-4),
```

then

```
rank E_3[Y,Y]  = 60-b,
rank E_-4[Y,Y] = 60-a.
```

A principal block of an orthogonal projector is the Gram matrix of the
corresponding coordinate restrictions.  Therefore

```
dim{full 3-eigenvectors supported on U}  = 54-(60-b) = b-6,
dim{full -4-eigenvectors supported on U} = 44-(60-a) = a-16.
```

The explicit two-dimensional sectors force

```
b >= 8,   a >= 18.
```

## 4. Exact star-set hit of U

A star set for an eigenvalue of multiplicity `m` is a basis of `m`
coordinate functionals on its eigenspace.  The most basis elements that
can be selected from `Y` is the rank of the corresponding projector block
on `Y`.  A maximum independent subset extends to a basis, so the following
minimums are exact:

```
minimum |S_3 intersect U|  = 54-(60-b) = b-6,
minimum |S_-4 intersect U| = 44-(60-a) = a-16.
```

In particular, no star set can avoid `U`.  The explicit supported sector
also gives an elementary version: two selected coordinates in the same
sector `Ti union Xi` induce proportional functionals on the beta-plane, so
killing that plane needs coordinates from at least two sector indices.

For a minimum-hit full-graph star set:

- a `3`-star complement has order 45 and contains `b` vertices of `Y`
  and `45-b` vertices of `U`;
- a `-4`-star complement has order 55 and contains `a` vertices of `Y`
  and `55-a` vertices of `U`.

## 5. Triangles and the first three Y moments

The 231 triangles split relative to the fixed `T` as follows:

```
T itself                 1
T plus two X            18
three X                  0
two X plus Y            36
X plus two Y           144
three Y                 32
                       ---
                       231
```

Here the 18 triangles use the six matching edges inside each `Xi`; the 36
use the cross-fibre edges of the triangle-free cubic graph `G[X]`; and each
`x in X` lies in four triangles with two vertices in `Y`.

It follows that `G[Y]` has order 60, degree 8, 240 edges, and 32 triangles:

```
tr(A_Y^0)=60, tr(A_Y)=0, tr(A_Y^2)=480, tr(A_Y^3)=192.
```

After removing the regular eigenvalue 8, `a` copies of 3, and `b` copies
of -4, let the remaining `r=59-a-b` roots be `z_j`.  Their power sums are

```
p1 = -8  - 3a + 4b,
p2 = 416 - 9a - 16b,
p3 = -320 - 27a + 64b.
```

Every `z_j` lies strictly between `-4` and `3`.  The degree-one localizer
for `z+4` has determinant

```
158976 - 7644a,
```

while the localizer for `3-z` has determinant

```
96480 - 7056b.
```

Together with `a>=18`, `b>=8`, positive semidefiniteness gives

```
18 <= a <= 20,   8 <= b <= 13.
```

All 18 Cartesian-product pairs survive the other order-three Hankel and
localizer conditions.

## 6. Four cycles and the fourth moment

Let `B_y=N(y) intersect X` and `c=C4(X)`.  Among adjacent pairs in `Y`,
96 have block intersection zero and 144 have block intersection one.
For nonadjacent pairs, let `n_i` count pairs with block intersection `i`.
Counting pairs inside the 36 ten-element point fibres gives

```
n1 + 2n2 = 1476.
```

Opposite pairs in four-cycles of `X` give

```
n0 = 342+2c,   n1 = 900-4c,   n2 = 288+2c.
```

Hence

```
C4(Y) = 171+c,
tr(A_Y^4) = 8568+8c,
p4 = 4472+8c-81a-256b.
```

The combinatorial counts give `0<=c<=225`.  Apply the order-four Hankel
condition and the localizer for

```
g(z)=(z+4)(3-z)=12-z-z^2.
```

The latter is the exact matrix

```
[300        -192
 -192   840-8c].
```

Its determinant forces `c<=89`.  The full exact feasible intervals are:

| a | b | minimum c | maximum c |
|---:|---:|---:|---:|
| 18 | 8 | 0 | 89 |
| 18 | 9 | 0 | 89 |
| 18 | 10 | 0 | 89 |
| 18 | 11 | 7 | 89 |
| 18 | 12 | 24 | 89 |
| 18 | 13 | 54 | 89 |
| 19 | 8 | 4 | 89 |
| 19 | 9 | 8 | 89 |
| 19 | 10 | 13 | 89 |
| 19 | 11 | 21 | 89 |
| 19 | 12 | 34 | 89 |
| 19 | 13 | 57 | 89 |
| 20 | 8 | 41 | 89 |
| 20 | 9 | 42 | 89 |
| 20 | 10 | 44 | 89 |
| 20 | 11 | 47 | 89 |
| 20 | 12 | 52 | 89 |
| 20 | 13 | 65 | 89 |

## 7. Exact scalar controls

For 16 of the 18 pairs, `exact-results.json` supplies a multiset supported
on the integer roots `{-3,-2,-1,0,1,2}` that matches `p0` through `p4`
for an allowed `c`.

The remaining two pairs have algebraic-integer controls:

- `(a,b)=(20,8)`: four copies of the two roots of
  `x^2+4x+1`, plus integer-root counts `(4,4,0,15,0,0)`;
  this gives `c=45`.
- `(a,b)=(20,9)`: four copies of the two roots of
  `x^2+5x+5`, plus integer-root counts `(3,0,4,14,1,0)`;
  this gives `c=50`.

The count tuples use root order `(-3,-2,-1,0,1,2)`.  Both quadratics have
two real roots strictly in `(-4,3)`.  Their conjugates occur with equal
multiplicity, so the corresponding characteristic-polynomial factors are
monic integral.  The checker verifies all power sums, Newton divisibilities,
and moment-localizer conditions exactly.

These are failure-of-obstruction controls only.  They do not show that the
multisets are spectra of simple graphs.

## 8. Smaller exact compatibility problem

The full 99-vertex question reduces to the following necessary 60-vertex
problem.  Find an 8-regular simple graph `A_Y` with 32 triangles and a
compatible `c` row from the table such that

```
rank(11A_Y+44I-2J) = 60-b in [47,52],
rank(-9A_Y+27I+J)  = 60-a in [39,42].
```

Equivalently, inside `Y` one may select:

- a star complement for eigenvalue 3 of order `60-a`, hence 40 to 42;
- a star complement for eigenvalue -4 of order `60-b`, hence 47 to 52.

For a star set `S`, star complement adjacency matrix `C`, and binary
incidence matrix `B`, the Reconstruction Theorem requires

```
mu I-A_S = B^T (mu I-C)^(-1) B,
```

with `mu` absent from the spectrum of `C`.  This is a finite exact
compatibility target materially smaller than the original graph, but the
present run does not construct or exhaust its binary matrices.

## 9. Conclusion

The spectral compression is nontrivial: it forces exact supported eigenspaces,
a small multiplicity box, quantified star-set intersections, and a bounded
four-cycle ledger.  The exact scalar controls show that the resulting trace
and algebraic-integrality constraints remain feasible.  Therefore the endpoint
is not excluded and Conway-99 remains `UNKNOWN`.
