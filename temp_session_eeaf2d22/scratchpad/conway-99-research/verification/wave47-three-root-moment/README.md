# Wave 47 independent three-root moment verification

This directory contains a clean-room, self-contained verifier for the sealed
Wave 47 three-labelled-root moment package.  It reads the sealed data
artifacts but does not import or execute any discovery implementation.

The full replay enumerates all locally admissible labelled graphs through
order seven, removes complete vertex-permutation orbits, constructs all eight
pointwise-labelled root families, verifies exact Petersen and Clebsch direct
Gram controls, reconstructs all 17 immutable seven-count witnesses, evaluates
all 2,664 supplied integer negative directions, and exactly compares all
2,657 deduplicated primitive cuts.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe verification\wave47-three-root-moment\verify.py
.\.venv\Scripts\python.exe -m unittest verification\wave47-three-root-moment\test_verify.py -v
.\.venv\Scripts\python.exe verification\wave47-three-root-moment\verify.py --validate verification\wave47-three-root-moment\verification-results.json
```

The verifier enforces a 20% free-physical-memory floor at every substantive
phase boundary.

The only permitted verdict is scoped: exact finite reconstruction may be
`VERIFIED_SCOPED`, while endpoint feasibility, a strict upper bound,
graph construction, and Conway-99 remain `UNKNOWN` or `NOT_PROVED`.
