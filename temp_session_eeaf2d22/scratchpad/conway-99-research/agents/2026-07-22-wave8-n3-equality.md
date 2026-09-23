# Wave 8 exclusion of the `n3=30` equality case

```yaml
role: proof_b
date_utc: 2026-07-23T01:26:58Z
git_commit: b2a31846d243a76b9e516f85304e21137e3fe874
claim_label: DERIVED
scope: conditional exclusion of n3=30 for a putative srg(99,14,1,2)
inputs:
  STRUCTURE.md: 90a3143f3eba935beb10eb424a6a2940dc52a2c09755225b3fcee9e9bf532efd
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  agents/2026-07-22-wave7-triangle-side-incidence.md: 2225d7f26f8719d24bceca0c4ef6d8b829332a80793762769d282f176e75b651
  verification/n3-equality/verify.py: 17b306d0e7d198d5c30e068a9c4e7b490ff01dfc91758416b9e67ed641007bf6
  verification/test_n3_equality.py: 8f6a7c6772733386ccb71810c24c996b2ef1739588846a622d670bffa44ad313
method: fixed-endpoint N3 incidence identity, point-clique edge accounting, and a local overlapping-set contradiction
command: |
  python verification/n3-equality/verify.py
  python -m unittest verification.test_n3_equality -v
outputs:
  conditional_global_n3_lower_bound: 33
  conditional_induced_C6_lower_bound: 209319
  branch_n3_lower_bounds: [33, 33, 42, 48, 48, 33, 42, 48, 33, 48, 42, 48]
limitations: conditional on the supplied Wave 6/7 lemmas and target-specific N3 occurrence; no construction or nonexistence proof for Conway-99 is produced
```

## Equality setup

Assume that a putative `srg(99,14,1,2)` has exactly `n3=30` induced copies
of `N3`. Retain the Wave 6 graph `H` on graph-edges and the Wave 7 graph `L`
on graph-triangles.

The Wave 7 identities say

```text
q(T)=0 or q(T)>=2,
d_L(T)=3q(T),
sum_T q(T)=2n3/3=20.
```

If there are `r` active triangles, then `r<=10`. If `r<=9`, some active
`q(T)` is at least three, giving `d_L(T)>=9>r-1`. Hence there are exactly ten
active triangles, every one has `q=2`, and the active part of `L` is
6-regular. Write

```text
K = complement(L)
```

on these ten active triangles. Thus `K` is a simple cubic graph with fifteen
edges. No connectedness or completed-graph automorphism is assumed.

Lou and Murin's 2014 MIT PRIMES-USA report already contains the equivalent
fixed-triangle partner profile and the `q!=1` gap used upstream. Those facts
are cited prior art or independent rederivations, not project novelty. The new
step checked in this wave begins with the fixed-*original-point* incidence
identity below and its point-clique consequences; novelty is not asserted for
that step either. See `agents/2026-07-22-wave8-status-search.md`.

## A fixed-point incidence identity

Fix an active graph-triangle `T={x,a,b}`. The ordered-pair construction used
for the Wave 7 second moment is uniform: for each unordered pair of vertices
of `T`, exactly twelve disjoint graph-triangles have cross-edges at both
chosen vertices.

For example, fix the ordered pair `(x,a)`. For each of the twelve neighbors
`u` of `x` outside `T`, the pair `u,a` is a nonedge. Besides `x`, it has one
other common neighbor `v`. The unique graph-triangle on edge `uv` is disjoint
from `T` and has cross-edges `xu,av`. Conversely, a disjoint triangle using
cross-edges at `x` and `a` recovers its unique `u`. Reversing the order counts
the same twelve partners, so this is a count of twelve for the unordered
side-vertex pair, not twenty-four.

Every prism partner uses all three side-vertex pairs. Since

```text
p(T)=12-q(T),
```

exactly `q(T)` of the twelve partners for each side-vertex pair are `N3`s.
Each vertex of `T` belongs to two such pairs, so it is an endpoint of a cross-
edge in exactly `2q(T)` of the `N3`s having side `T`.

Now fix an original graph vertex `u` and put

```text
S_u = {active graph-triangles containing u},
s_u = |S_u|.
```

