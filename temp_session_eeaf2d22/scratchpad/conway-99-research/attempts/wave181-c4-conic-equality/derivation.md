# Multiplicity-two classification and canonical-C4 equality

## 1. Frozen setting

Assume

```text
n3=4158,  P=0,  rank_F3(D)=11.
```

Retain the verified Waves 171, 174, 179, and 180:

1. for disjoint triangle blocks, their centered pairing is the number of
   cross edges modulo three;
2. distinct intersecting blocks have centered pairing one;
3. the 231 columns are singular and have dual distance at least four;
4. each point-star spans a nondegenerate six-space with projector
   `P_x=-sum z_S tensor z_S`;
5. one short circuit cross-realizes at most three vertex pairs; and
6. every circuit serving three nonedges belongs to the verified
   weight-four/weight-five companion pair.

## 2. Shared-center multiplicity two is impossible

Suppose a circuit `C` cross-realizes exactly the two nonedges

```text
{x,y}, {x,z}.
```

A support block avoiding `x` must contain both leaves.  Thus `y~z`, there is
a unique triangle

```text
T={y,z,t},
```

and every other support block belongs to the `x`-star and avoids `y,z`.
The circuit relation expresses `z_T in E_x`.

### Case 1: x is adjacent to t

Let `S_0` be the unique star block containing the edge `xt`.  It intersects
`T`, so

```text
<z_T,z_(S_0)>=1.                                  (1)
```

Besides `t`, the nonedge `xy` has one further common neighbor `a`, and
`xz` has one further common neighbor `b`.  The vertices `a,b` are distinct:
otherwise their common value would be a second common neighbor of the edge
`yz`, besides `t`.

If `a,b` belonged to the same outer `x`-star block, that block and `T`
would have the three cross edges

```text
xt, ay, bz,
```

forming a forbidden triangular prism.  Hence they lie in two different
outer star blocks.

Every one of the six outer star blocks is disjoint from `T` and already has
the baseline cross edge `xt`.  The two blocks containing `a,b` therefore
have pairing two, while the other four have pairing one.  Together with
(1), the seven star pairings have profile

```text
five 1s and two 2s.
```

Because `z_T in E_x`, projector singularity requires the sum of their
squares to vanish:

```text
0=<z_T,P_x z_T>=-(5+2)=-7=2 mod 3,
```

a contradiction.

### Case 2: x is nonadjacent to t

Now `x` is anticomplete to all of `T`.  The verified Wave 180 projector
classification applies.  The duplicate-vector profile is impossible, and
the surviving local relation space has exactly two circuits involving
`z_T`: the weight-four conic and its weight-five star complement.

Both circuits cross-realize all three nonedges

```text
{x,y}, {x,z}, {x,t}.
```

Thus neither can have exact multiplicity two.

Both cases are impossible.  Therefore

```text
two nonedge realizations with a shared endpoint do not occur.   (2)
```

## 3. The canonical quadrilateral involution

By Wave 179 and (2), every multiplicity-two nonedge circuit has disjoint
realizing pairs

```text
X={x_0,x_1},  Y={y_0,y_1}.
```

Its four support blocks are

```text
T_ij={x_i,y_j,t_ij},  i,j in {0,1}.               (3)
```

All four cross pairs `x_i y_j` are graph edges.  Since `X` is a nonedge and
has exactly two common neighbors,

```text
Y=N(x_0) intersect N(x_1).
```

The pair `Y` is a nonedge: otherwise its edge would have the two common
neighbors `x_0,x_1`, contradicting `lambda=1`.  Applying `mu=2` again gives

```text
X=N(y_0) intersect N(y_1).
```

Thus the map sending a nonedge to its common-neighbor pair is a
fixed-point-free involution.  Its 4,158 nonedges form exactly

```text
4158/2=2079
```

canonical induced quadrilaterals.

## 4. The fixed four-block Gram

