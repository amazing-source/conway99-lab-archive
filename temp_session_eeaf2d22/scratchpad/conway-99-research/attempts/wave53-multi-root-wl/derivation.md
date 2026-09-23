# Forced overlap of two rooted neighborhoods

Everything here is conditional on a prism-free `srg(99,14,1,2)`.

## Common `K`-neighbors

Let `R,S` be graph triangles. A triangle is a common `K`-neighbor when it
shares one graph vertex with each root.

- If `R,S` share a vertex, the five other triangles through that vertex are
  their common `K`-neighbors.
- If `R,S` are disjoint, every cross edge between them lies in a unique graph
  triangle. That triangle is a common `K`-neighbor.
- Conversely, a common `K`-neighbor of disjoint roots contains one vertex of
  each root and therefore supplies a cross edge.

Thus the common-neighbor counts are `5,2,1,0` in relations `K,B,C,D`.

Cross edges between disjoint root triangles form a matching. If one root
vertex met two vertices of the other triangle, it would be a second common
neighbor of an adjacent pair, contradicting `lambda=1`. Hence the two common
petals in relation `B` occupy distinct sectors at both roots.

## The shared forced-true variable for `B`

Write the two root cross edges as `r0-s0` and `r1-s1`, and let their unique
triangles be

```text
T0={r0,s0,t0},  T1={r1,s1,t1}.
```

Between `T0,T1`, the edges `r0-r1` and `s0-s1` are already present because
the endpoints lie in `R` and `S`. No endpoint-to-third-vertex cross edge can
occur: for example, `r0-t1` would make `t1` a second common neighbor of the
adjacent pair `r0,r1`. The only possible third cross edge is `t0-t1`, and
that would make a triangular prism. At the prism-free endpoint it is absent.
Therefore `T0,T1` are in relation `B`.

The unordered pair `{T0,T1}` occurs as a cross-sector candidate in both
rooted systems. The CSP identifies these occurrences as one Boolean variable
and fixes it to one.

## What remains unresolved

Every other cross-sector petal pair inside either root neighborhood remains an
unselected `B/C` candidate. Each petal has an exact-two cap toward each
opposite sector. The two-root union identifies only genuinely identical
triangle pairs; it does not align sectors, select cycle profiles, or assume
that any local permutation extends globally.
