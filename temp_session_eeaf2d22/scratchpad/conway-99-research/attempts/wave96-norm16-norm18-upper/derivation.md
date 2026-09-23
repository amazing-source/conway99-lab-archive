# Weighted C4 incidence, the projector wall, and norm 20

Claim label: `DERIVED`; independent verification required.

## 1. The exact rank-28 weighted target

Wave 86 gives the positive identity

```text
2387*N14 + 407*N16 + 43*N18 >= 13,980,652.
```

At the prism-free endpoint, verified Wave 99 gives `N14<=4950`.  On the
intersection with rank 28 this forces

```text
407*N16 + 43*N18 >= 2,165,002.                 (1)
```

All `N` counts are oriented and include both signs.

The graph has 4,158 nonedges.  Each nonedge is the diagonal of a unique
induced four-cycle, while every four-cycle has two diagonals.  Hence

```text
C4(G)=2079.                                    (2)
```

Let `A16=N16/2`, `A180=N18,h=0/2`, and
`A181=N18,h=1/2` be antipodal support counts.  Pair-codegree counting in the
verified signed supports gives at least

```text
20*A16 + 18*A180 + 26*A181                     (3)
```

support--C4 incidences.  If every target C4 lay in at most `E` of these
antipodal supports, (2)--(3) would give

```text
I <= 2079*E.
```

The weighted objective satisfies

```text
407*N16+43*N18
 = 814*A16+86*A180+86*A181
 <= (407/10)*(20*A16+18*A180+26*A181)
 <= (407/10)*2079*E.                           (4)
```

For `E=25`, the right side is `4,230,765/2`.  The objective is an even
integer, so it is at most `2,115,382`, contradicting (1).  For `E=26`,
this numerical implication fails.  Thus 25 is the exact integer cap target
for this relaxation.

Equivalently, (1) forces at least

```text
ceil(10*2,165,002/407)=53,195
```

support--C4 incidences, so some four-cycle lies in at least 26 antipodal
norm-16/norm-18 supports.

## 2. Fixed-cycle type partition is not the cap

Fix an induced C4 with same-sign diagonals
`P={p1,p2}` and `N={n1,n2}`.  No outside vertex can meet both vertices of
either diagonal.  Each of the four cycle edges has one distinct external
common neighbor.  The 95 outside vertices therefore split exactly as

```text
51 adjacent to no anchor,
20 adjacent only to one P anchor,
20 adjacent only to one N anchor,
4 adjacent to one P and one N anchor.
```

For a norm-16 support, the remaining six `P` vertices use two vertices from
each ten-element N-anchor-only fiber and two of the 51 zero-type vertices.
The remaining `N` vertices do the symmetric thing, with disjoint zero-type
choices.  Before any independence or support-edge test, this leaves

```text
C(10,2)^4 * C(51,2) * C(49,2)
  = 6,148,477,125,000
```

type-compatible selections.  The partition is a useful exact starting
domain but supplies no small upper bound.

## 3. The common projector does not prove 25

The `-4` eigenspace projector is

```text
E=(27I-9A+J)/63.
```

On an ordered induced C4 with adjacency matrix `H`, every cycle has the
same principal Gram matrix

```text
E[C,C]=(3I-H+J/9)/7.                            (5)
```

For the alternating sign pattern `s=(1,-1,1,-1)`, `Hs=-2s` and `Js=0`.
The minimum-norm vector in the `-4` eigenspace with these four fixed
coordinates has squared norm

```text
s^T E[C,C]^-1 s = 28/5.                        (6)
```

Consequently, norm-16 extensions have residual squared radius `52/5` in
the 40-dimensional kernel of the four coordinate evaluations; norm-18
extensions have radius `62/5`.

Distinct lattice vectors are separated by squared distance at least 14.
But the purely spherical norm-16 relaxation contains the 80 vertices of a
40-dimensional cross-polytope at radius squared `52/5`.  Its minimum
pairwise squared distance is

```text
2*(52/5)=104/5 > 14.
```

Therefore the common projector, dimension, radius, and minimum-distance
conditions alone admit 80 fixed-pattern points.  They cannot prove the
needed cap 25.  Integrality, the actual lattice coset, or graph incidence
compatibility must enter.

## 4. Exact norm-20 magnitude classification

The Wave 71 nonintegral coordinate classes have energy at least 22, so a
norm-20 vector still corresponds to an integer vector

```text
t in Z^99,  1^T t=0,  At=-4t,  sum t_i^2=20.
```

