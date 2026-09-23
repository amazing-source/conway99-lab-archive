# Independent Wave196 four-fiber audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Conditionally on the frozen prism-free rank-11 endpoint,

```text
j_x<=36 for every graph vertex x,
J<=3564,
Q>=7029.
```

Here `j_x` is the number of distinct fixed-center exact-three leaf labels,
`J=sum_x j_x`, and `Q` counts projective short circuits cross-realizing a
graph nonedge.

The independent result was frozen before either Wave196 source was opened:

```text
independent math SHA-256:
106444612745ed8e8b384460cc696c5d580a2201aa53f257e2a9d616ea5ce969
```

The sealed primary manifest is
`83bd93ab0980305d59052dd25dc373f582b5a6fc998b122d64d506871e244b1c`.
The hostile proof-B manifest is
`1eb6c6abdc6855af950459ac524653108f5582d9686fbe4e6a0df89e9c39c14a`.
Proof B was opened only after the independent freeze and primary
comparison, and was not used as a mathematical premise.

## 1. Four vertices in every two-block type

Fix `x`.  The graph on `N(x)` is 1-regular: each of its 14 vertices has
exactly `lambda=1` neighbor inside `N(x)`.  Thus the seven local graph
triangles through `x` are

```text
S_i={x,p_i,q_i}, i=1,...,7.
```

If `y` is a nonneighbor of `x`, its `mu=2` common neighbors with `x`
cannot be the two endpoints of one local matching edge.  Otherwise that
edge would have both `x` and `y` as common neighbors, contradicting
`lambda=1`.  Define `P_x(y)={i,j}` from the two distinct local blocks.

Conversely, choose one endpoint from each of blocks `i,j`.  The chosen
vertices are nonadjacent because `N(x)` is a matching.  Their nonedge has
exactly two common neighbors: `x` and one other vertex `y`.  That `y`
cannot lie in `N(x)`, since it would have two neighbors in the matching.
Different endpoint pairs give different `y`, because a nonneighbor of `x`
has only two common neighbors with `x`.

Hence each of the 21 block-pair types contains exactly four vertices:

```text
21*4=84,
```

which partitions all nonneighbors of `x`.

## 2. One flag uses types `ij,ik,jk`

An exact-three flag is `(x,T)`, with `T` a graph triangle anticomplete to
`x`, and with

```text
A_x(T)={i: j(T,S_i)=2}, |A_x(T)|=3.
```

Every leaf of `T` has two neighbors in `N(x)`, while each of the three
`A`-blocks has two incidences with `T`.  A local-block endpoint cannot
meet two leaves, because their triangle edge would then have two common
neighbors.  The two endpoints of one local block cannot meet the same
leaf, because their matching edge would then have common neighbors `x`
and that leaf.

The leaf-to-`A` incidence graph is therefore a simple 2-regular bipartite
graph on `3+3` vertices.  It is a 6-cycle.  If
`A_x(T)={i,j,k}`, the three leaves consequently have types

```text
ij, ik, jk,
```

one each.

The sealed Wave180/Wave194/Wave195 results make the fixed-center
`A`-family simple and pairwise intersecting.  Selected, old-`h`, and
new-`g` exact-three companion pairs form one disjoint flag pool, so this
local theorem applies to their union.

## 3. Nontrivial Hilton--Milner branch

If the fixed-center intersecting family has empty total intersection,
Hilton--Milner gives `c_x<=13`.  For `c_x<=12`,
`j_x<=3c_x<=36`.

At equality `c_x=13`, the `k=3` equality classification has exactly two
isomorphism types:

```text
H={B} union {A: a in A and A intersects B}, a notin B;
K={A: |A intersect B|>=2}, |B|=3.
```

The equality statement and both templates were checked in Theorem 11 of
Hurlbert and Kamat's primary paper:
<https://arxiv.org/abs/1609.04714>.

