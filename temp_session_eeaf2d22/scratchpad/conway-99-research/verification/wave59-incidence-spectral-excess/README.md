# Wave 59 independent verification

Scoped verdict: `VERIFIED` for the finite conditional incidence, spectral,
distance-layer, predistance, defect, Gram, Ihara--Bass, cycle-count, and cage
claims in sealed Wave 59.

No discovery implementation or test was opened, imported, or executed.
`independent_verifier.py` reconstructs the result from the frozen
`srg(99,14,1,2)` parameters and the explicit prism-free hypothesis using
exact arithmetic. Its post-computation comparison reads only the sealed
`exact-result.json`.

Two metadata-only corrections are recorded: the primary source's official
author spelling is `Miquel Àngel Fiol`, and the statement of Theorem 6 is on
printed page 6 (its proof continues beyond page 7). No mathematical mismatch
was found.

The exact independent result is `independent-result.json`; the full reasoning
and evidence boundary are in `audit.md`; the live primary-source check is in
`source-evidence.json`.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave59-incidence-spectral-excess\independent_verifier.py `
  --compare-discovery `
  attempts\wave59-incidence-spectral-excess\exact-result.json `
  --output `
  verification\wave59-incidence-spectral-excess\independent-result.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave59-incidence-spectral-excess `
  -p "test_*.py" -v
```

The second command passes 14 tests, including exact orthogonalization,
independent Bass-series expansion, relation-order invariance, sealed-result
comparison, and hostile mutations.

Status wall: no endpoint exclusion, construction, strict `n3` upper bound, or
novelty claim follows. Conway-99 and the prism-free endpoint remain `UNKNOWN`.
