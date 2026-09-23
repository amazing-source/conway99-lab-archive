# Root-system gluing on the canonical-C4 equality face

## 1. Equality hypothesis

Assume the verified conditional rank-11 endpoint and equality in Wave 181:

```text
Q=2079.
```

Every canonical induced quadrilateral is then a checkerboard conic.  For a
nonedge `xy`, let its two common neighbors be `c,d`.  Write `T_uv` for the
unique triangle block on an edge `uv`.  The Wave 181 relation is

```text
z_(T_xc)-z_(T_xd)=z_(T_yc)-z_(T_yd),              (1)
```

after choosing compatible signs.

Define the projective point

```text
rho_xy=<z_(T_xc)-z_(T_xd)>.                       (2)
```

Changing the order of `c,d` only changes sign.  Equation (1) gives

```text
rho_xy in E_x intersect E_y.                      (3)
```

The two blocks in (2) intersect at `x`, so their centered pairing is one.
They are singular, and therefore

```text
norm(rho_xy)=-2=1 mod 3.                          (4)
```

Thus every nonedge receives a projective norm-one label.

## 2. The 21 local simplex-difference roots

Fix `x` and write its seven star columns as `z_1,...,z_7`.  They have Gram
`J_7-I_7`, sum zero, and only the full seven-column relation.

The 14 neighbors of `x` are partitioned into the seven pairs belonging to
these triangle blocks.  Two neighbors in different pairs are nonadjacent:
if they were adjacent, their edge would lie in a triangle with the common
neighbor `x`, placing them in the same pair.

Conversely, every pair `c,d` chosen from two different star pairs has
exactly two common neighbors.  One is `x`; call the other `y`.  This gives a
bijection

```text
nonneighbors y of x
  <--> unordered pairs {c,d} from different star pairs.           (5)
```

There are

```text
binomial(14,2)-7=84
```

such pairs.  For a fixed pair of star blocks `{i,j}`, the four choices of
one neighbor from each block all give the same projective label

```text
<z_i-z_j>.
```

The 21 labels

```text
R_x={<z_i-z_j>:1<=i<j<=7}                         (6)
```

are distinct.  Any equality between two different projective differences
would produce a nonzero relation on at most four star columns, contradicting
the simplex relation space.  Each point in (6) has norm one and labels
exactly four nonedges at `x`.

This is the 21-point projective difference-root system of the negative
`A6` simplex form.

## 3. Exact intersection on nonedges

Equation (3) gives `rho_xy in R_x intersect R_y`.  Suppose a second
projective root lay in the intersection.  Equating its two difference
representations would produce a weight-four relation on two blocks from
the `x`-star and two from the `y`-star.  The stars are disjoint because
`xy` is a nonedge, and dual distance four makes the support a circuit.

Every one of its blocks contains exactly one of `x,y`, so this new circuit
cross-realizes the nonedge `xy`.  It is different from the canonical support
unless the root is `rho_xy`.  But Wave 181 equality says the 2,079 canonical
circuits are all nonedge-realizing short circuits.  Therefore

```text
R_x intersect R_y={rho_xy} for every nonedge xy.  (7)
```

## 4. Root colors are 4-regular complement graphs

Let `mathcal R` be the set of distinct projective roots appearing in at
least one `R_x`.  For `r in mathcal R`, put

```text
X_r={x:r in R_x},
m_r=|X_r|.
```

Color every complement edge `xy` by `rho_xy`.  At a vertex `x in X_r`,
Section 2 shows that exactly four complement edges at `x` have color `r`.

Moreover, if `x,y in X_r` are nonadjacent in the original graph, (7) forces
their label to be `r`.  Hence the color-`r` graph is exactly

```text
H_r=complement(G[X_r]),
```

and it is 4-regular.

Consequently `m_r>=5`.  For an edge `uv` of `H_r`, the other neighbors of
`u` and `v` in `H_r` occupy at most `3+3` vertices.  At least

```text
m_r-2-6=m_r-8
```

vertices of `X_r` are therefore adjacent to both `u,v` in the original
graph.  Since `uv` is a graph nonedge and `mu=2`,

