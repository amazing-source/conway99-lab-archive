# Wave 81: exact labelled norm-16 design

Status: `DERIVED`; independent verification required.

Conditional on the verified Wave 78 norm-16 histogram, this package moves
from scalar moments to exact labelled incidence matrices without assuming
any target automorphism.

The complete finite census finds:

- 1,800 anchored support matrices and five support isomorphism orbits;
- 4,985 exact deficiency-pair coupling multisets, with every support orbit
  still represented;
- all 4,985 pass a necessary per-`X2` common-neighbor flow test;
- the eight `X2` vertices must induce either no edge or one edge;
- each support orbit determines an exact degree-83 outside characteristic
  polynomial by Jacobi's principal-minor identity.

This is a substantial reduction, not a Conway-99 solution. No full outside
graph has been constructed, and all survivors remain necessary candidates.

## Replay

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave81-norm16-labeled-design\exact_check.py `
  --verify attempts\wave81-norm16-labeled-design\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave81-norm16-labeled-design -p "test_*.py" -v
```

The checker uses only the Python standard library and refuses to start
below 15% free physical memory.
