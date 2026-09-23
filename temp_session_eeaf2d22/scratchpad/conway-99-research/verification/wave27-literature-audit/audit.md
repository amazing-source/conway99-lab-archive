# Wave 27 proof-separated literature audit

Base audit cutoff: 2026-07-24T00:50:00Z  
Late A20 addendum cutoff: 2026-07-24T01:02:00Z  
Frozen repository commit: `2ac11809fafee7ab752965ae49a96e922859b5ee`  
Literature role only; no proof claim is promoted here.

## Bottom line

- **Conway-99:** the best qualifying evidence found still treats
  `srg(99,14,1,2)` as open. A 2025 peer-reviewed paper says explicitly that
  existence is unknown, and a 2026 primary preprint still approaches the
  problem computationally without resolving it. No construction or
  impossibility proof appeared in the bounded search.
- **E6 trace/parity optimization:** no source in the frozen result sets states
  the unrestricted minimum
  `min tr(E6 Q)=14` under the Wave 27 hypotheses, or its equality witness.
- **E6/A6 frames and cubic tensors:** no source in the frozen result sets
  studies the rank-six lattice frame, the scale-21 second moment, its affine
  cubic parity coset, or the Wave 27 orthogonal-summand obstructions.
- **A20 trace exclusion:** a separately frozen late addendum found only
  conceptual precedent for the standard `A_n` Cartan matrix, not for the
  trace bound or its use to exclude an orthogonal `A20` summand.
- **Rank-44 comparison:** no source directly compares
  `E8^4 orthogonal_sum E6^2` with
  `E8^5 orthogonal_sum A2^2`. Standard lattice tables support the component
  data from which the comparison below is derived.
- **Novelty/priority:** **UNKNOWN**. Bounded non-discovery is not evidence of
  novelty.

The correction in `protocol-correction.md` is active throughout:
`21E6^{-1}` means twenty-one times the inverse. It never means a factor-two
scaled inverse.

## Coverage

The base audit executed all 45 frozen service-query pairs plus the five
corrective `R00` pairs:

| service | frozen | corrective `R00` | usable responses | inspected records |
|---|---:|---:|---:|---:|
| Crossref | 10 | 1 | 11 | 110 |
| OpenAlex | 10 | 1 | 11 | 46 |
| zbMATH Open | 10 | 1 | 2; nine documented 404 failures | 6 |
| arXiv | 5 | 1 | 6 | 1 |
| general web | 10 | 1 | 11 | 100 |
| **total** | **45** | **5** | **41 usable; 9 failed** | **263** |

The general-web wrapper's first batched output did not preserve reliable
per-query attribution, so the same eleven exact queries were replayed
individually. Thus there were 61 network executions for 50 unique
service-query pairs. The replay did not expand a query beyond its first
result page or the ten-record review cap. See `failures.md`.

A late, separately frozen A20 addendum added six service-query pairs:
Crossref and OpenAlex once each, zbMATH once, and three general-web queries.
It inspected 40 records; five responses were usable and the zbMATH request
failed with the same documented 404 behavior. Combined coverage is therefore
56 unique service-query pairs, 303 inspected records, and 67 discovery-query
executions. Candidate-authentication reads are not counted as discovery
queries.

## Theme findings

### A. Conway-99

**Classification: EXACT for the cited open-status statement; no resolution
found.**

Ibrahim, LaFayette, and McCall (2025) explicitly write that it is unknown
whether an `srg(99,14,1,2)` exists. Keramatipour's April 2026 preprint still
frames the task as an existence problem and reports that the tested SAT
approach cannot traverse it in reasonable time. Brouwer's authoritative SRG
table marks the parameter row with `?`. Reimbayev (2024), Cesarz--Woldar
(2025), and Crnkovic--Maksimovic (2020) give structural restrictions or
conditional consequences, not a graph or a nonexistence proof.

This supports the restrained statement:

```text
current qualifying literature located by this audit:
Conway-99 remains unresolved
```

It does not certify that no unindexed or later result exists.

### B. E6 integral optimization

**Classification: BOUNDED NON-DISCOVERY.**

No qualifying record states or studies

```text
Q symmetric, even integral, positive definite
E6 Q congruent to I modulo 2
minimize tr(E6 Q),
```

and no qualifying record gives the Wave 27 trace-14 witness. Crossref C04
and OpenAlex O04 were lexical false positives; arXiv X02 returned zero;
zbMATH Z04 failed at the live endpoint. The corrective exact-21 searches
also yielded no qualifying record.

### C. E6 frames and cubic tensors

**Classification: BOUNDED NON-DISCOVERY.**

No qualifying source connects the rank-six `E6` root lattice to all of:

```text
sum_i z_i z_i^T = 21 E6^{-1},
P_abc = sum_i z_ia z_ib z_ic,
P_aab congruent to (21 E6^{-1})_ab modulo 2,
```

or to the claimed cubic-energy floor and orthogonal-summand obstruction.
The O05 tight-frame candidate concerns quaternionic mutually unbiased bases
in `H^2`, not the `E6` lattice. General-web cubic hits concern the
27-dimensional representation/Jordan cubic of the Lie group `E6`; that is a
different object and is not overlap.

### D. A6 analogue

