# Wave 56 independent verification

Status: `VERIFIED` for the exact conditional scope in `audit.md`.

The checker independently reconstructs the closure parameter census, small
control graphs, 64 four-tip labelings, 23 endpoint masks, 35 exact local
profiles, and 11 formal `D4` label-orbits. It also attacks the incidence
multiplicities behind

```text
n3+3P=4158, R=18H, 6H<=P, R<=3P, S>=n3.
```

No full graph, endpoint contradiction, strict `n3` upper bound, or
completability claim follows.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave56-percolation-closure -p "test_*.py" -v

.\.venv\Scripts\python.exe -B `
  verification\wave56-percolation-closure\independent_check.py `
  --discovery attempts\wave56-percolation-closure\exact-results.json `
  --verify-output verification\wave56-percolation-closure\independent-result.json
```

