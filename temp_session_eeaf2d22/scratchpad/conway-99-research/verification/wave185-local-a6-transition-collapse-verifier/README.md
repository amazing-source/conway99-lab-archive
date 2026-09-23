# Wave 185 independent verifier

This package independently audits the conditional local `A6` transition
collapse in `attempts/wave185-local-a6-transition-collapse`.

The verifier does not import or execute the discovery checker.  It rebuilds
the six-vertex prism certificate, the four-corner cell restriction, the
rooted transition table, the incident-cell capacity, the global companion
count, the integer multiplicity profiles, and the complement-triangle count
from the frozen prior-wave statements.  It validates the Wave 185 source
manifest, source input freeze, and every direct prior-package manifest named
by that freeze.

The verdict is `VERIFIED_WITH_SCOPE`:

```text
n_7=0,
5*n_5+6*n_6=2079,
(n_5,n_6)=(15+6u,334-5u), 0<=u<=66,
349<=|R|<=415,
rainbow complement triangles >= 94264.
```

All claims remain conditional on the Wave 181 equality face and endpoint
prism-freeness.  The endpoint and Conway 99 remain `UNKNOWN`.

Reproduce with:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave185-local-a6-transition-collapse-verifier\independent_check.py `
  --verify `
  verification\wave185-local-a6-transition-collapse-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave185-local-a6-transition-collapse-verifier\test_independent_check.py
```
