# Wave 6 opposite-edge graph and the `N3` count

```yaml
role: proof_b
date_utc: 2026-07-22T23:51:21Z
git_commit: a066170e452f31efe1e00610b8159a66b825b01f
claim_label: DERIVED
scope: auxiliary edge-graph consequences, global n3 lower bound, and local data for the normalized N3 branches
inputs:
  STRUCTURE.md: 5abb670df42aac367471951b6523587f3d3b0662656f093b76fb3886afdb440b
  agents/2026-07-22-wave3-prior-art.md: b0678e58b7efe04af502d3539cecd01b33c1f77885d917ad45d5cfa9999cf890
  verification/n3-joint-cover/n3-joint-cover.json: 58c4994ff0eef9c5e1702840f791d1400c3da71b445e3c217e3704c5e70de172
method: exact local SRG arguments, an auxiliary graph on the 693 graph edges, extremal triangle-free counting, and exhaustive matching checks
command: |
  .venv/Scripts/python verification/n3-count-bound/verify.py
outputs:
  global_n3_lower_bound: 24
  global_induced_C6_lower_bound: 209310
  branch_n3_lower_bounds: [24, 33, 42, 48, 48, 24, 42, 48, 33, 48, 42, 48]
limitations: conditional on target existence and the cited-and-derived universal N3 occurrence; no branch is solved and no completed-graph automorphism is assumed
```

## The opposite-edge graph

Let `G` be a putative `srg(99,14,1,2)`. Define `J` on the 693 edges of `G`:
two graph edges are adjacent in `J` when they are opposite edges of a
four-cycle in `G`.

Every four-cycle is induced. A diagonal would have the two intermediate
vertices as common neighbors, contradicting `lambda=1`.

Fix graph edge `e=xy`, and let `z` be the unique common neighbor of `x,y`.
For each of the twelve vertices

```text
u in N(x) - {y,z},
```

the nonedge `u,y` has common neighbor `x` and one unique other common neighbor
`v`. The edge `xv` is absent, or `x,y` would have a second common neighbor.
Hence `x-u-v-y-x` is an induced four-cycle whose opposite edge is `uv`.
This construction is bijective, so

```text
J is 12-regular,
|E(J)| = 693 * 12 / 2 = 4,158.
```

A pair of opposite graph edges determines its four-cycle uniquely: both
endpoint matchings would make the four endpoints a `K4`.

## `J` triangles and triangular prisms

Three vertices forming a triangle in `J` are three pairwise-disjoint graph
edges. Between every pair, the unique four-cycle supplies two side edges.
After independently switching endpoints of the three graph edges, the two
possible six-vertex unions are a triangular prism and `K3,3`. The latter is
impossible because two vertices in one part would have all three opposite-part
vertices as common neighbors, contradicting `mu=2`. Thus every `J` triangle
is exactly an induced triangular prism, with the three `J` vertices as its
vertical graph edges.

Every `J` edge belongs to at most one `J` triangle. To see this, orient its
unique four-cycle as

```text
x-u-v-y-x,
```

with opposite graph edges `xy` and `uv`. Let `p` and `q` be the unique third
vertices of the graph triangles on side edges `xu` and `yv`. Any prism
completion must use the uniquely determined third vertical edge `pq`.

The vertices `p,q` are distinct: equality would give the nonedge `xv` the
three common neighbors `u,y,p`. The two graph triangles `{x,u,p}` and
`{y,v,q}` are disjoint. Their known cross-edges are `xy` and `uv`. The two
four-cycle diagonals `xv,uy` are absent by `lambda=1`. Each of the other four
possible cross-edges would be a third common neighbor of one of those
diagonals, so is absent by `mu=2`. Only `pq` remains undecided.

- If `pq` is present, the six vertices induce the unique triangular prism
  completing this `J` edge.
- If `pq` is absent, they induce `N3`: two triangles joined by exactly two
  independent cross-edges.

Consequently, if `H` is the spanning subgraph of `J` consisting of the `J`
edges in no `J` triangle, then

```text
E(H) <-> induced N3 copies,
|E(H)| = n3.
```

This is a genuine bijection, with no factor of two. The graph `H` is
triangle-free, since an `H` triangle would be a `J` triangle. If `P` is the
number of induced triangular prisms, the `J` edges partition as

```text
4,158 = 3 P + n3.
```

This independently recovers `n3 = 0 (mod 3)`.

## Local degrees in `H`

For `e=xy`, the twelve vertices `N(x)-{y,z}` carry a perfect matching `M_x`
from the six other triangles through `x`. Mapping each `u` to the second
common neighbor of nonedge `u,y` is a bijection onto `N(y)-{x,z}`. Pulling
back the six triangle pairs through `y` gives a second perfect matching `M_y`
on the same twelve points.

A common edge of `M_x,M_y` gives a triangular prism through `e`. Every
noncommon endpoint gives one incident `H` edge. If

```text
t_e = |M_x intersect M_y|,
```

then

