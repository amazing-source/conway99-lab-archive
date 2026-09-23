# Wave 15 global-lift preinspection freeze

Frozen at `2026-07-23T09:43:15Z`, after reading only:

- `agents/2026-07-22-wave14-n3-48-proof-a.md`;
- `verification/2026-07-22-wave14-n3-48-proof-audit.md`.

No file under `attempts/wave14-proof-a/` and no Wave 15 sibling work had
been inspected when this framework was frozen.

## Human framework

Assume the audited conditional `n3=48` boundary.  Let `X` be the set of
original graph vertices whose active point is nonempty.  The active point
incidence sum is 48, all point sizes are two or three, and therefore

```text
16 <= |X| <= 24.
```

At a point `P` of size `s`, the active triangles through the corresponding
original vertex supply `2s` distinct neighbors inside `X`.  The residual
support graph `R` supplies `s` actual graph-edge neighbors inside `X`.
An `R`-edge can duplicate an active-triangle edge only when it is a full
meeting crossing.  There are at most `s` such duplicated neighbors.
Consequently the immediate coarse bound is only `d_X(P) >= 2s`, which is
four for a size-two point and six for a size-three point.  A sharper audit
must determine the maximum possible overlap between the two neighbor
sources.  In the all-size-two subcase no support edge can be a meeting
edge, because deleting the shared label leaves a crossing too small to
have `H`-degree four.  Hence every all-size-two active vertex has at least
six neighbors in `X`.

For an arbitrary subset `X` of size `m` in an
`srg(99,14,1,2)`, write `d_x=d_{G[X]}(x)`, `e=|E(G[X])|`, and
`a_y=|N(y) intersect X|` for `y` outside `X`.  Double counting common
neighbors of pairs in `X` gives

```text
sum_outside C(a_y,2)
  = m(m-1) - e - sum_inside C(d_x,2),
sum_outside a_y = 14m - 2e.
```

Thus

```text
sum_outside a_y^2
  = 2m^2 + 12m - sum_inside(d_x^2+d_x).
```

Cauchy over the `99-m` outside vertices imposes

```text
(99-m) [2m^2+12m-sum(d_x^2+d_x)]
  >= [14m-sum d_x]^2.                         (F)
```

The first target is to apply (F) to the all-size-two countermodel family,
where `m=24` and `d_x>=6`.  Writing `d_x=6+s_x`,
`T=sum s_x`, and `U=sum s_x^2`, the Cauchy defect
`left-right` becomes

```text
-4464 - 591T - 75U - T^2,
```

which is strictly negative.  This would exclude every full Conway lift of
the all-size-two active relaxation, including lifts with additional
active-active graph edges.

## Planned checks after the freeze

1. Inspect the permitted Wave 14 countermodel only to verify the semantic
   translation: point objects are original vertices, the mandatory
   active-triangle graph has degree four, support degree is two, and support
   edges do not overlap active-triangle edges in the all-size-two case.
2. Produce a standalone exact checker and a machine-readable arithmetic
   certificate for (F), including hostile mutations.
3. Investigate whether surviving size-three local modes bound the number of
   support/active-triangle overlaps tightly enough to force
   `d_X(P)>=6` at every point.  If yes, the same variance calculation may
   exclude the entire residual because `|X|<=24`.
4. Record any failed weaker common-neighbor or inactive-completion approach
   without promoting a computational non-hit.
