# Wave 57 independent star-complement verification

Status: `REFUTED_IN_PART`.

The quotient, supported eigenspaces, projector ranks, star-set minimum-hit
argument, `Y` moments, four-cycle transfer, 18-row truncated moment ledger,
and all 18 scalar controls were independently reproduced.

Two material corrections are required:

- cubicity gives `C4(X)<=27`, stronger than the reported `<=89`;
- the already verified Wave 36 transfer gives
  `mult_Y(3)=18` and `mult_Y(-4) in {8,9,10}`, so only three endpoint rows
  remain, not 18.

The corrected `Y` target has

```text
rank(11A_Y+44I-2J) in {50,51,52},
rank(-9A_Y+27I+J) = 42.
```

Thus a `3`-star complement inside `Y` has order 42, while a `-4`-star
complement has order 50 to 52.  This remains only a necessary 60-vertex
subproblem; it does not reconstruct the full endpoint.

No graph or binary reconstruction matrix is supplied.  The endpoint and
Conway-99 remain `UNKNOWN`.

## Reproduce

```powershell
python -B verification\wave57-star-complement\independent_check.py
python -B verification\wave57-star-complement\independent_check.py `
  --verify verification\wave57-star-complement\independent-results.json
python -B -m unittest discover `
  -s verification\wave57-star-complement -p "test_*.py" -v
```

The checker uses only standard-library exact arithmetic, imports no discovery
code, verifies the frozen inputs, and refuses to run below 20 percent free
physical memory.

## Files

- `protocol.md`: preinspection questions and promotion rules.
- `preinspection-freeze.sha256`: upstream and project-prior hashes.
- `discovery-freeze.sha256`: sealed Wave 57 discovery hashes.
- `independent_check.py`: clean-room exact verifier.
- `independent-results.json`: machine-readable verdict and corrected ledgers.
- `test_independent_check.py`: baseline plus hostile-mutation tests.
- `audit.md`: mathematical audit, corrections, and chronology.
- `run-report.yaml`: reproducibility record.
- `package-manifest.sha256`: final package checksums.