Every `H`-edge incident with a graph-edge `uv` is one `N3`, and exactly one of
its two disjoint side triangles contains `u`. Summing the fixed-side count is
therefore a bijective incidence count:

```text
sum_{v: uv in E(G)} d_H(uv) = 2 sum_{T in S_u} q(T).
```

All active `q` values are two in the equality case, giving the key identity

```text
sum_{v: uv in E(G)} d_H(uv) = 4 s_u.                 (1)
```

There is no orientation or factor-of-two ambiguity: one `N3` that uses `u`
has exactly one cross-edge incident with `u`. When `S_u` is empty, both sides
of (1) are zero.

## Point cliques in the cubic complement

Each `S_u` is a clique in `K`, because graph-triangles sharing `u` cannot be
adjacent in `L`. Hence `s_u<=4`. Two different point cliques consume disjoint
`K`-edges: otherwise two graph-triangles would share two original vertices,
putting the edge between those vertices in two graph-triangles.

Counting the three original vertices on each of the ten active triangles and
the consumed `K`-edges gives

```text
sum_u s_u = 30,
sum_u binom(s_u,2) <= 15.                             (2)
```

The Wave 6 local matching identity and the Wave 7 support identity remain in
force for every actual graph edge:

```text
d_H(uv) in {0,4,6,8,10,12},
d_H(uv) = e_L(S_u,S_v).                               (3)
```

The crossing in (3) is counted once even if `S_u,S_v` overlap.

## Excluding a size-four point

Suppose some `S_X` has size four. A 4-clique in a cubic graph is an entire
`K4` component, and `S_X` consumes all six edges of that component. In each
of its four active triangles, the two original vertices other than `X` can
belong to no second active triangle: that would consume an already consumed
edge of the `K4`, while no `K`-edge leaves the component. Thus the four
triangles force eight distinct singleton points.

There is no second size-four point. It cannot use the same `K4`, because point
cliques consume disjoint edges. Another 4-clique would be a second `K4`
component, leaving two vertices of the ten-vertex cubic graph, which is
impossible. For any one of the forced singleton points `S_u={T}`:

- its `L`-crossing with `S_X` is zero, because `T` and the other members of
  `S_X` lie in the `K4`; and
- its crossing with every other point is at most three.

By (3), every actual graph edge incident with `u` has `H`-degree zero. This
contradicts (1), whose right side is four. Therefore no size-four point exists.

## Excluding all remaining point sizes

With no size-four point, a singleton has crossing at most three with every
point. Equations (1) and (3) again make a singleton impossible. Let `x_i`
count points of size `i`. Equations (2) reduce to

```text
2x_2 + 3x_3 = 30,
x_2 + 3x_3 <= 15.
```

Substitution gives

```text
15 + (3/2)x_3 <= 15,
```

so `x_3=0` and `x_2=15`. Equality holds in the edge budget: every `K`-edge is
consumed by one size-two point.

A cubic graph on ten vertices cannot have every component equal to `K4`.
Choose a vertex `i` of `K` with two nonadjacent neighbors `j,k`. The consumed
edges `ij,ik` correspond to two distinct original vertices `u,v` in the
active graph-triangle indexed by `i`, with

```text
S_u={i,j},
S_v={i,k}.
```

In particular, `uv` is an actual graph edge. Among the possible crossings of
these overlapping sets, `ij` and `ik` are `K`-edges, `ii` is not an edge, and
`jk` is the unique `L`-edge. Therefore (3) gives

```text
d_H(uv) = e_L(S_u,S_v) = 1,
```

contradicting the allowed degree set in (3). This excludes `n3=30`.

## Consequences and status boundary

Wave 7 proved `n3>=30`, and `n3` is divisible by three. The equality exclusion
therefore yields the conditional necessary bounds

```text
n3 >= 33,
induced_C6_count = 209,286 + n3 >= 209,319.
```

The twelve normalized branch bounds become

```text
33,33,42,48,48,33,42,48,33,48,42,48.
```

The checker reproduces the finite arithmetic, point-size equations,
component-order alternatives, local overlapping crossing, and bound tuple.
It is a regression companion to the human graph-theoretic proof, not a
standalone nonexistence certificate. The Conway-99 existence question remains
`UNKNOWN`.