First, `|t_i|<=2`.  If `|t_i|>=3`, its neighbor sum has magnitude at least
12.  Since integer `a` satisfies `a^2>=|a|`, the neighbors alone have
squared mass at least 12, while only `20-9=11` remains after the chosen
coordinate.

Let `m` count magnitude-two coordinates.  The odd support has weight
`20-4m` and is a nonzero word of `ker_F2(A)`.  Its verified minimum weight
eight gives `m<=3`.  It cannot be the zero word: that would require five
magnitude-two coordinates, and an odd number of values in `{+2,-2}` cannot
sum to zero.  Exact zero-sum enumeration gives six profiles up to global
sign:

```text
m=0:  10(+1),10(-1)
m=1:  1(+2),7(+1),9(-1)
m=2:  2(+2),4(+1),8(-1)
      1(+2),1(-2),6(+1),6(-1)
m=3:  3(+2),1(+1),7(-1)
      2(+2),1(-2),3(+1),5(-1)
```

The mixed profiles are excluded as follows.

- Both `m=3` profiles have total negative mass at most seven, insufficient
  for the neighbor sum `-8` at a `+2`.
- In the first `m=2` profile, both `+2` vertices must meet all eight
  negative units and no positive nonzero vertex.  They are nonadjacent and
  have eight common neighbors, contradicting `mu=2`.
- In the mixed `m=2` profile, the `+2` meets the `-2` and all six negative
  units.  Every positive unit also meets the `-2` and at least two negative
  units, so it has at least three common neighbors with the nonadjacent
  `+2`, again contradicting `mu=2`.
- For `m=1`, the `+2` has at least eight neighbors among the nine negative
  units: positive neighbors only increase the negative demand in its
  equation.  Every positive unit has at least four negative-unit neighbors.
  Their two negative-neighbor sets therefore intersect in at least
  `8+4-9=3` vertices.  This contradicts `lambda=1` if the `+2` and unit
  are adjacent and `mu=2` if they are not.

Thus only

```text
boxed: ten +1 and ten -1
```

survives.

## 5. Norm-20 C4 count and the rank-30 target

Let `h` be the common number of same-sign edges in the two ten-point sign
sides.  The support has `40+4h` edges.  The restricted eigenvalue bound on
20 vertices is `5170/99<53`, so `h<=3`.

If the degrees on one sign side are `r_i`, the cross degrees are `4+r_i`,
and the total cross codegree of pairs on the opposite side is

```text
T=sum_i C(4+r_i,2)
 =60+7h+(1/2)sum_i r_i^2.
```

Each of the 45 pairs has cross codegree at most one as a baseline; only a
nonadjacent pair may have codegree two and then supplies an alternating
induced C4.  Hence the number of alternating C4s is at least `T-45`.
For `h=0,1,2,3` this is at least `15,23,31,39`, respectively.  Every
norm-20 support therefore contains at least 15.

Verified Wave 101 gives, in the `q=14` / rank-30 row,

```text
x7+x8+x9+x10 >= 6842.
```

The norm-20 classification identifies `x10=N20`, extending the graph
dictionary by one coefficient.  Since all four shells through norm 20
contain at least 15 alternating C4s, some target cycle occurs in at least
50 oriented vectors, or 25 antipodal supports.  A universal cap of 24
antipodal extensions through norm 20 would exclude rank 30.  It is not
proved here.

## 6. Coordinate-sensitive continuation

For each induced C4, form the four-variable marked theta/Jacobi series whose
Laurent exponents are the four coordinate evaluations.  Summing over all
2,079 cycles preserves a common index matrix (5).  The sum of the two
alternating Laurent coefficients at `q^8` and `q^9` is exactly the oriented
norm-16/norm-18 support--C4 incidence.  A proof-producing Jacobi-form LP
could therefore target the total incidence directly without a pointwise
cap.

Equivalently, the degree-eight polynomial

```text
F(t)=sum_C4 product_{v in C4} t_v^2
```

counts contained cycles on unit short vectors.  Its harmonic components
produce marked theta series of weights 22 through 30.  This route requires
the exact lattice-coset/Jacobi transformation law and control of signed
harmonic coefficients; scalar theta positivity alone does not provide
them.

## Boundary

The weighted lower bound, C4 minima, projector calculation, spherical null
control, and norm-20 classification are finite exact consequences.  The
pointwise caps 25 and 24 remain open.  No rank row is excluded.