**Classification: BOUNDED NON-DISCOVERY.**

No qualifying source states the scale-21 `A6` frame parity coset, the
rank-six symmetric-cubic enumeration, or the Wave 27 `A6` orthogonal-summand
obstruction. Crossref C07--C08 and OpenAlex O07 were false positives;
OpenAlex O08 and arXiv X04 returned zero; zbMATH Z07--Z08 failed.

### E. `E8^4 + E6^2` versus `E8^5 + A2^2`

**Classification: CONCEPTUAL component precedent; exact comparison is a
BOUNDED NON-DISCOVERY.**

The Nebe--Sloane catalogue gives:

| lattice | rank | determinant | minimum | norm-two vectors |
|---|---:|---:|---:|---:|
| `E8` | 8 | 1 | 2 | 240 |
| `E6` | 6 | 3 | 2 | 72 |
| `A2` | 2 | 3 | 2 | 6 |

The catalogue Gram matrices give cyclic order-three discriminant groups
with generator norms `4/3` for `E6` and `2/3` for `A2`, modulo `2Z`.
Therefore the two rank-44 sums both have determinant nine and discriminant
group `(Z/3Z)^2`. Their discriminant quadratic forms are isometric: over
`F3`,

```text
P = [[1, 1],
     [1,-1]]
```

is invertible and

```text
(2/3) ||P x||^2 = (4/3) ||x||^2.
```

Their root counts differ:

```text
E8^4 + E6^2: 4*240 + 2*72 = 1104
E8^5 + A2^2: 5*240 + 2*6  = 1212.
```

Thus discriminant data do not distinguish the two sums, while the
norm-two coefficient does. This paragraph is **DERIVED** from the cited
standard tables; no direct paper making this exact comparison was found.

### F. Late A20 trace addendum

**Classification: CONCEPTUAL component precedent; exact identity and use are
a BOUNDED NON-DISCOVERY.**

The six addendum queries found no source stating the Wave 27 identity, its
lower bound, or its use against an orthogonal `A20` summand. Chattopadhyaya
and Manschot (2026) display the standard `A_n` Cartan matrix, with diagonal
entries 2 and adjacent entries -1. From that standard matrix, direct
coefficient comparison gives

```text
tr(A_n Q)
  = Q(e_1) + Q(e_n)
    + sum_(i=1)^(n-1) Q(e_i-e_(i+1)).
```

If `Q` is positive definite, even, and integral, each of the `n+1`
displayed nonzero-vector values is a positive even integer. Hence the
right-hand side is at least `2(n+1)`, and at `n=20` it is at least 42.
This derivation is elementary **DERIVED** overlap from standard Cartan data,
not a located citation for the full Wave 27 argument. The separately
inspected local addendum applies it to an orthogonal-summand exclusion; no
exact or near-direct literature precedent was found. Novelty remains
`UNKNOWN`.

## Overlap with Wave 27 artifacts

The literature map was fixed before these artifacts were opened.

| Wave 27 artifact claim | literature overlap assessment |
|---|---|
| Explicit `E8^4 + E6^2` arithmetic hostile control and absence of an orthogonal `A2` component | Standard component data are CONCEPTUAL precedent. No direct source for the full package or exact hostile-control use was found. |
| Unrestricted local `E6` trace minimum 14 and equality witness | No exact or near-direct precedent found in the bounded search. |
| Doubled `E6`/`A2` discriminant-form isometry and root-count distinction | DERIVABLE from standard tables; no source directly comparing the two rank-44 sums was found. |
| Scale-21 `E6`/`A6` frame parity and cubic-tensor floors | No exact or near-direct precedent found. Lie-group `E6` cubic tensors are a different representation-theoretic object. |
| Exclusion of orthogonal `E6` or `A6` summands from a projector/Schur origin | No exact or near-direct precedent found. |
| `tr(A_n Q)>=2(n+1)` and the orthogonal `A20` exclusion | The standard `A_n` Cartan matrix is CONCEPTUAL precedent and makes the identity directly derivable. No exact or near-direct source for the bound or Wave 27 summand use was found. |
| Conway-99 and novelty remain `UNKNOWN` | Consistent with the qualifying literature and with this audit's status wall. |

This is an overlap classification, not a proof audit. At inspection, the
local trace theorem and the explicit hostile control had independent scoped
verification artifacts; the general root-tensor report was labelled
`DERIVED` with a separate verifier in progress. No literature status is
used to upgrade any mathematical claim.

The late artifact
`agents/2026-07-24-wave27-a20-trace-addendum.md`
(SHA-256
`97c7296752e0ef2126bd8da50cdf8b0abe07b3c72a939233d15aae6d7c413659`)
was opened only after the A20 addendum search map was fixed. It labels its
own A20 result `DERIVED`; this literature audit does not promote that label.

## Publication-safe wording

Safe:

> A frozen search across Crossref, OpenAlex, zbMATH Open, arXiv, and a
> general web index found no direct precedent for the Wave 27 trace,
> scale-21 frame-parity, cubic-tensor, A20 summand, or exact rank-44
> comparison claims. Standard lattice data cover the component invariants
> and the `A_n` Cartan matrix. Novelty remains unknown.

Unsafe:

> These claims are new, first, or absent from the literature.
