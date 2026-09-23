# Wave 42 canonical joint-incidence verification

Status: **VERIFIED scoped conditional reduction**.  This is not a full
incidence completion, an outside graph, endpoint exclusion, upper-bound
improvement, Conway-99 solution, or novelty claim.

The verifier was frozen before comparison and uses only Python's standard
library.  From the independently verified Wave 41 mask-51739 record it
reconstructs:

- the rank-33 triangle block and its cubic, triangle-free 36-vertex core;
- core components of orders 12 and 24, balanced 4+8 in each fibre;
- the exact required Gram matrix `Q=B B^T`;
- Cauchy equality forcing every hypothetical outside block to meet the small
  component in exactly two vertices;
- all 60 nonmatching pairs in every fibre and their exact once-only use;
- component-pattern multiplicities `4,4,4,16,16,16`;
- the exhaustive six-set census
  `216000 -> 118718 -> 49736 -> 45032`;
- necessary outside-column overlaps `458/1004/308`, outside-graph edge
  overlaps `96/144/0`, 32 triangles, and 181 four-cycles.

`two-fibre-certificate.json` is an independently generated positive
concurrence certificate.  It proves only that one two-fibre projection is
feasible.  It is distinct from, and independently validates alongside, the
discovery certificate.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave42-joint-incidence\independent_check.py `
  --output verification\wave42-joint-incidence\independent-results.json `
  --certificate verification\wave42-joint-incidence\two-fibre-certificate.json `
  --verify

.\.venv\Scripts\python.exe -B `
  verification\wave42-joint-incidence\comparison_check.py `
  --output verification\wave42-joint-incidence\comparison.json `
  --verify

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave42-joint-incidence -p "test_*.py" -v
```

