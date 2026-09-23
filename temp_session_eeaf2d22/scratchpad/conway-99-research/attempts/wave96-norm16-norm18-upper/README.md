# Wave 96: weighted short-shell C4 squeeze and norm-20 dictionary

Status: `DERIVED` and `UNKNOWN`; independent verification required.

In the prism-free endpoint and rank-28 row, the verified Wave 86 identity
and Wave 99 bound imply

```text
407*N16 + 43*N18 >= 2,165,002.
```

Every antipodal norm-16 support contains at least 20 alternating induced
four-cycles.  The two norm-18 lanes contain at least 18 and 26.  Since the
target has exactly 2,079 induced four-cycles, a universal cap of 25
antipodal norm-16/norm-18 extensions per cycle would give

```text
407*N16 + 43*N18 <= 2,115,382,
```

and close the row.  This package does **not** prove that cap.  In fact, the
fixed-cycle projector plus minimum-distance relaxation admits an exact
80-point cross-polytope, so coordinate projection and spherical distance
alone cannot prove 25.

The package also proves a new conditional dictionary entry:

```text
norm 20 integer -4 eigenvector = ten +1 and ten -1 coordinates.
```

Its support has at most three same-sign edges and at least 15 alternating
four-cycles.  Combined with the verified Wave 101 `q=14` prefix bound, this
would exclude rank 30 if every cycle had at most 24 antipodal short-support
extensions through norm 20.  That local cap is also open.

Reproduce:

```powershell
python -B attempts\wave96-norm16-norm18-upper\exact_check.py
python -B attempts\wave96-norm16-norm18-upper\exact_check.py `
  --verify attempts\wave96-norm16-norm18-upper\exact-results.json
python -B -m unittest discover `
  -s attempts\wave96-norm16-norm18-upper -p "test_*.py" -v
```

No graph nonexistence, rank exclusion, Conway-99 resolution, or novelty
claim is made.
