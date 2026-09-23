# Wave 51 independent verifier

This package independently reconstructs the conditional Seidel Smith form,
mod-7 Jordan type, and symmetric-square rank bound.

The corrected structural result is `VERIFIED`, but one discovery statement is
`REFUTED`: the multiplicities of \(+7\) and \(-7\) in the rational spectrum
were reversed. The correct spectrum is
\[
-70^1,+7^{54},-7^{44}.
\]
The correction leaves the absolute determinant and all verified structural
consequences unchanged.

The graph endpoint remains `UNKNOWN`. All ranks \(28,\ldots,44\) survive.

## Reproduce

From this directory:

```powershell
python independent_check.py --verify
python comparison_check.py --verify
python -m unittest -v test_independent_check.py
```

The checker uses standard-library exact integer and finite-field arithmetic
and enforces the 15% free-physical-memory floor.

## Files

- `protocol.md`: frozen scope and verifier separation.
- `input-freeze.sha256`: hashes of all received inputs.
- `independent_check.py`: reconstruction written without importing discovery
  code.
- `independent-result.json`: canonical independent artifact.
- `comparison_check.py` and `comparison.json`: byte-frozen comparison.
- `test_independent_check.py`: hostile and regression tests.
- `audit.md`: mathematical proof, correction, and limitations.
- `run-report.yaml`: reproducibility metadata.
- `package-manifest.sha256`: verifier package hashes.

