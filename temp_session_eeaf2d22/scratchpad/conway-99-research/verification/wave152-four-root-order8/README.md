# Wave152 clean-room verification

## Verdict

`VERIFIED`: the sealed Wave150 count pseudowitness is exactly separated by
the four-root covariance test. The independently reconstructed centered
blocks for root masks 3 and 12 have exact negative integer-vector quadratic
values, so each is non-PSD.

This refutes only that one pseudowitness. It is **not** an endpoint
infeasibility certificate, does not improve the strict upper bound, and does
not resolve Conway-99.

## Key values

- Flag-family sizes: `224, 201, 155, 99, 69, 178, 125, 60, 70`.
- Reconstructed \(x_6\) SHA-256:
  `f6c8adc240488d97b77bd92d136d0d79ecff0ddb7f6db693352563829d53b40a`.
- Root mask 3:
  `v^T B v = -2293145527521819747490560`.
- Root mask 12:
  `v^T B v = -8605517548253993047296`.
- Semantic result SHA-256:
  `2ae3dd5f58f5743aac81ea51fda148bcbe9a2ecc28bb737b18413321964b37e1`.

## Reproduce

From the repository root:

```powershell
.\.venv\Scripts\python.exe -B verification\wave152-four-root-order8\independent_verify.py --verify verification\wave152-four-root-order8\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover -s verification\wave152-four-root-order8 -p "test_*.py" -v
```

The verifier hashes the discovery program but never imports or executes it.
Its count reconstruction, flag enumeration, moment accumulation, and
certificate arithmetic are separately implemented with the Python standard
library.

## Artifacts

- `protocol.md`: frozen inputs, scope, separation, and memory boundary.
- `derivation.md`: definitions and exact proof.
- `independent_verify.py`: clean-room enumerator and verifier.
- `independent-results.json`: full universes, hashes, totals, and certificates.
- `test_independent_verify.py`: 11 exact and hostile regression tests.
- `run-report.yaml`: reproducibility record.
- `package-manifest.sha256`: verifier package seal.