```text
d_H(e) = 12 - 2 t_e.
```

Two perfect matchings cannot share exactly five edges, because the final two
vertices would then also be paired in both. Therefore

```text
t_e in {0,1,2,3,4,6},
d_H(e) in {12,10,8,6,4,0}.
```

Every nonisolated vertex of `H` has degree at least four.

## Global lower bound

The target-specific cited-and-derived theorem that every putative Conway
graph contains an `N3` is essential here: it makes `H` nonempty. This does not
follow from `lambda=1,mu=2` alone; for example, the 3-by-3 rook graph has an
empty corresponding `H`.

Let `m=|E(H)|`. For any nonisolated vertex of degree `d`, its neighborhood is
independent. Every neighbor has degree at least four, so the edges incident to
that neighborhood number at least `4d`. Hence `m >= 4d`, in particular
`m >= 16`. Divisibility leaves only `m=18` or `21` below 24.

For `m=18`, minimum degree four and Mantel's bound force exactly nine
nonisolated vertices, all of degree four. Fix a vertex `v`, put `A=N(v)`, and
let `B` be the other four vertices. Then `A` is independent,
`e(A,B)=12`, and `e(B)=2`. If `rs` is an edge of `B`, triangle-freeness makes
the `A`-neighborhoods of `r,s` disjoint, forcing
`d_B(r)+d_B(s) >= 4`. No two-edge graph on four vertices has that property.

For `m=21`, the same bounds force ten nonisolated vertices with degree sequence
`(6,4,4,4,4,4,4,4,4,4)`. At the degree-six vertex, its six independent
neighbors must each meet all three remaining vertices to reach degree four;
those three then have degree at least six, a contradiction.

Therefore

```text
n3 >= 24,
induced_C6_count = 209,286 + n3 >= 209,310.
```

## The twelve normalized branches

For the normalized graph edge `e=x-a`, the mate edges in the certified
shared-fiber matching are exactly the common matching edges counted by `t_e`.
Since `N_H(e)` is independent and all its vertices have degree at least four,

```text
n3 >= max(24, next_multiple_of_3(4 d_H(e))).
```

The union of the two local matchings, after common edges are removed, is a
disjoint union of even alternating cycles. Its cycle-size signature is useful
metadata but is not a complete invariant: different branches may share one.

| branch | `t_e` | `d_H(e)` | coarse signature | `n3 >=` | induced `C6 >=` |
|---:|---:|---:|---|---:|---:|
| 1 | 4 | 4 | `4` | 24 | 209310 |
| 2 | 2 | 8 | `4+4` | 33 | 209319 |
| 3 | 1 | 10 | `4+6` | 42 | 209328 |
| 4 | 0 | 12 | `4+4+4` | 48 | 209334 |
| 5 | 0 | 12 | `4+8` | 48 | 209334 |
| 6 | 3 | 6 | `6` | 24 | 209310 |
| 7 | 1 | 10 | `4+6` | 42 | 209328 |
| 8 | 0 | 12 | `6+6` | 48 | 209334 |
| 9 | 2 | 8 | `8` | 33 | 209319 |
| 10 | 0 | 12 | `4+8` | 48 | 209334 |
| 11 | 1 | 10 | `10` | 42 | 209328 |
| 12 | 0 | 12 | `12` | 48 | 209334 |

## Exact boundary profile of the normalized `N3`

Name the two triangles `{x,u,v}` and `{a,b,c}`, with cross-edges `x-a,u-b`.
An outside vertex can have two neighbors in this six-set only in the following
pairs, with exact multiplicity:

```text
xa:1, ub:1, xc:1, uc:1, va:1, vb:1, vc:2.
```

Every other pair has already reached its required one or two common neighbors
inside the `N3`. The seven allowed pairs form a triangle-free graph, so no
outside vertex can have three or more neighbors in the six-set. There are
therefore exactly eight pair-profile vertices. The exact singleton counts are

```text
(x,u,v,a,b,c) = (9,9,8,9,9,8),
```

and exactly 33 outside vertices see none of the six.

For two-neighbor percolation from central diagonal `{x,b}`, synchronous wave 1
adds exactly `u,a`, and wave 2 adds exactly `v,c` and the unique pair-profile
vertices for `xa,ub`. Once all six `N3` vertices are infected, the other six
pair-profile vertices are eligible, but additional outside vertices may also
qualify through the already infected pair-profile vertices. No exact claim is
made for wave 3.

## Mate-edge propagation

If a rooted fiber matching contains

```text
p={g,a} ~ q={g,mate(a)},
```

then nonedge `p,mate(a)` already has common neighbors `a,q`. The `mu=2` axiom
forces `p` nonadjacent to the other eleven vertices of the mate fiber. The
symmetric statement for `q` contributes eleven more. For `t` mate edges these
are `22t` distinct specified residual nonedges, with

```text
22t = 11(12-d_H(e)).
```

This explains the Wave 6 propagation blocks. It is already a consequence of
the established block equation, so it is not counted as a new independent
global restriction.
