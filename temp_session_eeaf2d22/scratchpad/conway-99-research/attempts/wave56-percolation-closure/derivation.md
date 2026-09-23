# Wave56 derivation

All statements are conditional on a hypothetical
`G=srg(99,14,1,2)`.  This is a discovery derivation pending independent
verification.

## 1. Closure dichotomy

Let `C=<A>` be the 2-bootstrap closure of a set `A`.  Ibrahim, LaFayette,
and McCall's Lemma 4.9 says that an induced closure in a strongly regular
graph is a `K_(lambda+2)`, an irregular `(lambda,mu)`-graph, or a strongly
regular graph with the same `lambda,mu`.

For a seed consisting of a nonedge:

- the closure cannot be `K3`, because it contains the nonedge;
- the irregular alternative is impossible because Theorem 4.8 permits an
  irregular `(lambda,mu)`-graph only for `mu=0` or `mu=1`;
- hence a proper closure is an `srg(n',k',1,2)`.

The parameter equation is

```text
n' = 1 + k' + k'(k'-2)/2 = 1 + k'^2/2.
```

Thus `k'` is even and at most 14.  The two restricted eigenvalues have
discriminant

```text
Delta = 4k' - 7.
```

Exact multiplicity arithmetic for `k'=2,4,...,14` leaves only

```text
(n',k') = (3,2), (9,4), (99,14).
```

The first is the already excluded complete `K3` case, and the last is the
ambient graph.  Therefore a nonpercolating nonedge has a nine-vertex
`srg(9,4,1,2)` closure.

The nine-vertex graph is reconstructed directly below: its first eight
vertices force both opposite tip edges, and degree four forces the ninth
vertex to be adjacent to all four tips and to none of the four-cycle
vertices.  The displayed coordinate map in `exact-results.json` identifies
the graph with the `3 by 3` rook graph, equivalently `K3 square K3`.

Consequently:

```text
a nonedge percolates to all 99 vertices,
or its closure is a unique induced K3 square K3.
```

This independently recovers the target-specific closure content of Theorem
4.19 from the cited general lemma.

## 2. The two channels of an arbitrary nonedge

Let the seed be the nonedge `{c0,c2}`.  Its two common neighbors are `c1,c3`.
They are nonadjacent: if they were adjacent, that edge would have the two
common neighbors `c0,c2`, contradicting `lambda=1`.  The first infected set
therefore induces the four-cycle

```text
c0-c1-c2-c3-c0.
```

Each cycle edge has a unique triangle mate:

```text
t01, t12, t23, t30.
```

The four tips are distinct and each sees exactly its named cycle edge.
Otherwise an adjacent pair would acquire too many common neighbors or one
of the two cycle diagonals would acquire a third.

Tips on adjacent cycle edges cannot be adjacent.  For example, if
`t01-t12` were an edge, then the adjacent pair `c1,t01` would have both
`c0` and `t12` as common neighbors, contradicting `lambda=1`.  Only the two
opposite pairs may be edges:

```text
t01-t23,  t12-t30.
```

Each opposite pair gives one exact channel:

- if the tips are nonadjacent, the corresponding six vertices induce an
  `N3`, two triangles joined by exactly two matching cross-edges;
- if the tips are adjacent, they induce a triangular prism.

Hence the four locally admissible labeled tip graphs have zero, either one,
or both opposite edges.  Their `(N3 channels, prism channels)` are

```text
(2,0), (1,1), (1,1), (0,2).
```

No automorphism of a completed graph is used: all 64 labeled graphs on the
tips are tested.

## 3. Global incidence relations

Let

```text
n3 = number of induced N3 copies,
P  = number of induced triangular prisms,
H  = number of induced K3 square K3 closures,
R  = number of nonpercolating nonedges,
S  = number of percolating nonedges.
```

There are

```text
C(99,2) - 99*14/2 = 4158
```

