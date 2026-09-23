# Wave 110: safe symmetry-reduced motif-extension SAT

Status: sealed discovery package; independent verification required.

This package retains the complete Wave 105 extension equations conditional
on an induced `C4 box K3`. It adds lexicographic ordering only among outside
vertices with identical motif-neighborhood patterns, comparing their
adjacency to vertices outside that pattern class.

A single weighted-potential argument proves that every relabeling orbit has a
representative satisfying all 50 row comparisons simultaneously. This is
encoding symmetry; it assumes no automorphism of an unknown target graph.

The exact submission per branch has

```text
3,741 outside-edge variables
317,985 common-neighbor conjunction variables
4,126 lex-prefix variables
325,852 variables total
978,711 CNF clauses
9,746 native at-most constraints
```

Four sequential 45-second branches, partitioned by the invariant
`e(X0)=0,1,2,3`, all returned `UNKNOWN_TIMEOUT`. The corresponding Wave 105
runs also all timed out, so symmetry breaking produced no solve-status
progress at this budget. Free physical memory remained above 50% throughout.

Reproduce the exact audit and tests:

```powershell
python -B attempts\wave110-c4boxk3-symmetry-sat\symmetry_sat.py `
  --audit
python -B -m unittest discover `
  -s attempts\wave110-c4boxk3-symmetry-sat -p "test_*.py" -v
```

Run one bounded branch:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave110-c4boxk3-symmetry-sat\symmetry_sat.py `
  --solve-seconds 45 --branch-eX0 0
```

Timeouts and uncertified UNSAT exits remain `UNKNOWN`. Any SAT graph is
directly checked against `A^2=12I-A+2J` before it can be emitted.
