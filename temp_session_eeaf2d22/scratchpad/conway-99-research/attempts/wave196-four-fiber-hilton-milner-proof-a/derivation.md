# Compact Wave196 derivation

At a fixed center `x`, its 14 neighbors form seven matching edges. Every
nonneighbor `y` has two common neighbors with `x`, lying in two distinct
matching edges. This defines a two-block type `P_x(y)`. Each of the 21
types has exactly four vertices, one for each endpoint pair.

For a canonical exact-three flag with `A={i,j,k}`, its three leaf vertices
have types

```text
ij, ik, jk.
```

The local `A`-family is simple and intersecting by the verified dual
distance at least four.

If the family is nontrivial, Hilton--Milner gives `c<=13`. For `c<=12`,
the leaf union is at most 36. At `c=13`, either equality template has three
block-pairs of degree five. The corresponding fibers have capacity four,
forcing at least three repeated leaf occurrences among 39, so again
`j<=36`.

If the family has a common block `{x,p,q}`, a flag is determined by its
`p`-neighbor `y`: `mu=2` determines its `q`-neighbor and `lambda=1`
determines the third leaf. There are only twelve possible `y`, so
`c<=12` and `j<=36`.

Therefore

```text
F<=99*13=1287,
J<=99*36=3564,
S36=3564-C+n1+2*n2-a3-b3>=0.
```

With the Wave194 slacks,

```text
Q0-(11*C-3564)/6

 =(2/3)*SI+(4/3)*S2+(1/6)*SE2
  +(2/3)*RA+(1/3)*SL+(1/6)*S36
  +a1/6+b3/2+c2/6+W/3.
```

At `C=4158`, the target is exactly 7,029.