In the grid (3), blocks in adjacent cells intersect in one square vertex,
so their centered pairing is one.  The two diagonally opposite blocks are
disjoint.  The other two square edges already give two cross edges between
them.  At `P=0`, a disjoint triangle pair cannot have a third cross edge, so
each diagonal pairing is two.

In the order `00,01,10,11`, the centered Gram matrix is

```text
G =
[0 1 1 2
 1 0 2 1
 1 2 0 1
 2 1 1 0].                                        (4)
```

Exact row reduction over `F_3` gives

```text
rank(G)=3,
ker(G)=<(1,2,2,1)>.                               (5)
```

A true relation on the four columns must lie in (5).  Dual distance four
makes it a circuit, and its equation is

```text
z_00-z_01-z_10+z_11=0.                            (6)
```

Scale the four columns by the coefficients in (6).  Their Gram becomes

```text
2(J_4-I_4).
```

They span a nondegenerate projective plane and are its four singular points,
the complete conic `Q(2,3)`.  Their pure-square sum is the positive
orthogonal projector onto that plane.

Each canonical quadrilateral has only the four blocks (3), so it supports
at most one projective multiplicity-two circuit.

## 5. Equality in the Wave 180 nonedge bound

Let `Q` be the total number of projective short circuits that cross-realize
at least one nonedge.  Wave 180 proves

```text
Q>=2079.
```

Suppose equality holds.  In the Wave 180 inclusion-minimal cover, let `N`
be the number of selected supports and `a` the number serving three
nonedges.  The proof gives

```text
4158<=2N+a,
Q>=N+a.
```

With `Q=2079`, both inequalities can be equalities only when

```text
a=0, N=2079.
```

The sum of all cover-set sizes is then at most `2N=4158`, exactly the size
of their union.  Hence every selected support serves exactly two nonedges,
the label pairs are disjoint, and the cover already contains every one of
the `Q` nonedge-realizing circuits.

By Sections 2--4, these supports are precisely the 2,079 canonical
quadrilateral supports.  Therefore

```text
Q=2079
  implies every canonical induced C4 satisfies (6),
  and no other short circuit cross-realizes a nonedge.            (7)
```

## 6. Signed incidence-rank continuation

Let `R_square` have one row (6) for each of the 2,079 canonical
quadrilaterals and one column for each of the 231 triangle blocks.  Under
the equality hypothesis (7), every row is a true column relation.  Since
the centered column rank is 11,

```text
rank_F3(R_square)<=231-11=220.                    (8)
```

There is also an exact Gram identity.  Each triangle block supplies three
graph edges, each graph edge lies in exactly 12 induced quadrilaterals, and
no induced quadrilateral contains two edges of one triangle.  Thus every
column occurs 36 times.

Two distinct intersecting triangle blocks contribute four quadrilaterals in
which their boundary edges are adjacent; checkerboard signs give product
`-1`.  Two disjoint blocks contribute one quadrilateral with them opposite
exactly when they have two cross edges.  Writing `K` for block intersection
and `L` for the endpoint `j=2` relation,

```text
R_square^T R_square=36I-4K+L over Z,
                     =2K+L over F_3.              (9)
```

A parameter-forced proof that the matrix in (8) has rank at least 221 would
make the Wave 180 lower bound strict.  No such proof is currently known.

## 7. First projector sum is a null boundary

If all 2,079 square supports are conics, let `Q_C` be the rank-three plane
projector from one switched conic.  Switching does not change pure squares,
so

```text
Q_C=sum_(T on C) z_T tensor z_T.
```

Every block occurs in 36 squares.  Consequently

```text
sum_C Q_C=36*sum_T z_T tensor z_T=0 over F_3.      (10)
```

Thus the first global projector sum does not contradict equality.  A
continuation must use the rank in (8)--(9), higher projector products, or
cohomology of the signed square--triangle complex.

## Boundary

The multiplicity-two equality face is now exact, but it survives the first
projector sum.  No strict improvement to the Wave 180 enumerator bound, no
rank-11 exclusion, no strict `n3` upper bound, no graph construction, and no
Conway-99 resolution follows.
