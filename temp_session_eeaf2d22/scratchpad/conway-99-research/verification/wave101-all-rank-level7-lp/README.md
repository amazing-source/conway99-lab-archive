# Wave 101 independent all-rank scalar-theta verification

Status: `VERIFIED_WITH_SHARPENING`, scoped.

For each conditional Wave 71 row `q=2,4,...,14`, the verifier independently
reconstructed the complete weight-22 level-seven modular space, exact Fricke
map, rank-dependent Poisson transfer, and every submitted rational
primal/dual LP certificate. All reported total, prefix, triangular, parity,
and mod-seven conclusions match.

The strategically important null also survives: every row has an exact
integral, even, nonnegative first-15-coefficient scalar control with
`x7=x8=x9=0`. Consequently these bounds do not force a vector in the only
range where the graph-specific signed-unit dictionary is proved.

The submitted mod-two upper bounds are valid. The triangular bound can be
tightened by a factor of eight, from

```text
704(2^44-1)
```

to

```text
88(2^44-1).
```

The tighter bound is still far above every scalar LP lower bound, so no rank
row is excluded. Conway-99 and novelty remain `UNKNOWN`.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave101-all-rank-level7-lp\independent_verify.py --verify

.\.venv\Scripts\python.exe -B `
  verification\wave101-all-rank-level7-lp\compare_discovery.py

.\.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave101-all-rank-level7-lp\test_independent_verify.py
```

