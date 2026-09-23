# Wave 14 `n3=48` proof-audit preinspection freeze

Frozen at `2026-07-23T09:19:34Z`, before opening
`agents/2026-07-22-wave14-n3-48-proof-a.md` or any file below
`attempts/wave14-proof-a/`.

The reconstruction used these earlier framework files:

```text
4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2  agents/2026-07-22-wave6-opposite-edge-graph.md
7b4693420eae7e6f13ce0d66c786424c18863a1b1c350da83097f8e982ebe324  agents/2026-07-22-wave7-triangle-side-incidence.md
010fe1e2a9752ac18067b44c9e6cf1114e2d1651364c49a574adbe22fe5461f3  agents/2026-07-22-wave8-n3-equality.md
b2fe46cce67440d1a730d6f56b48a512952624d79afa9835ffc772c050c94555  agents/2026-07-22-wave9-n3-33-equality.md
971e0809376d5bb40967ddd297eca627e0b125df908e30817a95cfa67d5b6f4a  agents/2026-07-22-wave12-n3-42-proof-a.md
```

## Independently reconstructed facts

- At `n3=48`, `sum q=32`, every active `q>=2`, and
  `3q<=r-1`. Exact multiset enumeration gives 12 profiles:
  one at `r=11`, one at `r=12`, four at `r=13`, three at
  `r=14`, two at `r=15`, and one at `r=16`.
- With `K=overline{L[A]}`, every active label lies in three non-singleton
  point cliques consuming distinct incident `K`-edges. Thus `d_K>=3`;
  the inherited degree-three obstruction strengthens this to `d_K!=3`.
  These filters leave `(r;q)=(14;2^10,3^4)`,
  `(15;2^13,3^2)`, and `(16;2^16)`.
- In the `r=16` all-`q=2` case, `K` is simple 9-regular. Petal expansion
  gives point size at most five. For a point clique `P` of size `s`, each
  of its `2s` petals has a disjoint nonempty external part. In a labeled
  crossing against `P-{i}`, each external vertex has `L`-crossing degree
  zero or two. An external part of size `a>=2` therefore contributes at
  least `a+(s-3)a=(s-2)a` `K`-edges into `P`; a singleton side has empty
  crossing and contributes exactly `s`. For `s=5`, every petal contributes
  at least five cut edges, so the cut is at least `50>25`; for `s=4`, every
  petal contributes at least four, so the cut is at least `32>24`. Hence
  points have size two or three.
- Put `F` equal to the union of point-clique edges, `U=K-E(F)`, and let
  `t_i` count size-three points through label `i`. Then
  `d_F(i)=3+t_i` and `d_U(i)=6-t_i`. For a size-three point
  `{i,j,k}`, size-two petals at `j,k` force
  `t_i<=t_j+t_k`, cyclically. These inherited capacity inequalities alone
  leave nine sorted modes, not eight; an additional premise is required to
  remove one of them. This discrepancy is frozen as an audit target.
- If every point has size two, the point family is the edge set of a simple
  cubic triangle-free graph `F` on 16 labels, with `F subset K`. Empty
  singleton crossings force every `F`-distance-two pair into
  `U=K-E(F)`.
- For two disjoint `F`-edge points, a positive labeled crossing is exactly
  an `L`-complete `2 x 2` rectangle and has `H`-degree four. The fixed-point
  identity gives each of the 24 point objects exactly two such support
  partners. Each of the 48 `L`-edges (an `N3` side pair) must be covered
  by exactly two rectangles corresponding to its two independent cross
  graph edges. These are necessary abstract active-layer conditions, not
  sufficient conditions for a 99-vertex strongly regular graph.

The two surviving mixed-profile exclusions, the extra condition reducing
the nine raw size-three modes to eight, and the claimed explicit abstract
countermodel remain deliberately unresolved at this freeze.
