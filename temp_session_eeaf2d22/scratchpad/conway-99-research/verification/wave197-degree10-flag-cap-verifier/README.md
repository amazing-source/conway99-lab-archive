# Wave197 degree-ten flag-cap verifier

Status: `VERIFIED_WITH_SCOPE`.

Under the frozen prism-free rank-11 endpoint assumptions, this package
independently verifies the selected exact-three label-degree cap, the
weighted `S10`, `SH`, and `SF` rows, and

```text
Q>=7033.
```

The clean-room mathematical result was frozen before either Wave197 source
was opened.  The full verifier then compared the sealed proof-A package and
used sealed proof B only as a hostile, non-premise cross-check.

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave197-degree10-flag-cap-verifier\independent_check.py --verify-math verification\wave197-degree10-flag-cap-verifier\independent-math-result.json
.\.venv\Scripts\python.exe -B verification\wave197-degree10-flag-cap-verifier\independent_check.py --verify verification\wave197-degree10-flag-cap-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave197-degree10-flag-cap-verifier\test_independent_check.py
```

No graph, code, cover, SAT, LP, construction, configuration, family,
enumeration, isomorphism, or brute-force search is used.  Rank 11, the
endpoint, and Conway-99 remain `UNKNOWN`.
