# Packing closure for the forced short-vector supports

Claim label: `DERIVED` (discovery; independent verification required).

This package is conditional on the Wave 71 signed-support reduction and the
Wave 74 outside-incidence equations. It uses no automorphism assumption.

## 1. The packing lemma

Let an outside vertex `x` meet `d` vertices of one sign side. For the
norm-16 branch, the opposite sign side has eight vertices and every selected
support vertex has four neighbors there. If `p` and `q` are both adjacent to
`x`, then `x` is already one common neighbor of `p,q`. Those two same-sign
vertices are nonadjacent, so they have only two common neighbors in the full
strongly regular graph. Their two four-subsets of the opposite side therefore
intersect in at most one point.

If `d>=3`, choose three selected vertices. Their opposite-side neighborhoods
are four-subsets `R1,R2,R3` with pairwise intersections at most one. But

```text
|R1 union R2 union R3|
  = 12 - sum_{i<j}|Ri intersection Rj|
       + |R1 intersection R2 intersection R3|
  >= 12 - 3
  = 9.
```

They cannot fit into an eight-point opposite side. Therefore

```text
norm 16: d<=2.
```

For norm 18 the opposite side has nine vertices. The same argument excludes
`d>=4`: any four selected four-subsets would have union at least
`16-C(4,2)=10`. Thus

```text
norm 18: d<=3.
```

Equality for three four-subsets on nine points is rigid. Their union is all
nine points, all three pair intersections have size one, and their triple
intersection is empty.

In the norm-18 `h=1` lane, each endpoint of the unique same-sign edge has
five, rather than four, opposite-side neighbors. If a `d=3` outside block
contained even one endpoint, its three opposite-side neighborhoods would
have total size at least `5+4+4`; every selected pair already has the outside
vertex as a common neighbor, so their internal intersections contribute at
most three. Their union would have size at least ten, impossible on the
nine-point opposite side. If both endpoints were selected, their mutual
internal intersection is zero because their unique common neighbor is
already the outside vertex, making the contradiction stronger. Thus every
surviving `d=3` block avoids both endpoints of the same-sign edge.

## 2. Exact histogram collapse

Wave 74 gives the moments

```text
norm 16:
  |X|=83, sum d_x=80, sum C(d_x,2)=8;

norm 18, h=0:
  |X|=81, sum d_x=90, sum C(d_x,2)=18;

norm 18, h=1:
  |X|=81, sum d_x=86, sum C(d_x,2)=9.
```

Adding the packing bounds and solving the three integer systems gives:

```text
norm 16:
  (n0,n1,n2)=(11,64,8);

norm 18, h=0:
  (n0,n1,n2,n3)=(9-j,54+3j,18-3j,j),  0<=j<=6;

norm 18, h=1:
  (n0,n1,n2,n3)=(4-j,68+3j,9-3j,j),   0<=j<=3.
```

Thus the Wave 74 lists shrink exactly as follows:

```text
norm 16:       4 -> 1 histogram
norm 18, h=0: 20 -> 7 histograms
norm 18, h=1:  6 -> 4 histograms.
```

The standard-library checker exhausts the relevant four-subset families and
the bounded histogram systems independently of these formulas.

## 3. Boundary

The unique norm-16 histogram is still only a necessary aggregate condition.
The seven and four norm-18 histograms also survive only as integer moment
solutions. No compatible labelled outside blocks, outside graph, lattice,
or Conway graph is constructed.

The Wave 71 congruence

```text
N14+N16+N18 = 2 (mod 14)
```

still has live norm-14, norm-16, and norm-18 alternatives. Conway-99 and
literature novelty remain `UNKNOWN`.
