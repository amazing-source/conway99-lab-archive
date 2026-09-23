# Wave 40 edge-type coupling audit

Date: 2026-07-27 UTC

Verdict: **PASS for scoped conditional identities and finite enumerations.**
The endpoint, improved general upper bound, target graph, and novelty remain
`UNKNOWN`.

## Independence and frozen premises

The verifier did not read, import, or execute
`attempts/wave40-edge-type-coupling`. It reconstructed the target from the
audited `J/H`, triangle-side `L`, Wave 39 local-rank, and frozen conjecture
premises listed in `input-freeze.sha256`.

## Global complex

At the prism-free endpoint, every `J` edge is nontriangular. A `J` edge is
therefore the pair of opposite cross-edges of a unique induced `N3`, and maps
to the `L` edge joining its side triangles. This proves the endpoint
`E(J)<->E(L)` bijection.

For a graph edge `e`, the incident `L` edges form a two-regular link. Types
`222,24,33,6` give face-boundary lengths respectively

```text
(4,4,4), (4,8), (6,6), (12).
```

Every `L` edge has exactly two face incidences, selected by the two distinct
cross-edges of its `N3`. The face identities and edge-face handshake in the
result file follow.

The unsplit object has 231 vertices, 4,158 edges, and
`F=3*t222+2*t24+2*t33+t6` faces. It is a closed two-complex but not
automatically a surface: the link at a triangle can be disconnected.
Splitting once per link cycle gives a closed surface with

```text
V=C=sum_T components(H_T), E=4158, F as above.
```

Each `H_T` is a two-factor on 36 vertices with cycles of length divisible by
three and at least six, so `231<=C<=1386`. The coarse surface Euler range is
`-3234<=chi<=-693`. Negative Euler characteristic is allowed; orientability
parity is conditional and supplies no contradiction.

## Complete quotient normalization

Collapse each within-fibre pair in the all-`222` one-triangle graph. Between
each pair of six-point fibres, the quotient is `3C4`. Fix the `01` relation.
At fibre 1, the two induced pairings have exactly three relative types:

```text
111:1, 12:6, 3:8.
```

One representative of each relative type fixes the `12` relation. The
remaining `20` relation is determined by a pairing on each side and a
permutation of its three blocks: `15*15*6=1350`. Hence the 4,050-case list is
complete under fibre relabeling. It is not asserted to be an isomorphism
census.

Independent elimination of `2I+A_Q` over `F_3` gives

```text
{11:8,12:1,13:400,14:46,15:2616,16:979}.
```

## Exhaustive lift and 39-block identity

At each of the eighteen quotient vertices, independently swapping the two
underlying endpoints removes one of two endpoint-assignment bits. One
relative bit remains, so the checker covers exactly `2^18` masks.

The canonical rank-eleven quotient has sixteen quotient triangles. Each
triangle lifts precisely at one prescribed pattern of its three local bits.
Rejecting every such pattern leaves exactly 37,378 triangle-free masks.
Exact symmetric elimination over `F_7` gives the two recorded rank
distributions.

For completeness, order the 39-set as `T|X`, let `R` be the three fibre
indicators, and take `K=J-I-2A` over `F_7`. The `T` block is `I-J_3`, whose
inverse is `I+3J_3`. Its Schur complement vanishes on
`U=span(R^T)` and equals `2(3I-A_X)` on `U_perp`. Meanwhile
`3I-A_X` has rank two on `U`. Thus

```text
rank(K_39)=3+(rank(3I-A_X)-2)=1+rank(3I-A_X).
```

The emitted canonical witness independently checks ranks 32 and 33 by dense
elimination as a positive control.

## Scope wall

No 60-column `B`, compatible `Y` graph, cross-triangle gluing, 99-vertex
adjacency matrix, graph, counterexample, endpoint exclusion, or upper-bound
improvement is supplied. The positive one-triangle control shows that this
lane reaches a feasible local boundary rather than a contradiction.
