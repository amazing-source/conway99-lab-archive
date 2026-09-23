# Wave 37 proof-producing endpoint formula

Status: `CANDIDATE_FORMULA_ONLY`; satisfiability, the endpoint, and Conway-99
remain `UNKNOWN`.

This package exports one exact OPB branch for a future proof-producing attack
on the conditional prism-free endpoint `n3=4158`. It combines:

- the complete compact rooted SRG encoding;
- all 84 endpoint nonedge units;
- the theorem-forced `N3` normalization;
- refined branch 15, one member of the exact 33-case endpoint-compatible
  cover; and
- all prism clauses derived from the six triangles fixed by parent branch 4.

No automorphism of a completed graph is assumed. The six fixed-triangle clause
families are exact consequences of `P=0`, but they do not enumerate every
possible prism.

## Frozen artifact

```text
refined branch:       15 of 33 endpoint-compatible cases
parent branch:        4
variables:            289,338
ordinary clauses:     568,777
native AtMost:          5,838
OPB constraints:      574,615
raw bytes:         29,827,704
raw SHA-256:        4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5
gzip bytes:          3,854,306
gzip SHA-256:       7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e
```

The deterministic gzip round trip reproduces the raw OPB byte for byte. The
raw file is intentionally not published in ordinary Git; regenerate it with
the exporter or decompress `branch-15.opb.gz`.

The pinned Exact binary accepted the formula with `--onlyparse`. That is a
syntax result, not a SAT or UNSAT result.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B attempts\wave37-proof-producing-endpoint\export_endpoint_opb.py `
  --refined-branch 15 `
  --opb attempts\wave37-proof-producing-endpoint\branch-15.opb `
  --metadata attempts\wave37-proof-producing-endpoint\branch-15-formula.json

.\.venv\Scripts\python.exe -B attempts\wave37-proof-producing-endpoint\audit_opb.py `
  --opb attempts\wave37-proof-producing-endpoint\branch-15.opb `
  --metadata attempts\wave37-proof-producing-endpoint\branch-15-formula.json `
  --output attempts\wave37-proof-producing-endpoint\branch-15-opb-audit.json

.\.venv\Scripts\python.exe -B attempts\wave37-proof-producing-endpoint\package_opb.py `
  --source attempts\wave37-proof-producing-endpoint\branch-15.opb `
  --output attempts\wave37-proof-producing-endpoint\branch-15.opb.gz `
  --audit attempts\wave37-proof-producing-endpoint\compression-audit.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave37-proof-producing-endpoint -p "test_*.py" -v
```

With the pinned Exact tool installed at the path documented by the calibration:

```bash
PROJECT_WSL="/mnt/c/path/to/conway-99-research"
EXACT="/absolute/path/to/pinned/Exact"
FORMULA="$PROJECT_WSL/attempts/wave37-proof-producing-endpoint/branch-15.opb"
"$EXACT" --onlyparse "$FORMULA"
```

## Promotion boundary

An apparent `UNSAT` result is worthless unless a retained proof is replayed
independently by the pinned VeriPB and CakePB pipeline. An apparent `SAT`
result must be decoded and checked as a complete 99-vertex SRG and as
prism-free. Even a checked `UNSAT` result for this file would close only one
of 33 refined endpoint cases.
