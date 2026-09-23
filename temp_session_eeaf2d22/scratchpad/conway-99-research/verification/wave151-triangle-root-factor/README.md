# Wave151 clean-room verification

## Verdict

`VERIFIED_PARTIAL_CONSTRUCTION_UNKNOWN_FULL`.

The stored \(Q_1\) independently reconstructs an exact binary
\(24\times60\) factor for the frozen Wave149 `G00`, `G11`, and `G01`
blocks. Every row has weight 10 and every column has two ones in each
12-row group.

The complete \(36\times60\) factor \(C\) and residual adjacency block \(D\)
remain `UNKNOWN`.

## Evidence boundary

- The fixed-\(Q_1\) model independently has 1,620 allowed Boolean mappings.
- Its stored `unsat` status has no exported proof and is only an
  `UNVERIFIED_SOLVER_DIAGNOSTIC`.
- The retained \(Q_2\) candidate has exact residual \(40+40=80\), so it is
  not a third-group construction.
- The unrestricted score 108 has no stored permutations and cannot be
  replayed.

## Exact hashes

- Binary \(24\times60\) factor:
  `11dd68b64c237e6d45e221e8910b3da69e9492dd01aeb697555d874fdab9eed5`
- Partial \(24\times24\) Gram:
  `6d3358e61a802bbca3695cf5ddee6a3ce57493b95cd8613d54d1b4641b4babd3`
- Semantic verification result:
  `538eae68a2ba247be1d2cf0dde999f20506e73b1e5c557640d7b2a1daca90de3`

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B verification\wave151-triangle-root-factor\independent_verify.py --verify verification\wave151-triangle-root-factor\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover -s verification\wave151-triangle-root-factor -p "test_*.py" -v
```

The verifier does not import or execute discovery code.

## Artifacts

- `protocol.md`: frozen inputs and evidence rules.
- `derivation.md`: exact factor and solver-boundary derivation.
- `independent_verify.py`: clean-room verifier.
- `independent-results.json`: full binary matrix and replay hashes.
- `test_independent_verify.py`: 11 exact and hostile tests.
- `run-report.yaml`: reproducibility record.
- `package-manifest.sha256`: verifier package seal.
