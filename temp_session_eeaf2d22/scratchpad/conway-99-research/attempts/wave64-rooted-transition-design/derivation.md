# Rooted transition/design derivation

## Scope and status

Everything below is conditional on a prism-free strongly regular graph
`srg(99,14,1,2)` at the endpoint under study.  The construction is rooted but
uses no automorphism of a target graph.  The finite equalities are `DERIVED`;
discovery does not promote them to `VERIFIED`.  Neither this formulation nor
the searches in this package resolve the endpoint.

## 1. The 84 residual vertices are the edges of `K14 - 7K2`

Fix a vertex `o`.  Its 14 neighbors induce a 1-regular graph because adjacent
vertices have exactly `lambda=1` common neighbor.  Write those seven edges as
mate pairs and call the 14 vertices the base points.

A residual vertex `p` is nonadjacent to `o`, so it has exactly `mu=2` common
neighbors with `o`.  These are two base points.  They cannot be mates: if they
were adjacent, their edge would have both `o` and `p` as common neighbors,
contradicting `lambda=1`.

Conversely, two nonmate base points are nonadjacent and have exactly two common
neighbors.  One is `o`, so the other is a unique residual vertex.  Thus the 84
residual vertices are in bijection with the edges of

```text
H = K14 - 7K2 = K_{2,2,2,2,2,2,2}.
```

There are `C(14,2)-7=84` such labels.  A residual vertex has 2 neighbors among
the base points and therefore residual degree 12.

## 2. Intersecting labels form a transition system

Suppose two adjacent residual labels share a base point `s`.  Then `s` is
already their unique common neighbor, so the residual pair has no residual
common neighbor.

For a label `p` and each of its two base endpoints `s`, the adjacent pair
`(p,s)` has one common neighbor.  It is a residual label also incident with
`s`.  Hence the twelve `H`-edges incident with each base point are paired:
there is one perfect matching at each base point.  Across all 14 base points
this selects

```text
14 * 6 = 84
```

intersecting-label residual edges, and every residual label has two of them.

At a fixed base point, the other endpoints of the twelve incident `H`-edges
come in six mate pairs.  Pairing the two edges whose other endpoints are mates
would create the triangular prism with triangles `(o,a,mate(a))` and
`(s,p,q)`.  Those six transitions are therefore forbidden.  Inclusion-
exclusion gives the number of allowed perfect matchings:

```text
11!! - C(6,1)9!! + C(6,2)7!! - C(6,3)5!!
     + C(6,4)3!! - C(6,5)1!! + C(6,6)(-1)!!
= 10395 - 5670 + 1575 - 300 + 45 - 6 + 1
= 6040.
```

There are `60` allowed transition variables at each base point and `840` in
total.

## 3. Disjoint-label edges are 140 three-edge matching blocks

The other ten residual neighbors of each label must have disjoint `H`-edge
labels.  There are therefore

```text
84 * 10 / 2 = 420
```

selected disjoint-label edges.

If two disjoint labels `p,q` are adjacent, their unique common neighbor cannot
be `o` or a base point, so it is a residual vertex `r`.  If `r` shared a base
point with either `p` or `q`, that root neighbor and the third triangle vertex
would be two common neighbors of an adjacent pair.  Therefore the three
labels in the residual triangle are pairwise vertex-disjoint edges of `H`.

Every selected disjoint-label edge is in its unique residual triangle.  The
420 edges consequently partition into 140 blocks, each a 3-edge matching of
`H`.  Every one of the 84 labels occurs in five blocks.

The candidate count follows by excluding the seven forbidden mate edges from
all 3-matchings of `K14`:

```text
sum_{k=0}^3 (-1)^k C(7,k) C(14-2k,6-2k) (5-2k)!!
= 45045 - 10395 + 945 - 35
= 35560.
```

For each pair within a block, count whether the two disjoint base edges use
two, three, or four support groups.  The exact block census is:

| counts for support-union `(2,3,4)` | candidates |
|---|---:|
| `(0,0,3)` | 6,720 |
| `(0,1,2)` | 20,160 |
| `(0,2,1)` | 6,720 |
| `(0,3,0)` | 280 |
| `(1,0,2)` | 1,680 |

## 4. Mate-pair occupancy is `(32,96,12)`

Fix one root mate pair, viewed as one support group.  Let `n_i` be the number
of the 140 blocks that use `i` of its two base points.  A block cannot use
more than two.

