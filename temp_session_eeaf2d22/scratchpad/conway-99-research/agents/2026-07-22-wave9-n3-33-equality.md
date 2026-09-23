# Wave 9 exclusion of the `n3=33` equality case

```yaml
role: proof_a
date_utc: 2026-07-23T02:00:29Z
git_commit: 3d47bb260a71c5c2606347d8bb53e3ad766236e8
claim_label: DERIVED
scope: conditional exclusion of n3=33 for a putative srg(99,14,1,2)
inputs:
  STRUCTURE.md: 0d4cf2bb4ff77bdce5f0f1f78657e91dddcdff124ac80a958a0cae58e9281619
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  agents/2026-07-22-wave7-triangle-side-incidence.md: 7b4693420eae7e6f13ce0d66c786424c18863a1b1c350da83097f8e982ebe324
  agents/2026-07-22-wave8-n3-equality.md: 010fe1e2a9752ac18067b44c9e6cf1114e2d1651364c49a574adbe22fe5461f3
  agents/2026-07-22-wave9-status-search.md: add0d9d2afc335b7de9f9f6d5ffab72d66af97a568141cc8e885725984dc6b05
  verification/n3-33-equality/verify.py: fdac28fb0daf7a9af09dd490d878a3c848b187d64a8716e0bdabe2ce36d2aea8
  verification/test_n3_33_equality.py: 8e2adceda27399d948844820f48718c3588ada9e16987af13a5bda411e5a113f
method: active-q enumeration, labeled crossing-graph incidence, point-clique edge accounting, local K5 closure, and a complement matching obstruction
command: |
  python verification/n3-33-equality/verify.py
  python -m unittest verification.test_n3_33_equality -v
outputs:
  conditional_global_n3_lower_bound: 36
  conditional_induced_C6_lower_bound: 209322
  branch_n3_lower_bounds: [36, 36, 42, 48, 48, 36, 42, 48, 36, 48, 42, 48]
limitations: conditional on the committed Wave 6-8 lemmas and target-specific N3 occurrence; no construction or nonexistence proof for Conway-99 is produced
```

## Equality setup

Assume that a putative `srg(99,14,1,2)` has exactly `n3=33` induced copies
of `N3`. Retain the Wave 6 graph `H` on graph-edges, the Wave 7 graph `L` on
graph-triangles, and the active-triangle quantities `q(T)`. The established
identities are

```text
q(T)=0 or q(T)>=2,
d_L(T)=3q(T),
sum_T q(T)=2n3/3=22.
```

If there are `r` active triangles, then `r<=11` and every active triangle
satisfies `3q(T)<=r-1`. Exact integer enumeration leaves only

```text
r=10: q=(2,2,2,2,2,2,2,2,3,3),
r=11: q=(2,2,2,2,2,2,2,2,2,2,2).
```

Write `K` for the complement of the active part of `L`. No connectedness or
automorphism assumption is imposed on `K` or on the putative Conway graph.

## A labeled crossing-graph lemma

For an original graph vertex `u`, let

```text
S_u = {active graph-triangles containing u}.
```

Every `S_u` is a clique in `K`. The Wave 7 support identity and the Wave 8
fixed-point identity say, for every actual graph edge `uv`,

```text
d_H(uv) = e_L(S_u,S_v),
sum_{v: uv in E(G)} d_H(uv) = 2 sum_{T in S_u} q(T),       (1)
```

and the Wave 6 local calculation gives

```text
d_H(uv) in {0,4,6,8,10,12}.                              (2)
```

There is a useful additional consequence of the fixed-side graph `H_T`.
For an actual graph edge `uv`, form a bipartite graph with a labeled left
copy of `S_u`, a labeled right copy of `S_v`, and the crossing `L`-edges.
This labeling matters when the point sets overlap. Two graph-triangles can
share both `u` and `v` only when they are the unique graph-triangle on edge
`uv`, so `S_u` and `S_v` overlap in at most that one triangle. Both labeled
copies of an overlap triangle are isolated: every triangle in either point
set intersects it.

For a non-overlap triangle `T` on the left, its crossing degree is exactly
the degree of graph-edge `uv` in `H_T`, hence is zero or two. The same holds
on the right. Every crossing has a unique orientation because its endpoint
triangles are disjoint, so the number of crossing edges is still exactly
`e_L(S_u,S_v)` and no edge is doubled.

If `S_u` is a singleton, its crossing degree for every graph neighbor `v` is
therefore zero or two. Equation (2) excludes two, so every term on the left
of (1) is zero. The right side is positive for an active singleton. Thus

```text
no active point set S_u is a singleton.                         (3)
```

Equivalently, using the degree-zero-or-two property on both labeled sides,
the nonisolated crossing components would be even cycles, and no such simple
bipartite component can have only one left vertex.

## Excluding the mixed `r=10` profile

