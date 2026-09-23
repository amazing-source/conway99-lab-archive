# Wave 98: long scalar-theta positivity probe

Status: `UNKNOWN` finite null result.

Wave 86 constructed an exact formal modular pair attaining

```text
N14+N16+N18 = 5868.
```

It was known to be integral, even, and nonnegative through degree 50. This
package reconstructs the same pair by a separate long-prefix arithmetic
implementation and extends that finite check through degree 1,000.

No bad coefficient is found. This does not prove all-orders positivity and
does not realize a lattice, marked frame, or graph. It is evidence that the
scalar modular-form lane alone is unlikely to exclude the rank-28 case.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave98-scalar-positivity-probe\probe.py `
  --precision 1000 `
  --verify attempts\wave98-scalar-positivity-probe\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave98-scalar-positivity-probe -p "test_*.py" -v
```
