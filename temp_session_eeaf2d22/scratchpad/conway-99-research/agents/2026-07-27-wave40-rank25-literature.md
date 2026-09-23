# Wave 40 literature/priority audit: the characteristic-7 rank-25 condition

Date: 2026-07-27

Role: statement/literature agent

## Frozen target

For a hypothetical `srg(99,14,1,2)`, let `N` be the vertex-triangle
incidence matrix, let `E0` be the rational projector used in the Wave 40
triangle-space construction, and put

```text
M = 21 E0,
K = N M N^T = J - I - 2A  (mod 7).
```

The independently verified Wave 40 conclusion being audited is the universal
necessary condition

```text
rank_F7(M) = rank_F7(K) >= 25.
```

The proof uses the 27 vertices induced by an edge and both endpoint
neighborhoods, the 11 possible alternating-component types, the 12-point third
fiber at the common triangle mate, and a bordered-matrix rank lemma. This audit
asks whether that exact conclusion, or an equivalent result with those
ingredients, was already publicly stated.

## Outcome

```text
exact/equivalent rank_F7(M) >= 25 result located:  NO, in the bounded corpus
27-vertex edge-neighborhood and its 11 types:      PRIOR ART
general p-rank/Smith-form framework for aA+bJ+cI: PRIOR ART
triangle-incidence and clique-graph spectrum:      PRIOR ART
Conway-specific Smith form of the Laplacian:       PRIOR ART, DISTINCT MATRIX
Conway-specific finite-field frame consequence:    PRIOR ART, CHARACTERISTIC 5
novelty:                                           UNKNOWN
priority:                                          UNKNOWN
```

The strongest permitted sentence is:

> No exact prior statement equivalent to
> `rank_F7(M) >= 25` was located in the bounded primary sources searched
> through 2026-07-27.

This is a search result, not a novelty or priority claim.

## Most important overlap

Gray Taylor's public 2020 repository, pinned at
`68a9f2dcade05581986bf98b97cf8d7a5cdd4158`, contains a notebook that starts
with adjacent vertices `a,b`, their unique common neighbor, and the remaining
12 neighbors on each side. It derives the internal side matchings and the
matching between the two 12-sets. Its recorded exhaustive reduction produces
11 representatives on the resulting 27 vertices. Taylor's accompanying post
also states that there are exactly eleven possibilities and describes the
subsequent combinatorial explosion.

This is exact prior art for the Wave 40 **27-point local scaffold and
11-type classification**. It does not contain the 12-point third fiber, the
permutation border, the characteristic-7 bordered-rank calculation, the
integral projector `M`, or the lower bound 25. Searches for `rank`, `Smith`,
`Seidel`, `mod 7`, `F7`, and `incidence` in the pinned notebook were negative.

## Algebraic prior art

Brouwer and van Eijl's 1992 paper studies the `p`-rank and Smith form of
integral matrices `aA+bJ+cI` attached to a strongly regular graph. Thus its
scope contains `K=J-I-2A` directly. It identifies the structure-dependent case
as the one where `p` divides the difference of the two restricted
eigenvalues. For Conway's parameters those eigenvalues are `3` and `-4`, so
`p=7` is exactly that case. The paper supplies general parameter-only upper
bounds and structural tools; it does not state a positive Conway-specific
lower bound, the number 25, or the Wave 40 local coupling.

Van Eijl's 1991 thesis is the precursor cited by the paper. Peeters's 1995
minimal-`p`-rank paper studies `A+cI` and structural characterizations. The
2022 Brouwer--Van Maldeghem monograph surveys `p`-ranks and separately lists
the Conway problem. Direct text searches found no joining of the Conway
parameter set to the rank-25 statement in these sources.

## Near hits that use different matrices or fields

- Ducey et al. compute the full critical group forced by the hypothetical
  Conway graph's parameters. This is Smith-form information for the Laplacian
  `14I-A`, not for `M` or `K`; its primes are `2`, `3`, and `11`, not `7`.
- Greaves, Iverson, Jasper, and Mixon show that a Conway graph would imply a
  100-vector equiangular tight frame in dimension 45 over `F_5`. This is a
  finite-field Seidel/Gram consequence in characteristic 5, not the
  characteristic-7 rank of `K`.
- Petro and Phillips define the vertex-clique incidence matrix and derive the
  triangle-clique graph spectrum of a hypothetical Conway graph. Their
  spectrum `18^1, 7^54, 0^44, (-3)^132` is close to the Wave 40 triangle-space
  setup, but they do not discuss modular rank, Smith form, `M`, `K`, or 25.

## Direct Conway sources and computational work

The Wilbrink report and the Cesarz--Woldar paper concern automorphism
restrictions. Lou--Murin, Selub, Dunkel, Keramatipour, and Reimbayev pursue
subgraph, local-search, SAT, or small-subgraph approaches. Direct text searches
of the accessible primary PDFs did not locate the relevant rank terminology or
an equivalent result. Exact GitHub code searches for the frozen formula and
rank aliases returned no hits. These nonhits are recorded only as bounded
coverage evidence.

## Priority boundary

The Wave 40 contribution must not be described as inventing the 27-point
edge-neighborhood classification. Any future paper should cite Taylor's pinned
notebook/post for that scaffold and describe the new work, if independently
accepted, as the characteristic-7 **extension through the third fiber and
border coupling**.

The source ledger, exact queries, pins, and limitations are in
`attempts/wave40-rank25-literature/`.
