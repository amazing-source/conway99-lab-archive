# Compact derivation

At a fixed center, the 14 neighbors form `7K2`.  Every pair of local
edges has four nonneighbor vertices, one for each endpoint pair.  A flag
with `A={i,j,k}` uses one leaf from each of the fibers `ij,ik,jk`.

The local `A`-family is simple and intersecting.  A nontrivial family has
at most 13 members.  At equality, both Hilton--Milner templates have
three pair-fibers of degree five, forcing three repeats in four-element
fibers and hence `j<=36`.  A common-star family injects into 12 possible
neighbors by `mu=2` followed by `lambda=1`, so it also has `j<=36`.

Including the separated selected, old, and new exact-three companion
orbits gives

```text
F<=1287,
J<=3564,
S36=3564-C+n1+2n2-a3-b3>=0.
```

The exact Wave194 combination is

```text
Q0-(11C-3564)/6
 =2SI/3+4S2/3+SE2/6+2RA/3+SL/3+S36/6
  +a1/6+b3/2+c2/6+W/3.
```

At `C=4158`, this proves `Q>=7029`.
