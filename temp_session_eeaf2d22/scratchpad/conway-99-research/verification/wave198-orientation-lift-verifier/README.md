# Wave198 orientation-lift verifier

Status: `VERIFIED_WITH_SCOPE`.

Conditionally on the frozen prism-free rank-11 endpoint, this package
independently verifies the oriented selected-label row

```text
S5=17820-3n3-4p3-5a3-5b3>=0
```

and the exact consequence `Q>=7037`.

The clean-room result was frozen before either sealed Wave198 source was
opened.  No graph, configuration, cover, SAT, LP, construction,
enumeration, isomorphism, or brute-force search is used.

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave198-orientation-lift-verifier\independent_check.py --verify verification\wave198-orientation-lift-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave198-orientation-lift-verifier\test_independent_check.py
```

Rank 11, endpoint existence, and Conway-99 remain `UNKNOWN`.
