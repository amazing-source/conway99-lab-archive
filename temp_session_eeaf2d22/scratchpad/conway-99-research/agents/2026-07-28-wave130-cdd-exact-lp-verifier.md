# Wave130 independent verifier

```yaml
role: verifier
date_utc: 2026-07-28T07:30:29Z
git_commit: aef7b93124f8caeb1a7487f58289436bc4118880
claim_label: VERIFIED
scope: exact rational feasibility of the finite cutoff-28 Jacobi relaxation
inputs:
  - attempts/wave130-cdd-exact-lp/MANIFEST.sha256
method: independent no-cache theta/Eisenstein/Fricke reconstruction and exact row replay
command: python -B verification/wave130-cdd-exact-lp/independent_no_cache_verify.py --verify verification/wave130-cdd-exact-lp/independent-results.json
outputs:
  - verification/wave130-cdd-exact-lp/independent-results.json
limitations:
  - finite necessary-condition feasibility only
  - no graph, lattice, rank realization/exclusion, or Conway-99 resolution
```

The frozen 34-entry discovery seal passed.  A separate implementation rebuilt
all 239 Fourier columns without importing discovery code and without reading
the serialized column cache.  Exact substitution of the sealed rational
primal passed all 454 equalities and all 1,686 inequalities, with exact
agreement on the 506 tight labels.

Promoted result:

```text
cutoff-28 finite Jacobi relaxation: VERIFIED_EXACT_RATIONAL_FEASIBLE
rank-28 realizability:             UNKNOWN
rank-28 exclusion:                 NO
graph/lattice construction:        NO
Conway-99:                          UNKNOWN
```