In the profile `(2^8,3^2)`, each `q=3` triangle has `L`-degree nine and is
therefore universal among the ten active triangles. It is isolated in `K`.
Every original point on either such triangle has a `K`-clique containing that
isolate, so its active point set is a singleton. This contradicts (3).

There is also a direct numerical check. Removing the two isolated vertices
leaves a cubic `K` on eight vertices, so every point clique has size at most
four. For a singleton on a `q=3` triangle, every incident crossing has size
at most four. Equations (1) and (2) make all positive terms equal four, while
their required sum is `2q=6`, impossible.

## Point resources in the all-`q=2` profile

It remains to treat `r=11`. Here `L` is 6-regular and `K` is a simple
4-regular graph on eleven vertices. At each active graph-triangle, its three
original points give three point cliques containing the corresponding
`K`-vertex. Distinct point cliques consume disjoint `K`-edges: otherwise two
graph-triangles would share two original points, putting their graph edge in
two graph-triangles.

By (3), each of the three cliques has size at least two. Their consumed
degrees at a fixed `K`-vertex are therefore positive and have sum at most
four. Consequently every active point set has size two or three, and at most
one size-three point set contains a given active triangle.

Let `x2,x3` count the point sets of those sizes. Counting the 33 point
incidences and at most 22 consumed `K`-edges gives

```text
2x2 + 3x3 = 33,
x2 + 3x3 <= 22.
```

The only nonnegative integer solutions are

```text
(x2,x3)=(12,3) or (15,1).                                (4)
```

The size-three point sets are vertex-disjoint because no active triangle can
belong to two of them.

## A size-three point forces a `K5` component

Let a size-three point set be `C={i,j,k}`. The other two original points on
active graph-triangle `i` have size-two active sets

```text
A={i,a}, B={i,b}.
```

Their four consumed edges exhaust the degree at `i`, so
`N_K(i)={j,k,a,b}`. Each pair among the three original points on graph-
triangle `i` is an actual graph edge. Its support crossing is, respectively,

```text
e_L(C,A)<=2, e_L(C,B)<=2, e_L(A,B)<=1.
```

No positive value is allowed by (2), so all three crossings vanish. Hence

```text
ja,ka,jb,kb,ab are K-edges.
```

Together with the point-clique edge `jk`, the neighborhood of `i` is a
`K4`. Since `K` is 4-regular, the five vertices `{i,j,k,a,b}` form a saturated
`K5` component.

If `x3=3`, the three size-three point sets are disjoint. Two disjoint triples
cannot lie in one five-vertex component, so they force three distinct `K5`
components, requiring fifteen vertices. This eliminates the first solution
in (4).

## Excluding the residual six-vertex case

For `(x2,x3)=(15,1)`, the unique size-three point forces one `K5` component.
The remaining component `R` is 4-regular on six vertices, hence

```text
R = K6 minus a perfect matching M.
```

Every active triangle `v` in `R` has three size-two point sets, which consume
three distinct incident `K`-edges and leave one incident edge unused. Do not
confuse these locally unused edges with the structural missing matching `M`.

Take any two of the three consumed neighbors `a,b` of `v`. The corresponding
original points both lie on graph-triangle `v`, so they form an actual graph
edge. Their overlapping active sets `{v,a}` and `{v,b}` have crossing degree
one exactly when `ab` is not a `K`-edge. Equation (2) forbids degree one.
Thus the three consumed neighbors of `v` must form a clique in `R`.

But the four neighbors of any vertex of `K6-M` contain the two remaining
nonedges of `M`. Deleting any one neighbor leaves one complete nonedge pair,
so no three of those four obtained this way form a clique. This is the final
contradiction.

## Consequences and status boundary

Both active profiles at `n3=33` are impossible. Combining this exclusion with
the Wave 8 bound and `n3=0 (mod 3)` gives the conditional necessary bounds

```text
n3 >= 36,
induced_C6_count = 209,286 + n3 >= 209,322.
```

The twelve normalized branch bounds strengthen to

```text
36,36,42,48,48,36,42,48,36,48,42,48.
```

The compact checker enumerates both active profiles, the local singleton
crossing graphs, the point-size solutions, all local size-three closures, all
15 perfect matchings on the residual six vertices, and all 360 labeled local
unused-edge choices. It has no survivor. A separate two-implementation census
of all 266 quartic types and 610 admissible point-clique families likewise has
zero survivors: every family already contains an internal actual graph edge
of forbidden `H`-degree one or two.

A focused primary-source search found no checked occurrence of the exact
`n3=33` exclusion or this proof chain. That is not evidence of novelty. The
result is described only as a conditional project derivation pending external
review, while the upstream Lou--Murin, Makhnev, and Reimbayev ingredients keep
their cited attribution. The checkers are regression companions to the human
proof, not standalone Conway-99 certificates. The target remains `UNKNOWN`.
