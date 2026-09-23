# Wave 131 independent verification

Verdict: `VERIFIED_SCOPED_RATIONAL`.

A clean-room standard-library verifier confirms:

- the conditional symmetric-idempotent, LCD, even, and symplectic code facts;
- injectivity of both subset maps for every `|S|<=3`;
- the complete one-, two-, and three-subset image/dual distributions;
- a nonnegative exact rational formal enumerator with distances `(14,15)`;
- all 100 forward and 100 inverse MacWilliams rows;
- dual complement symmetry and every forced lower bound; and
- exactly 34 fractional image coefficients and 32 fractional dual
  coefficients.

The integral scout remains `UNKNOWN_HARD_TIMEOUT`.  It contains neither an
integral solution nor an infeasibility certificate and permits no negative
inference.

The rational witness is not an integral enumerator, LCD certificate, binary
code, adjacency matrix, or graph.  No rank or Conway-99 claim follows.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave131-binary-lcd-enumerator\independent_verify.py `
  --verify `
  verification\wave131-binary-lcd-enumerator\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave131-binary-lcd-enumerator -p "test_*.py" -v
```
