---
role: construction
date_utc: 2026-07-23T18:46:39Z
git_commit: 121a2fda5d9d36d8a16825f2a29d0765d1285eb1
claim_label: DERIVED
scope: complete order-seven deletion-deck necessary-condition system at n3=705, including the 19 published Hamiltonian counts at h11=2820
inputs:
  - path: attempts/wave21-six-vertex-lp/exact-results.json
    sha256: 5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b
  - path: arxiv:2511.06572v1 source archive
    sha256: 10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a
method: exhaustive labeled census and S7 canonicalization, exact deletion decks, discovery-only SciPy MILP, then a standard-library exact replay of the frozen integer witness
command: python attempts/wave22-full-seven-deck/exact_check.py --output attempts/wave22-full-seven-deck/exact-results.json
outputs:
  - path: attempts/wave22-full-seven-deck/witness.json
    sha256: d74453faa91e42abbe2343d428296818ae051be579305277eff6f113fe66c47d
  - path: attempts/wave22-full-seven-deck/exact-results.json
    sha256: ca5d9d116f6a9d6e355600429652e2bf4474b73dcf281bbcb564420d820acbd2
limitations: aggregate necessary counts only; no overlap consistency or 99-vertex adjacency matrix; H-panel transcription is human source interpretation; independent verifier review still required
---

# Wave 22: the complete seven-vertex deletion deck is feasible at the incumbent

## Verdict

`DERIVED_INCONCLUSIVE`.

I found and froze a nonnegative integer solution of the complete 62-equation
order-seven vertex-deletion deck system at `n3=705`.  More strongly, the same
witness fixes all 19 Hamiltonian seven-vertex isomorphism types to the published
formulas at the admissible value `h11=2820`.

This closes the route negatively: these necessary count equations do not
improve the conditional bound `n3>=705`.  The witness is not a graph
construction and does not change Conway-99's `UNKNOWN` status.

## Exact system

Let `x_J` be the number of induced seven-subsets whose canonical isomorphism
type is `J`.  For source six-vertex type `N_i`, let `d_i(J)` be the number of
vertices of `J` whose deletion leaves a graph isomorphic to `N_i`.  Double
counting a six-subset together with one outside vertex gives

```text
sum_J d_i(J) x_J = (99-6) n_i = 93 n_i,   i=1,...,62.
```

Every column sums to seven.  Consequently the row equations imply the
redundant total

```text
sum_J x_J = binom(99,7) = 14887031544.
```

The `n_i` values are the Wave-21 exact formula values at `n3=705`.  The
source-`N_i` to canonical-mask alignment is an explicitly pinned Wave-21 input.
Wave 22 independently enumerates the six-vertex class universe and checks that
the 62 pinned masks are a bijection over it.

## Complete independent census

The exact checker enumerates all `2^21` labeled graphs on seven vertices and
keeps precisely those satisfying the necessary induced-subgraph inequalities:

```text
inside common neighbors <= 1 for an edge;
inside common neighbors <= 2 for a nonedge.
```

It finds:

```text
locally admissible labeled masks:       394020
locally admissible unlabeled classes:      208
six-vertex unlabeled classes:                62
deletion-matrix shape:                   62 x 208
```

Canonicalization takes the least edge mask over all `7!` vertex permutations;
it does not assume an automorphism.  Exact modular Gaussian elimination gives

```text
rank over F_2  = 48
rank over F_3  = 57
rank over F_5  = 61
rank over F_7  = 61
rank over F_11 = 62.
```

The last equality proves real row rank 62.  It does not, by itself, prove
integer feasibility; the frozen witness does that for the selected right-hand
side.

## Source-Hamiltonian alignment

The pinned TeX says that `H_0` is the omitted bare `C7` and that figure panels
1 through 18 are `H_1` through `H_18`.  I read the perimeter vertices clockwise
as `0,...,6`, with vertex 0 at the top, and transcribed only the extra chords in
each green panel.  The exact checker canonicalizes those 19 labeled drawings.

This produces 19 distinct canonical masks.  Independently, the checker fixes a
labeled `C7`, enumerates every subset of its 14 chords, filters by the local
conditions, and canonicalizes.  Any Hamiltonian graph can be relabeled so that
one Hamiltonian cycle is this fixed `C7`, so this is complete.  The independent
census also has 19 classes, and its set of masks is exactly the transcribed set.

At `n3=705`, `h11=2820`, the published values are:

```text
(h0,...,h18) =
(1237530, 930270, 1013430, 163500, 163500, 81750, 160680,
 78930, 321360, 160680, 1410, 2820, 4158, 1410, 2820, 1410,
 1410, 3453, 0).
```

The full witness assigns exactly these counts to the aligned canonical masks.
Thus the result is not merely deck-only: it is exactly compatible with one
admissible specialization of all 19 published Hamiltonian formulas.

## Witness and exact replay

SciPy/HiGHS was used only to discover an integer point.  The published witness
contains all 208 canonical masks and counts, including zeros.  The
standard-library checker then independently rebuilds the censuses, masks,
decks, ranks, Hamiltonian alignment, formula values, and verifies:

```text
nonnegative integer class counts: PASS
all 62 deletion equations:        PASS
all 19 Hamiltonian counts:         PASS
sum x_J = binom(99,7):             PASS
positive support size:             105
```

Hostile tests mutate masks, ordering, parameters, deck counts, Hamiltonian
counts, integer types, and completeness.  All 15 tests pass, and each malformed
witness is rejected.

## Retained failures

The route ledger retains:

- the initial `importlib`/`dataclass` harness crash caused by omitting
  `sys.modules`;
- a 120-second SymPy HNF timeout and a later manually terminated HNF run;
- modular ranks `48,57,61,61` with no restriction on `t=n3/3` for
  `p=2,3,5,7`;
- a false HiGHS infeasibility report caused by an arbitrary objective plus a
  redundant, badly scaled total-count row.

The last failure is directly refuted by the exact witness.  Solver status was
never treated as a certificate.

## Scope wall

The count vector does not assign types consistently to overlapping subsets,
does not impose every higher-order compatibility condition, and does not encode
a `99 x 99` adjacency matrix.  Its only conclusion is:

> The encoded complete order-seven deletion-deck necessary conditions,
> together with the aligned published Hamiltonian formulas at
> `n3=705,h11=2820`, are feasible.

Target status remains `UNKNOWN`.  Novelty is not assessed.
