# Wave200 two-face gluing verifier

This package independently verifies, conditionally on the frozen
prism-free rank-11 endpoint, that the Wave198 integer faces
`Q0=7037,7038` are impossible and hence

```text
Q>=7039.
```

The proof is analytic: exact slack arithmetic, oriented incidence, simple
3-uniform local families, four-vertex fibres, and the two fixed
Hilton--Milner equality formulas.  It performs no graph or configuration
search.

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave200-two-face-gluing-verifier\independent_check.py --verify verification\wave200-two-face-gluing-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave200-two-face-gluing-verifier\test_independent_check.py
```
