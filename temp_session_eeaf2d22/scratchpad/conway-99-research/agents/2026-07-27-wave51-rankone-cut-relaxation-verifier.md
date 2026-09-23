# Wave51 fixed rank-one relaxation clean-room verifier

```yaml
role: verifier
date_utc: 2026-07-27T19:18:35Z
git_commit: 7a77446e8f1aa163170ff91e3b5068482603898b
claim_label: VERIFIED
scope: exact rational feasibility of the fixed 170-equation, 174-cut Wave51 relaxation
inputs: verification/wave51-rankone-cut-relaxation-independent/input-freeze.sha256
method: clean-room cut reconstruction, exact fraction substitution, and exact modular rank certification
command: .\.venv\Scripts\python.exe verification\wave51-rankone-cut-relaxation-independent\verify.py --compute
outputs: verification/wave51-rankone-cut-relaxation-independent/verification-result.json
limitations: fixed rational aggregate relaxation only; full PSD, integrality, graph, endpoint, and Conway-99 remain UNKNOWN
```

The source package did not satisfy discovery/verifier separation: one agent
selected the 174-cut bundle, constructed the witness, replayed it, and labeled
its own result `VERIFIED`/`VERIFIED_SCOPED`. I treated that source chronology
as `CANDIDATE`, recorded the defect, and did not edit the source.

The clean-room replay independently rebuilt all 170 Wave44 equations, checked
all 17 Wave45 cut self-hashes, attacked the full 2,657-cut Wave47 ledger and
its 136-cut selection, and recomputed all 21 Wave49 cuts from sealed integer
directions and independently verified coefficient tensors. The Wave49 replay
performed 5,691 exact quadratic checks. The source probe and numerical solver
were not imported.

The exact rational witness passes all 170 equations and 174 cuts. It has
support 136, `h11/4=4158`, 66 tight cuts split `5/46/15`, minimum positive
slack `133056`, and maximum denominator length 272 digits. Its active
coefficient matrix has rank 209, independently certified by exact elimination
modulo `2147483647`.

Thus the fixed finite bundle is exactly feasible and cannot supply a Farkas
infeasibility contradiction. This does not verify omitted cuts, the full PSD
system, integer feasibility, an endpoint graph, a strict upper bound, or
Conway-99. Those claims remain `UNKNOWN`.