nonedges.  Every nonedge has two channels.  Every `N3` has exactly two
central nonedge channels, while every triangular prism has six.  Double
counting gives

```text
2*4158 = 2*n3 + 6*P,
n3 + 3*P = 4158.
```

The `3 by 3` rook graph has exactly:

```text
18 nonedges,
6 induced triangular prisms,
0 induced N3 copies.
```

Every nonpercolating nonedge lies in its unique closure, and every nonedge of
an induced `K3 square K3` closes to that same graph.  Therefore

```text
R = 18*H,
S = 4158 - R.
```

In particular `H<=4158/18=231`.  If `H=231`, no nonedge percolates, and an
adjacent pair can close only its unique triangle.  On the other hand, add any
vertex outside a nine-vertex closure to one of its nonedge seeds.  The new
closure strictly contains the rook graph, and the closure census permits no
intermediate order, so the three-set percolates.  Thus

```text
2 <= m(G,2) <= 3,
m(G,2)=3 iff H=231,
m(G,2)=2 iff H<231.
```

Also `H=0` exactly when every nonedge percolates.  This recovers all three
parts of Theorem 4.19.

A fixed prism lies in at most one such closure: two closures containing the
prism would share any of its nonedges, contradicting uniqueness of closure.
Thus

```text
H <= 231,
6*H <= P,
R <= 3*P = 4158-n3,
S >= n3.
```

Equality is not automatic.  The following are equivalent:

```text
R = 3*P,
S = n3,
every induced prism lies in an induced K3 square K3 closure.
```

An `N3` cannot lie in `K3 square K3`: every triangle in the rook graph is a
row or column, and two disjoint triangles of the same direction have all
three matching cross-edges, not two.  Hence both central nonedges of every
`N3` percolate.

At the prism-free endpoint:

```text
n3=4158, P=H=R=0, S=4158.
```

Thus every nonedge percolates at the endpoint.  This is stronger than merely
exhibiting one two-vertex percolating set.

## 4. Exact next-wave CSP

At the endpoint the four tips are independent, since either possible tip
edge is already a triangular-prism channel.  For the forced eight-vertex
graph, the 28 pair deficits split as

```text
14 deficits zero,
12 deficits one,
2 deficits two,
total deficit 16.
```

For an outside vertex, retain its exact neighborhood mask on the eight
vertices when the mask has size at least two.  A mask is allowed only when:

1. it covers no zero-deficit pair;
2. for a current neighbor, the mask supplies at most one already visible
   common neighbor;
3. for a current nonneighbor, it supplies at most two;
4. it creates no induced prism with five current vertices.

Exactly 23 labeled masks survive:

```text
14 of size 2, 8 of size 3, 1 of size 4.
```

The exact nonnegative multicover of all 28 pair deficits has 35 labeled
solutions.  If `xr` counts next-wave vertices seeing exactly `r` of the
eight current vertices, the complete triple census is

| `(x2,x3,x4)` | labeled profiles | next-wave size |
| --- | ---: | ---: |
| `(16,0,0)` | 1 | 16 |
| `(13,1,0)` | 8 | 14 |
| `(10,2,0)` | 16 | 12 |
| `(7,3,0)` | 8 | 10 |
| `(4,4,0)` | 1 | 8 |
| `(10,0,1)` | 1 | 11 |

Every row satisfies the smaller exact equation

```text
x2 + 3*x3 + 6*x4 = 16.
```

After the third synchronous wave, between 16 and 24 vertices in total are
infected.  Grouping the 35 retained labeled profiles by the formal dihedral
relabelings of the rooted four-cycle gives 11 bookkeeping orbits.  This
grouping is not an assumption that the completed graph has an automorphism.

Across all endpoint nonedges, the CSP yields only

```text
sum x2 + 3 sum x3 + 6 sum x4 = 4158*16 = 66528.
```

The triple- and quadruple-mask totals are higher-order unknowns.  No global
contradiction follows from the pair-deficit equation alone.
