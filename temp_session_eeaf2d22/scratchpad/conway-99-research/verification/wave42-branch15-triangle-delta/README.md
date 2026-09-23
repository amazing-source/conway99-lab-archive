# Wave 42 branch-15 triangle-delta verifier

This package independently checks one exact proof-producing reduction inside
refined endpoint branch 15. It does not decide that branch or Conway-99.

The frozen formula directly forces `x2=1`. In the rooted full graph this edge
joins residual labels `(0,2)` and `(0,4)`, which already share coordinate
vertex `1`; hence full vertices `[1,15,17]` form an additional fixed triangle.

Every triangular prism based at this triangle is forbidden at the prism-free
endpoint. Clean-room enumeration gives:

```text
raw clauses:       64,932 = 132 width-3 + 64,800 width-5
active clauses:    33,778 = 91 width-3 + 580 width-4 + 33,107 width-5
active units:           0
active empty clauses:   0
```

The active census is simplified by a fresh replay of the frozen OPB's
generalized-unit closure, not by trusting the Wave 41 discovery certificate.

Reproduce after `independent-results.json` has been generated:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave42-branch15-triangle-delta\independent_check.py `
  --verify verification\wave42-branch15-triangle-delta\independent-results.json

.\.venv\Scripts\python.exe -B `
  verification\wave42-branch15-triangle-delta\comparison_check.py `
  --verify verification\wave42-branch15-triangle-delta\comparison.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave42-branch15-triangle-delta -p "test_*.py" -v
```

The comparison was performed only after the clean-room implementation and
result were frozen in `implementation-freeze.sha256`. It parses both discovery
OPB catalogues independently and proves equality of the complete normalized
clause sets, not merely equality of counts.

Status:

```text
triangle-delta reduction: VERIFIED SCOPED
branch 15:                UNKNOWN
endpoint cases closed:    0/33
Conway-99:                UNKNOWN
```