```text
m_r<=10.                                           (8)
```

Counting the 21 roots in every star gives

```text
sum_(r in mathcal R) m_r=99*21=2079.              (9)
```

The lower bound in (8) already gives `|mathcal R|<=floor(2079/5)=415`.

## 5. Common roots on graph edges

Let `x~y`, and let `T_0` be their common triangle block.  A common root of
`R_x,R_y` cannot use `T_0` in either difference representation.

If both representations used `T_0`, equating them up to sign would produce
a relation of weight at most three or duplicate columns.  If only one used
`T_0`, pairing the resulting four-column relation with `z_(T_0)` gives

```text
-1
```

independently of the projective sign, so it cannot be a relation.

Thus every common root comes from two outer blocks on each side.  Equating
the two difference roots gives a balanced weight-four outer edge circuit.
Wave 178's exact four-cycle-type Gram classification allows at most six
projective weight-four directions for one edge: its largest case is cycle
type `3+3`, with 12 nonzero scalar words.

Therefore

```text
|R_x intersect R_y|<=6 for every graph edge xy.   (10)
```

Double-counting pairs of stars through global roots and using (7), (10)
gives

```text
sum_r binomial(m_r,2)
 =sum_(x<y) |R_x intersect R_y|
 <=4158+693*6
 =8316.                                            (11)
```

Together with (9),

```text
sum_r m_r^2
 =2*sum_r binomial(m_r,2)+sum_r m_r
 <=18711
 =9*2079.                                          (12)
```

Cauchy--Schwarz now yields

```text
2079^2
 <=|mathcal R|*sum_r m_r^2
 <=|mathcal R|*18711,

|mathcal R|>=231.                                  (13)
```

Combining (8)--(13),

```text
231<=|mathcal R|<=415,
5<=m_r<=10.                                        (14)
```

## 6. The rigid 231-root equality case

If `|mathcal R|=231`, every inequality in (12)--(13) is equality.
Consequently

```text
m_r=9 for every root r,                            (15)
|R_x intersect R_y|=6 for every graph edge xy.    (16)
```

Wave 178's local table then forces every adjacent star pair to have cycle
type `3+3`, and all six projective weight-four Gram-kernel directions must
be true relations.

The `99 by 231` star--root incidence matrix `F` has row sum 21, column sum
9, and pair intersections six on graph edges and one on nonedges:

```text
F F^T=20I+5A+J over the integers.                 (17)
```

Its real eigenvalues are

```text
189^1, 35^54, 0^44.
```

Thus the first incidence-spectrum test is exactly positive semidefinite and
does not exclude the extremal design.

## 7. Orthogonality and frame identities

For one canonical quadrilateral, let

```text
r=z_00-z_01,
s=z_00-z_10
```

be the labels on its two opposite graph nonedges.  The fixed Wave 181 Gram
matrix gives

```text
<r,s>=0,
<r,r>=<s,s>=1.                                    (18)
```

Thus the nonedge involution pairs orthogonal norm-one roots.

For a fixed star, the standard simplex-difference identity gives

```text
sum_(i<j) (z_i-z_j) tensor (z_i-z_j)
 =7*sum_i z_i tensor z_i
  -(sum_i z_i) tensor (sum_i z_i)
 =sum_i z_i tensor z_i
 =-P_x.                                            (19)
```

Summing (19) over all 99 stars and using `sum_x P_x=0`,

```text
sum_(r in mathcal R) m_r r tensor r=0.            (20)
```

At the extremal value (15), every coefficient `m_r=9` vanishes in `F_3`.
The frame identity (20) is then coefficientwise zero and supplies no
contradiction.

## Boundary

Wave 181 equality is now recast as a gluing of 99 negative-`A6`
projective root systems with 4-regular complement color classes and the
sharp support bounds (14).  The extremal 231-root case becomes the explicit
two-class incidence design (17), but it survives both the incidence spectrum
and the first root-frame sum.

No strict improvement to the Wave 180 enumerator bound, no rank-11
exclusion, no strict `n3` upper bound, no graph construction, and no
Conway-99 resolution follows.