The verifier independently instantiated both formulas.  They are
pairwise intersecting, have empty core and size 13, and are nonisomorphic
because their element-degree sequences are

```text
H: 12,6,6,6,3,3,3
K:  9,9,9,3,3,3,3.
```

In `H`, the three pairs `{a,b}`, `b in B`, each occur in five members.
In `K`, the three pairs within `B` each occur in five members.  A pair of
blocks has only four possible leaf vertices, so each of these three
distinct fibers forces one repeated leaf.  The losses are additive
because a leaf has a unique type.  Thus

```text
j_x<=3*13-3=36.
```

The checker evaluates these two fixed formulas only.  It does not search
the `2^35` possible subfamilies of the 35 triples.

## 4. Common-block branch

Suppose every `A_x(T)` contains `S={x,p,q}`.  Each flag has one
`p`-neighbor leaf `a`, a distinct `q`-neighbor leaf `b`, and a third
leaf `c`.

The vertices `q,a` are nonadjacent.  Their common neighbors are `p` and
`b`, so `mu=2` makes `b` the unique common neighbor other than `p`.
Then `a,b` are adjacent, and `lambda=1` makes `c` their unique common
neighbor.  Consequently `a` determines the whole flag.

There are at most

```text
deg(p)-2=12
```

choices for `a`, after excluding the known neighbors `x,q`.  Hence
`c_x<=12` and `j_x<=3c_x<=36`.

## 5. Global oriented-label row

Summing over 99 centers gives

```text
J<=99*36=3564=6C/7.
```

The Wave195 lower-bound orientations are unchanged.  For the undirected
selected type-three label union `U`,

```text
|U|>=C-n1-2n2.
```

Every label in `U` gives at least one orientation.  The `a3` assignments
give one additional oriented private label each, while the two `b3`
endpoint translates of one type-two private nonedge have opposite
centers.  The verified pool separation makes these injections disjoint.
Thus

```text
J>=C-n1-2n2+a3+b3,
S36=n1+2n2-a3-b3-C/7>=0.
```

No unproved factor-two type-one orientation and no unrelated candidate
capacity row is used.

## 6. Exact certificate and arithmetic boundary

Retain the verified Wave194 slacks

```text
SI =I-2C,
S2 =p2-n2,
SE2=2r2-a2-c2,
RA =3h+y+3g-a2-a3-2b3-c2,
SL =n1+2n2+c1+2r2+y+2W-C.
```

Exact coefficient expansion gives

```text
Q0-71C/42
 =2SI/3+4S2/3+SE2/6+2RA/3+SL/3+S36/6
  +a1/6+b3/2+c2/6+W/3.
```

Every term on the right is nonnegative.  At `C=4158`,

```text
71C/42=(11C-3564)/6=7029.
```

Therefore `Q>=7029`.  Adding 693 edge-isolated projective circuits gives
7,722 projective short circuits, hence 15,444 nonzero scalar circuit
words.  Wave188's 18,018 all-short-word lower bound remains numerically
stronger because it also counts nonminimal words.

The independent arithmetic null is integral:

```text
a2=n1=594,
c1=p3=r1=2970,
n3=1386,
r2=297,
h=198,
all other split and new-pool variables zero.
```

It zeros `SI,S2,SE2,RA,SL,S36` and has `Q0=7029`.  The primary source has
a different integral null, which the verifier independently replayed.
Neither row constructs a graph, code, cover, flag family, or circuit
system.

## Reproducibility and boundary

```text
independent math replay:       PASS
independent full replay:       PASS
independent tests:             13/13 PASS
primary source replay:         PASS
primary source tests:          8/8 PASS
proof-B hostile replay:        PASS
proof-B hostile tests:         6/6 PASS
all sealed hashes:             PASS
```

No graph, code, cover, SAT, LP, configuration, family, construction,
enumeration, isomorphism, or brute-force search was used.  Rank 11,
endpoint existence, strict original `n3` improvement, external novelty,
and Conway-99 remain `UNKNOWN`.