There are 24 `H`-edge labels incident with the group and every label lies in
five blocks, so

```text
n0+n1+n2 = 140,
n1+2n2 = 24*5 = 120.                         (1)
```

The rooted endpoint profile for a label `p` and base point `s` is

```text
sum_{q: s is in label(q)} x_pq
  = 2 - [s is in label(p)] - [mate(s) is in label(p)].   (2)
```

Let `a` be the endpoint of `p` in the fixed support group and put
`s=mate(a)`.  The right side of (2) is 1.  No transition neighbor can
contribute: a transition through the other endpoint of `p` whose other
endpoint is `mate(a)` is precisely one of the prism-forbidden transitions.
Thus exactly one block-neighbor of `p` uses `mate(a)`.

Sum this equality over the 24 labels incident with the support group.  Every
block using both base points is counted from each of its two incident labels,
so `2n2=24`.  Hence `n2=12`; substituting in (1) gives

```text
(n0,n1,n2) = (32,96,12)
```

for each of the seven root mate pairs.  This is the support-local form of the
Wave-3 dichotomy

```text
2*x(full-opposite) + sum x(one-support-opposite) = 2.
```

## 5. The two integer masters

The block-only master has one binary variable for each of the 35,560 blocks.
It imposes:

1. every label has block degree 5;
2. every disjoint label pair occurs in at most one selected block;
3. every support group is doubled in exactly 12 selected blocks; and
4. the Wave-3 local dichotomy at every label.

This is a relaxation, not an exact graph reformulation.  The package contains
an explicitly checked 140-block witness with disjoint-pair relation counts

```text
(support-union 2, support-union 3, support-union 4) = (5,74,341).
```

The stronger linear master adds the 840 transition variables, the 168 local
perfect-matching equations, all 1,176 endpoint-profile equations (2), and the
280 transition-triangle cuts.  A transition triangle would give each of its
three edges a residual common neighbor as well as its shared base-point common
neighbor, so it is forbidden.  The count is `C(7,3)*2^3=280`.

The stronger master is still a relaxation because it does not impose every
residual pair codegree.

## 6. Exact fractional positive control

The stronger linear master has the following exact rational feasible point:

```text
z_b = 1/120  for block type (0,0,3),
z_b = 1/240  for block type (0,1,2),
z_b = 0      for the other three block types,
t_e = 1/10   for every allowed transition.
```

Direct rational enumeration checks every declared linear row.  Pair loads are
`0,1/10,1/5`; every label has block degree 5; every support occupancy is 12;
every local dichotomy is 2; every transition degree is 1; and every endpoint
profile has zero residual.  A transition-triangle left side is `3/10`.

This is not a graph and is not an integral design.  It proves only that the
declared linear master is rationally feasible, so a Farkas separation at this
linear level is impossible.  The scaffold-invariant assignment is used as a
positive control and does not assume a target graph has that symmetry.

## 7. Exact completion and lazy residual-codegree cuts

Given integral transition/block variables, define `x_pq` as follows:

- `x_pq` is the selected transition variable for an allowed intersecting pair;
- it is zero for a forbidden intersecting pair;
- for a disjoint pair, it is the sum of selected blocks containing that pair
  (binary because of pair simplicity).

Let

```text
Q_pq = |label(p) intersect label(q)|.
```

The missing exact residual condition is, for every distinct residual pair,

```text
sum_{r != p,q} x_pr*x_qr = 2 - Q_pq - x_pq.        (3)
```

Together with the rooted scaffold and endpoint profiles, (3) supplies all
remaining `lambda=1, mu=2` equations.  A proof-producing complete encoding can
introduce binary products `w_pqr=x_pr*x_qr`, impose

```text
w_pqr <= x_pr,
w_pqr <= x_qr,
w_pqr >= x_pr+x_qr-1,
sum_r w_pqr + x_pq = 2-Q_pq,
```

and check all of them.

For a lazy implementation, first attack selected transition edges: for each
detected residual common neighbor `r`, add

```text
x_pq + x_pr + x_qr <= 2.
```

For a selected disjoint edge, its selected block already supplies its one
allowed common neighbor; apply the same cut to every additional detected
common neighbor.  Nonadjacent intersecting pairs must eventually receive
exactly one residual common neighbor, and nonadjacent disjoint pairs exactly
two.  Those lower as well as upper codegree obligations must be closed before
the formulation is equivalent to a full residual graph.  A solver nonhit
before this closure has no nonexistence meaning.

