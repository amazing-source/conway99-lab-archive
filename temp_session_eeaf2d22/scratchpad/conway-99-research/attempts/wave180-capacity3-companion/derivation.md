# Conic-companion classification and global count

## 1. Frozen conditional setting

Assume

```text
n3=4158,  P=0,  rank_F3(D)=11.
```

Use the independently verified model from Waves 174--179.  The 231 triangle
blocks give singular, projectively distinct columns `z_T` in a nondegenerate
11-space over `F_3`, and the dual distance is at least four.

For every graph vertex `x`, its seven triangle blocks form a simplex:

```text
Gram(S_x)=J_7-I_7,
sum_(S in S_x) z_S=0.
```

They span a nondegenerate six-space `E_x`.  Its orthogonal projector is

```text
P_x=-sum_(S in S_x) z_S tensor z_S.                (1)
```

Wave 179 defines `R_cross(C)` using exact two-transversals and proves

```text
|R_cross(C)|<=3                                   (2)
```

for every short cross circuit support `C`.  It also supplies 693 distinct
edge circuits that cross-realize no nonedge.

## 2. Shape of equality in the transversal bound

Let `C` be a circuit whose cross-realization set consists of three nonedges.
The pairwise-intersecting part of the Wave 179 proof forces

```text
R_cross(C)={{x,y_0},{x,y_1},{x,y_2}}              (3)
```

with a common center `x`.  A support block avoiding `x` must contain all
three leaves, so the leaves form the unique triangle block

```text
T={y_0,y_1,y_2}.
```

Every other support block contains `x` and avoids all three leaves.  Hence

```text
C subset {T} union S_x.                            (4)
```

The circuit cannot contain the whole seven-block star, because that star is
already a proper dependent subset.  In particular, the relation on `C`
expresses

```text
z_T in E_x.                                        (5)
```

All three pairs in (3) are nonedges, so `x` is anticomplete to `T`.

## 3. The seven local cross-edge counts

Enumerate the blocks in `S_x` as `S_1,...,S_7` and put

```text
j_i=j(T,S_i).
```

For each `y` in `T`, the nonedge `xy` has exactly two common neighbors.
These six common-neighbor incidences are at distinct outside vertices: a
vertex adjacent to two points of `T` would be a second common neighbor of
their edge, besides the third point of `T`, contradicting `lambda=1`.

Each `S_i` has only two vertices besides `x`, so `j_i` lies in `{0,1,2}`.
Writing

```text
t=number of i with j_i=2,
```

the total of six incidences gives the exact profile

```text
(m_0,m_1,m_2)=(1+t,6-2t,t),  0<=t<=3.             (6)
```

At the endpoint, the verified centered Gram table for disjoint blocks is

```text
h_i=<z_T,z_(S_i)>=j_i mod 3.                       (7)
```

## 4. Projector singularity leaves only t=0 or t=3

By (5), `P_x z_T=z_T`.  Since `z_T` is singular, (1) gives

```text
0=<z_T,P_x z_T>
 =-sum_i h_i^2
 =-(6-t) mod 3.
```

Therefore

```text
t in {0,3}.                                        (8)
```

Suppose first that `t=0`.  Then `h` has six entries one and one entry zero.
If the zero occurs at `S_0`, this is exactly the pairing profile of the star
column `z_(S_0)` against the seven spanning star columns.  Both `z_T` and
`z_(S_0)` lie in the nondegenerate space `E_x`, so equality of all seven
pairings forces

```text
z_T=z_(S_0).
```

This is a weight-two dual relation between distinct triangle blocks,
contradicting the verified dual-distance bound.  Thus

```text
t=3.                                               (9)
```

## 5. A conic circuit and its complementary circuit

Let

```text
A={S_i:j_i=2},  |A|=3,
B=S_x minus A,   |B|=4.
```

Pairing against every star column and using nondegeneracy gives

```text
z_T+2*sum_(S in A) z_S=0.                         (10)
```

Adding the full-star relation gives

```text
z_T+sum_(S in B) z_S=0.                           (11)
```

The eight columns `{z_T} union S_x` span `E_x`, so their relation space has
dimension two.  Normalize the coefficient of `z_T` to one.  Adding the
three scalar multiples of the star relation to (10) gives exactly:

```text
support {T} union A,       weight 4;
support {T} union B,       weight 5;
support {T} union S_x,     weight 8.
```

The first two are circuits.  For weight four this follows already from dual
distance four.  For weight five, the four columns in `B` are independent,
and the displayed representation of `z_T` uses every one of them.  The
weight-eight relation is not a circuit because it contains the full
seven-star circuit.

After scaling the three `A`-columns by two, the four columns in (10) have
Gram matrix

```text
J_4-I_4.
```

They are the four singular points of the nondegenerate conic `Q(2,3)` in
their projective plane.  Thus every circuit serving three nonedges is
exactly one member of a canonical pair:

```text
weight 4 conic support  <-->  weight 5 complement support.   (12)
```

Both members cross-realize all three pairs in (3).  By (2), those are their
entire cross-realization sets.  The pairing is an involution, and different
three-pair sets yield different companion pairs.

## 6. Minimal-cover amplification

Wave 179 supplies at least one short circuit for every nonedge.  From all
such supports, take an inclusion-minimal subfamily whose nonedge
cross-realization sets cover all 4,158 nonedges.

Let

```text
N = number of selected supports,
a = number of selected supports covering three nonedges.
```

Every other selected support covers at most two nonedges, so

```text
4158<=2(N-a)+3a=2N+a.                              (13)
```

For each of the `a` triple-serving supports, (12) supplies a distinct
companion with exactly the same three labels.  Inclusion-minimality means
the cover cannot contain both members of a companion pair: either one would
then be redundant.  Hence the total number `Q` of nonedge-realizing
projective short circuits satisfies

```text
Q>=N+a.
```

Combining this with (13),

```text
2Q>=2N+2a>=2N+a>=4158,
Q>=2079.                                           (14)
```

The 693 selected edge circuits from Wave 179 realize no nonedge, so they are
disjoint from these `Q` classes.  Therefore

```text
projective circuits of sizes 4..9 >=2079+693=2772. (15)
```

Every ternary projective circuit class contributes its two nonzero scalar
words.  If `B_i` is the dual weight distribution, (15) yields

```text
B_4+B_5+B_6+B_7+B_8+B_9>=2*2772=5544.             (16)
```

The edge-specific subbound remains simultaneous:

```text
B_4+B_6+B_8>=1386.                                (17)
```

## Boundary

The denominator-three loss in Wave 179 is now compensated by a forced
companion rather than eliminated.  Equations (16)--(17) are stronger
necessary conditions for the conditional rank-11 endpoint, not an
inconsistency.

No rank-11 exclusion, endpoint exclusion, strict `n3` improvement, graph
construction, or Conway-99 resolution follows.  External novelty is
`UNKNOWN`.
