# Wave 43 branch-15 two-triangle verifier

Status: `VERIFIED_SCOPED`. Branch 15, the prism-free endpoint, and Conway-99
remain `UNKNOWN`; checked endpoint coverage remains `0/33`.

This clean-room implementation imports no Wave 43 discovery module. It binds
the frozen Wave 37 and Wave 42 inputs, independently replays generalized-unit
closure, reconstructs the rooted coordinate-triangle catalogue, visits every
pair and matching in the stated restricted family, and compares complete raw
and active OPB clause streams.

The exact reproduced census is:

```text
coordinate triangles:             924 = 7 true + 157 false + 760 unfixed
unfixed pairs:                 288,420
vertex-disjoint pairs:         259,499
mate-anchor disjoint pairs:     20,400
matching visits:             1,556,994
accepted distinct cuts:         40,800
active after closure:            34,340
satisfied by closure:             6,460
```

The checker also independently replayed the same deterministically selected
32 controller variables in both polarities. All 64 complete pass and
derivation records match exactly: there is no failed polarity, implication,
contradiction, or derivation sourced by the Wave 43 cuts.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave43-branch15-two-triangle\independent_check.py `
  --verify verification\wave43-branch15-two-triangle\independent-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave43-branch15-two-triangle -p "test_*.py" -v
```

Completeness is restricted to pairs of coordinate-anchored triangles whose
controllers are unfixed at the frozen Wave 42 closure. Triangles without a
coordinate anchor are not covered. A propagation fixed point is neither a
SAT witness nor an UNSAT certificate, and no completed-graph automorphism is
assumed.
