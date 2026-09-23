# Wave 29 `S0` literature and status audit

## Outcome

**Conservative literature verdict:** `NO_EXACT_PRIOR_RESULT_FOUND_IN_SEARCHED_SOURCES`.

The exact statement was frozen in `protocol-freeze.md` before searching. Across
81 query strings and 16 retained primary or authoritative source records, I
found no paper, preprint, catalogue entry, or institutional record that states
the exact exclusion of

```text
S0 = K12 orthogonal_sum LAMBDA(F)
```

from the full Wave-29 projector/Schur endpoint package. I also found no source
with the identifying combined proof signature

```text
231 rows -> 63+168
det(Q_K),det(Q_L) = 5,1
det(B_K),det(B_L) = 3645,1
tr(B_K),tr(B_L) = 24,36
characteristic-pseudodeterminant integrality
det(B_K) <= 3^6 = 729 < 3645.
```

This is a search result, **not** a proof of novelty. The novelty label remains
`UNKNOWN`.

Recent sources inspected in this run still formulate existence of
`srg(99,14,1,2)` as unresolved or as a problem being approached rather than
resolved. The strongest source is Cesarz--Woldar (2025), whose publisher
abstract explicitly calls existence an open problem. Keramatipour's
arXiv:2604.23037v2 (April 2026) reports that its SAT experiments do not solve
the problem in reasonable time. A June 2026 institutional seminar announcement
likewise describes only a possible analogous approach after a result for the
different parameters `(85,14,3,2)`. No resolution was found, but finite
literature search cannot certify global openness. Accordingly, the broader
Conway-99 status remains `UNKNOWN` in this repository.

## Claim wall

| Claim | Literature disposition | Reason |
|---|---|---|
| Exact `S0` full-endpoint exclusion appears in prior art | `NO_MATCH_FOUND` | None of the searched object-pair, numeric, endpoint-equation, or obstruction queries returned it. |
| Exact result is novel | `UNKNOWN` | Search coverage is finite and terminology/indexing dependent. |
| Individual lattice invariants and provenance | `CITED` | Nebe--Sloane catalogue plus Conway--Sloane and Koch--Venkov sources. |
| Tight-frame, spherical-design, and even-unimodular rank ingredients | `CITED_STANDARD_INGREDIENTS` | Established in general literature; not evidence that the candidate combination is known. |
| Characteristic-pseudodeterminant definition/integrality mechanism | `CITED_STANDARD_INGREDIENT` | General pseudodeterminant literature supplies the definition; the candidate's use and log bound were not found. |
| Local candidate proof is mathematically correct | `OUTSIDE_THIS_ROLE` | The separate verifier package records its own verdict; this literature agent did not promote or re-verify the proof. |
| All determinant-729 rank-44 forms are excluded | `UNKNOWN` | The candidate and this audit concern one exact direct sum only. |
| `n3 >= 709` or nonexistence of `srg(99,14,1,2)` | `UNKNOWN` | Neither follows from excluding one endpoint lattice. |

## Exact-result search

The search deliberately used several families of alternate language:

- `K12`, `K_12`, Coxeter--Todd, `KV32F`, `LAMBDA(F)`, Koch--Venkov,
  direct sum, orthogonal sum, rank 44, and determinant 729;
- the numerical fingerprints `231`, `63`, `168`, `3645`, `729`, and traces
  `24` and `36`;
- Conway 99, `srg(99,14,1,2)`, projector, tight frame, Euclidean
  representation, Hadamard/Schur square, and endpoint equations such as
  `M^2=21M`;
- characteristic pseudodeterminants, integral characteristic polynomials,
  `det(I+2C)`, determinant-versus-trace bounds, and the final logarithmic
  inequality;
- English, German, and French object aliases.

No exact result was found. Two false-positive classes were specifically
discarded:

1. biological uses of “K-12”; and
2. an unrelated Kramer--Mesner design calculation with a `63 x 168` system on
   231 vertices.

The arXiv API exact searches for the object pair and for Conway-99 plus lattice
language returned zero indexed records. OpenAlex returned zero for three exact
cross-checks. These zero counts document index behavior only; they are not
mathematical or novelty certificates.

## What is standard and what was not found

### Standard, separately sourced ingredients

1. **The two lattice objects.** The Nebe--Sloane catalogue records `K12` as a
   12-dimensional integral 3-modular lattice of determinant 729 and minimum 4,
   and `LAMBDA(F)` as a 32-dimensional unimodular lattice of determinant 1 and
   minimum 4. Conway--Sloane and Koch--Venkov provide the historical/primary
   provenance. These sources do not state the direct-sum endpoint exclusion.

