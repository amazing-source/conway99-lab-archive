# Wave 15 global-lift verifier preinspection freeze

```yaml
role: verifier
date_utc: 2026-07-23T09:56:11Z
git_commit: UNRECORDED_NO_GIT
claim_label: DERIVED
scope: independent reconstruction of a global contradiction from the audited Wave 14 n3=48 residual, frozen before inspection of the Wave 15 global-lift submission
inputs:
  agents/2026-07-22-wave14-n3-48-proof-a.md: f0a7d7b5638415cff7d5ad4ef176542de9aa89a2b46a03347f90a2133f18999c
  verification/2026-07-22-wave14-n3-48-proof-audit.md: 44d1383548b26660dfb5d4b140c831774f6ca81e58ae140e3ceb2f80a9740802
method: direct reconstruction from the audited residual, SRG identities, and the two-sided labeled-crossing rule
command: none; human derivation frozen before reading agents/2026-07-23-wave15-global-lift.md
outputs:
  reconstructed_subset_bound: "|X| >= 27 if delta(G[X]) >= 6"
  wave14_residual_bound: "|X| <= 24 and delta(G[X]) >= 6"
  conditional_n3_48_exclusion: DERIVED_PENDING_SUBMISSION_AUDIT
limitations: conditional on the audited Wave 14 residual and inherited semantic bridges; this freeze has not inspected the Wave 15 discovery report; target existence and novelty remain UNKNOWN
```

## Inspection boundary

Before this freeze I read only:

1. `agents/2026-07-22-wave14-n3-48-proof-a.md`; and
2. `verification/2026-07-22-wave14-n3-48-proof-audit.md`.

I did not open `agents/2026-07-23-wave15-global-lift.md`, any Wave 15
attempt artifact, or the separate Wave 15 algebraic report.  The
reconstruction below is therefore independent of the submitted global-lift
lane.

## Audited premises carried forward

Assume that an `srg(99,14,1,2)` exists and that `n3=48`.  The audited Wave 14
residual supplies:

- sixteen active graph-triangle labels, each lying in exactly three indexed
  nonempty active points `S_u`;
- every active point has size two or three;
- the sum of point sizes is `16*3=48`;
- a simple support graph `R` on the indexed active point objects;
- every edge of `R` is an actual graph edge between the corresponding
  original vertices;
- `d_R(S_u)=|S_u|`; and
- for an actual graph edge `uv`, after deleting both labeled copies of the
  possible common active triangle from the crossing between `S_u` and
  `S_v`, every remaining row and column has degree zero or two and the
  crossing size equals `d_H(uv)`.  An `R`-edge has `d_H(uv)=4`.

No automorphism, connectedness, completion heuristic, or solver result is
used below.

## Independent local-to-global reconstruction

Let

```text
X = {u in V(G) : S_u is nonempty}.
```

The points are indexed by original vertices.  They are also distinct as
sets: if two different vertices had the same active point of size at least
two, two distinct graph-triangles would contain both vertices and hence
share their graph edge, impossible when `lambda=1` (each graph edge has a
unique common neighbor and lies in a unique triangle).  Thus the point
objects and the vertices of `X` are in bijection.

Every point has size at least two, while

```text
sum_(u in X) |S_u| = 48.
```

Consequently

```text
|X| <= 24.                                                (F1)
```

If `P=S_u` has size `s`, each active graph-triangle in `P` gives two
neighbors of `u` in `X`.  Distinct graph-triangles through `u` cannot share
another vertex, because then they would share the edge from `u` to that
vertex.  Hence these are `2s` distinct neighbors:

```text
d_(G[X])(u) >= 2|P|.                                     (F2)
```

Every `R`-neighbor of `P` is a distinct vertex of `X` adjacent to `u` in
`G`, because `R` is simple and its edges are actual graph edges.

The only possible overlap relevant to a degree-six lower bound occurs when
`|P|=2`.  If an active-triangle neighbor `v` of `u` were also an
`R`-neighbor, then `P` and `Q=S_v` would share their active triangle label.
After deleting that label on both sides, the crossing has only one row on
the `P` side.  The inherited two-sided `0/2` law forces every remaining
column to have degree zero: with one row, a nonzero column would have degree
one.  Therefore the crossing is empty and `d_H(uv)=0`, contradicting the
requirement `d_H(uv)=4` for an `R`-edge.

Thus, for `|P|=2`, its four active-triangle neighbors and its
`d_R(P)=2` support neighbors are disjoint.  For `|P|=3`, the active
triangles alone give six distinct neighbors.  In both cases,

```text
delta(G[X]) >= 6.                                        (F3)
```

## Independent spectral subset bound

The nonprincipal eigenvalues of an `srg(99,14,1,2)` are the roots of

```text
theta^2 - (lambda-mu)theta - (k-mu) = 0,
```

namely `3` and `-4`.

For a subset `X` of size `m`, write its characteristic vector as

```text
1_X = (m/99) 1 + y,  with y perpendicular to 1.
```

Since the largest eigenvalue on `1^\perp` is `3`,

```text
2e(X)
 = 1_X^T A 1_X
 <= 14m^2/99 + 3(m-m^2/99)
 = 3m + m^2/9.
```

Therefore

```text
average_degree(G[X]) <= 3 + m/9.                         (F4)
```

If `delta(G[X])>=6`, then the average degree is at least six, so

```text
6 <= 3+m/9,
m >= 27.                                                 (F5)
```

Equations (F1) and (F5) contradict one another.  Subject to the audited
Wave 14 premises, `n3=48` is therefore impossible.

## Independent second-moment route to check after inspection

There is also a purely counting form of the same obstruction.  Put
`a_x=|N(x) intersect X|` for `x in X`, and
`b_z=|N(z) intersect X|` for `z outside X`.  If `m=|X|` and
`D=sum_X a_x=2e(X)`, then

```text
sum_outside b_z = 14m-D,
sum_all_vertices C(d_X(v),2) = 2C(m,2)-e(X).
```

Equivalently,

```text
sum_X a_x^2 + sum_outside b_z^2 = 2m^2+12m-D.
```

Cauchy on the two vertex classes gives, with `t=D/m>=6`,

```text
m t^2 + m^2(14-t)^2/(99-m) <= 2m^2+12m-mt.              (F6)
```

At the suspected extremal boundary `m=24,t=6`, the left side is
`24*36 + 24^2*64/75`, while the right side is
`2*24^2+12*24-144`; the left exceeds the right.  A verifier must still
check monotonicity (or an exact integer convexity argument) over
`7<=m<=24` and all feasible `t>=6` before treating this as a standalone
alternative.  The spectral proof (F4)-(F5) is already complete and does not
depend on that pending check.

## Preinspection objections to attack

The submitted proof must survive all of the following:

1. point objects must not be conflated with labels or unindexed set values;
2. every claimed neighbor must be an original vertex in `X`;
3. active-triangle neighbors must be distinct;
4. `R` must be loopless/simple and each `R`-edge an actual `G[X]` edge;
5. disjointness of the two neighbor sources is needed only for size-two
   points and must use both sides of the labeled `0/2` crossing law;
6. the subset inequality must use the positive restricted eigenvalue `3`,
   not the least eigenvalue `-4`;
7. minimum degree must not be replaced by an unsupported regularity claim;
   and
8. exclusion of `n3=48` does not by itself resolve Conway-99 or establish
   novelty.
