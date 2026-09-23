# Wave 59 independent verification protocol

```yaml
role: verifier
date_utc: 2026-07-27T21:18:02Z
git_commit: 4bb1989e9e286b2ec753a855db58ad584e31f63a
claim_label: UNKNOWN
scope: sealed Wave 59 incidence and spectral-excess package; finite graph-theoretic and source-metadata claims only
```

## Pre-inspection claim surface

This protocol was written after hashing the sealed Wave 59 directory but before
reading its claim artifacts. The task-supplied claim surface is:

1. reconstruct the incidence matrix `N` and graphs `L` and `K`, then verify
   their spectra independently;
2. verify connectedness, girth, diameter, distance layers, and the stated
   `B`/`C` split;
3. check every hypothesis used for the spectral-excess theorem and independently
   derive the predistance polynomials;
4. derive the exact `K^2` and `K^3` relation tables and any defect/projection
   norm identities;
5. derive the pair-neighborhood Gram identity and bound;
6. derive the stated Ihara--Bass determinant, nonbacktracking traces, and cycle
   counts;
7. check the cage comparison and the frozen primary-source metadata.

## Clean-room rules

- The discovery implementation `incidence_spectral.py` will not be opened,
  imported, or executed.
- The discovery test implementation `test_incidence_spectral.py` will not be
  opened or executed because it may expose or import discovery internals.
- Discovery prose and recorded outputs are advisory claims, not verification
  evidence.
- All computations will be reimplemented in
  `verification/wave59-incidence-spectral-excess/` from the frozen mathematical
  statement, using exact integer, rational, polynomial, and symbolic arithmetic.
- Every finite equality will be checked from independently constructed objects
  or formulas. Relevant invariance and hostile-mutation checks will be included.
- Source claims will be checked against primary sources, publisher/DOI records,
  or author-hosted originals, with access dates and URLs recorded.
- At least 15 percent physical memory must remain free during computation.

## Status wall

- `VERIFIED` may be assigned only to a precisely scoped, independently
  reproduced finite statement.
- A solver exit code, discovery prose, or agreement with a discovery output is
  not by itself a certificate.
- Any correction is recorded explicitly rather than silently repaired.
- No conclusion in this package promotes the underlying endpoint or the
  existence/nonexistence of the conjectural graph. The endpoint remains
  `UNKNOWN` unless independently resolved elsewhere.

## Reproducibility

The final run report will record exact commands and SHA-256 hashes for all
verifier inputs and outputs. The pre-inspection artifact ledger is
`preinspection-freeze.sha256`.