2. **Spherical design and tight-frame language.** Delsarte--Goethals--Seidel,
   Benedetto--Fickus, and Nebe's Venkov survey establish the general
   spherical-design, lattice-shell, and tight-frame background. None supplies
   the `63/168` split or candidate endpoint arithmetic.

3. **The rank-12 even-unimodular veto.** The Milgram signature formula is
   classical; Taylor's exposition gives a current accessible source for the
   signature modulo eight mechanism. A positive-definite even unimodular
   lattice must have rank divisible by eight, so rank 12 is impossible. This
   ingredient is standard.

4. **Characteristic pseudodeterminants.** Martin--Maxwell--Reiner--Wilson
   define the pseudodeterminant via the last nonzero coefficient of the
   characteristic polynomial and develop general identities. For an integral
   matrix, integrality of characteristic-polynomial coefficients is elementary.
   No source was found for the candidate's exact pointwise log inequality or
   for its application producing the cap `729`.

5. **AM--GM and elementary determinant/trace facts.** These are standard and
   need no novelty claim.

### Combined features for which no prior source was found

- deriving the exact `63+168` row allocation from the minimum-four direct sum
  inside this full endpoint;
- forcing block determinants `5/1` and `3645/1`;
- forcing block traces `24/36` by the multiple-of-six residue plus AM--GM;
- applying characteristic-pseudodeterminant integrality to
  `C_K=(B_K-I_12)/2`;
- the displayed logarithmic inequality and the contradiction
  `3645 > 729`;
- the entire chain as an exclusion of only `K12 orthogonal_sum LAMBDA(F)`.

The absence of a found source for these combined features is the sole basis for
the `NO_MATCH_FOUND` disposition. It does not turn them into externally
verified novelty.

## Target-status audit

The most probative inspected status records were:

- Cesarz and Woldar, *On the automorphism group of a putative Conway
  99-graph*, Algebraic Combinatorics 8(2), 2025, DOI
  `10.5802/alco.418`: the publisher abstract explicitly says existence remains
  an open problem.
- Ali Keramatipour, *Approaching the Conway-99 problem using SAT solvers*,
  arXiv:2604.23037v2, revised 28 April 2026: the primary record describes
  unsuccessful computational experiments, not a proof.
- Reimbay Reimbayev, arXiv:2409.10620v1 and arXiv:2508.03377v2: these study
  hexagons and order-six subgraphs in the wider parameter family, not graph
  existence/nonexistence.
- Petro and Phillips, arXiv:2502.17845v1: this applies clique-graph methods to
  the existence problem among other examples, without a resolution claim in
  the inspected abstract.
- Hebei Normal University seminar announcement, 24 June 2026: it reports a
  nonexistence approach for the different graph `srg(85,14,3,2)` and says only
  that a possible similar approach to Conway's graph will be discussed.

Thus, **no source searched through 2026-07-24 reported a resolution**. Since
unindexed, unpublished, newly posted, non-English, or inaccessible work may
exist, this audit does not upgrade “no resolution found” to a global proof that
the problem is open.

## Coverage and limitations

- Search date: 2026-07-24 UTC.
- Logged searches: 81 query strings in 21 batches: 68 general web, 3
  OpenAlex, 2 Crossref, and 8 arXiv API.
- Retained source records: 16.
- Crossref rate-limited one query with HTTP 429.
- Direct API URLs were rejected by the web safe-open layer; the same read-only
  OpenAlex/Crossref searches were run without retaining responses.
- Google Scholar, MathSciNet, and zbMATH were not comprehensively
  machine-audited in this run.
- Search snippets were used for discovery only. Substantive claims above rely
  on inspected publisher, DOI, arXiv, institutional, author-catalogue, or
  original-paper metadata.
- No PDF, raw HTML, raw API response, or copyrighted full text was saved.
- No automorphism, symmetry, or other hidden restriction was imposed on the
  frozen mathematical statement. The restriction is explicit: this is one
  `S`-form within the full endpoint equations.

## Final verdict

> No exact prior result was found in the sources searched as of 2026-07-24.

That supports recording the Wave-29 result as an **apparently unlocated exact
combination pending specialist review**, not as “proved novel.” The appropriate
repository labels are:

```text
exact prior-art match: NO_MATCH_FOUND
novelty: UNKNOWN
recent target status: NO_RESOLUTION_FOUND_IN_SEARCHED_SOURCES
broader Conway-99 claim: UNKNOWN
```
