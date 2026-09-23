# Wave149 clean-room verification

## Verdict

`VERIFIED_SCOPED`: the sealed discovery package's explicit matching witness
survives the first forced Gram/PSD projection and has zero rooted prisms.
Independent integer reconstruction reproduces the discovery matrix exactly,
including its SHA-256, exact spectrum, and rank.

This is **not** a graph construction and **not** a new upper bound. Existence
of the required binary \(36\times60\) incidence factor is `UNKNOWN`; the
compatible residual 60-vertex graph and global compatibility are also
`UNKNOWN`.

## Reproduce

From the repository root:

```powershell
.\.venv\Scripts\python.exe -B verification\wave149-terwilliger-triple\independent_verify.py --verify verification\wave149-terwilliger-triple\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover -s verification\wave149-terwilliger-triple -p "test_*.py" -v
```

The verifier checks the sealed discovery manifest before reading the stored
candidate data. It never imports or executes discovery code.

## Artifacts

- `protocol.md`: frozen verifier scope and separation boundary.
- `derivation.md`: independent mathematical derivation.
- `independent_verify.py`: standard-library exact verifier.
- `independent-results.json`: full matrix and exact certificate.
- `test_independent_verify.py`: replay and hostile-mutation tests.
- `run-report.yaml`: reproducibility record.
- `package-manifest.sha256`: sealed verifier artifact hashes.
