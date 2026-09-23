# Wave 189 degree-seven star package

This is the frozen proof-B source package for two conditional rank-11
endpoint statements:

1. the exact one-star complete degree-seven relaxation remains feasible, so
   Wave 187's negative `B_(7,0)` was witness-specific; and
2. analytic companion-orbit packing plus equality-face cancellation gives
   the `DERIVED` circuit bound `Q>=4852`.

The full mathematical account is in
`agents/2026-07-29-wave189-degree7-star-complete-proof-b.md`.  A compact
source derivation is in `derivation.md`.  `exact_check.py` independently
recomputes every reported rational transform, moment, polygon lift, scalar
packing identity, and cancellation profile using only the Python standard
library.

Run:

```powershell
python -B attempts/wave189-degree7-star-complete/exact_check.py
python -B -m unittest -v attempts/wave189-degree7-star-complete/test_exact_check.py
```

The package is not a verifier promotion.  Its status remains `DERIVED`
until a clean-room verifier freezes and audits the source.
