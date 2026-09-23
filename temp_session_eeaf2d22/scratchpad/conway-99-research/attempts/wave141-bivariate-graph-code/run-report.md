---
role: proof_a
date_utc: 2026-07-28T09:36:33Z
git_commit: 0a15bfe548e301ea98c83e292ba8931322e39945
claim_label: DERIVED
scope: exact bivariate graph-code transform, D8 equality dimension, signed input shells S0 through S6, and a bounded non-evidentiary row-generated numerical scout
inputs:
  - attempts/wave21-six-vertex-lp/exact_check.py sha256=0dd44ca37ca21aeaa757f3b2d7f7f9639907f22b95da39472ed9d836027a94a3
  - attempts/wave21-six-vertex-lp/exact-results.json sha256=5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b
method: exact Krawtchouk/MacWilliams derivation, D8 Burnside trace calculation, independent Wave21 canonical-mask parity replay, exact K3 transform unit, and row-generated floating LP telemetry in input-conditional coordinates
command:
  - python -B attempts/wave141-bivariate-graph-code/exact_check.py --verify
  - python -B -m unittest discover -s attempts/wave141-bivariate-graph-code -p "test_*.py" -v
  - .venv/Scripts/python.exe attempts/wave141-bivariate-graph-code/numeric_scout.py --rounds 3 --add-per-round 30 --time-limit 20 --branches plus-max minus-max --solver-method highs-ds --initial-input-rows 1 --output attempts/wave141-bivariate-graph-code/numeric-scout.json
outputs:
  - attempts/wave141-bivariate-graph-code/exact-results.json sha256=351857e985a871e6d69c5662f90ad5cd6a608f92b1703e84ffb549a753cc8b2e
  - attempts/wave141-bivariate-graph-code/numeric-scout.json sha256=d2c963f089a5819a297a88c16dbc7edcf0448cb8d9f1b97d9734b9f5b3fae00e
limitations:
  - no exact rational primal or dual optimization certificate
  - floating row generation stops at UNKNOWN_NUMERICAL after 80 active transform rows
  - inactive transform residuals remain large at the last floating point
  - no code, adjacency matrix, graph, improved n3 upper bound, or Conway-99 resolution
---

# Wave141 run report

The exact part passes.  Output parity and the bivariate transform generate
`D8`; the 5,000-state output-even space has invariant dimension 1,275 and
equality rank 3,725.  Frozen Wave21 masks and count formulas independently
reproduce

```text
S6 = 2024484 + (512/3)n3.
```

Both bounded floating Arf branches remain `UNKNOWN_NUMERICAL`.  Their first
50-row relaxations maximize the sixth signed row at the trivial
nonnegativity ceiling and badly violate inactive transform rows.  Adding the
30 largest violations produces no floating primal.  No negative inference
is permitted.
