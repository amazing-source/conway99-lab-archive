# Wave 190 residual-stability package

This package freezes the proof-B derivation of the conditional circuit bound

```text
Q>=5544
```

from combined raw-extraction and checkerboard-residual capacity in exact-three
companion orbits.

The mathematical report is
`agents/2026-07-29-wave190-residual-stability-proof-b.md`.  The exact checker
verifies the coefficient certificate and a sharp integer relaxation row.

Run:

```powershell
python -B attempts/wave190-residual-stability-proof-b/exact_check.py
python -B -m unittest -v attempts/wave190-residual-stability-proof-b/test_exact_check.py
```

Status is `DERIVED`, not `VERIFIED`.
