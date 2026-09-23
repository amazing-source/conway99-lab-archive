# Wave 60 independent audit

## Verdict

**VERIFIED in exact finite scope; no endpoint promotion.**

The clean implementation reproduces all exact discovery headlines.  No
correction is required to the finite counts.  The finite-field rank route is
confirmed to be redundant, and the bounded construction telemetry remains
properly labelled `UNKNOWN`.

## Reproduced results

- The normalized component census is exactly 216 graphs.
- Exactly 50 pass the graph and sector-aware codegree conditions, with
  labelled four-cycle distribution `2:6, 4:30, 6:14`.
- Complete fibre-preserving canonicalization gives exactly 18 types.
- There are 1,140 unordered type triples.
- Simultaneously relabelling the fixed triangle and all three fibres gives
  exactly 275 coordinate orbits, of sizes `1:15, 3:145, 6:115`.
- No target automorphism is assumed.  The hostile witness
  `(0,1,1) -> (0,1,11)` shows why independently permuting fibres in different
  components would be an invalid stronger quotient.
- The target `F2` rank distribution is exactly
  `14:67, 16:415, 18:412, 20:185, 22:51, 24:10`.
- The necessary alternating-rank ceiling is 30, so the rank filter rejects
  zero triples.
- There are exactly 21 formal column patterns: six `AAA`, nine `ABB`, and six
  `BBB`.
- All 1,140 triples have positive individual column support.  Counts range
  from 15,936 to 27,200.
- For aligned discovery type 4, both the category-product formula and direct
  candidate enumeration give 20,928 columns with all 21 patterns.
- In each component the off-diagonal target multiplicities sum to 60 and
  have row sums 10.  Hence the local pair equations force the omitted global
  60-column equation and all diagonal row equations.
- The aligned marginal ledger obeys
  `x_ABB = 36 - 3*x_AAA`, `x_BBB = 24 + 2*x_AAA`, and
  `0 <= x_AAA <= 12`.  The discovery probes at `x_AAA=0,6,12` are admissible
  ledger choices, not an exhaustive search over all couplings.

## Source and artifact audit

- The preinspection freeze checks 36 discovery/public-input files with zero
  hash failures.
- The discovery package manifest checks 23 entries with zero hash failures.
- Seven discovery tests pass.
- Eight clean-verifier tests pass.
- Directly regenerated JSON is byte-identical to `independent-results.json`.

## Status qualification

The reported local-search best errors (`82` through `104`) and duplicate
counts cannot be independently checked from the sealed artifacts because the
best assignments were not emitted.  This is not a correction to the
discovery status: those files already say `UNKNOWN`, and the values are only
telemetry.

The bounded Glucose artifact says `UNKNOWN`, supplies no design and no proof,
and contains no CNF/proof file.  It is non-evidentiary for either existence or
nonexistence.

## Unresolved boundary

No safe coordinate orbit has been exhausted, no full incidence matrix has
been found, and no component triple has been excluded.  The conditional
`kappa=3` incidence problem, the prism-free endpoint, and Conway-99 all remain
`UNKNOWN`.
