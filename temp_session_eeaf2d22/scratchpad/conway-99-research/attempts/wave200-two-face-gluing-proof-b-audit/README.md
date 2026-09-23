# Wave 200 proof-B hostile audit

This analytic audit confirms the two-face obstruction

```text
Q0=7037,7038  => contradiction,
Q>=7039 conditionally.
```

Its main purpose is to check that repeated-leaf losses from saturated
orientations add across distinct four-vertex pair fibers. The audit uses
no graph or configuration search.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave200-two-face-gluing-proof-b-audit\exact_check.py --verify attempts\wave200-two-face-gluing-proof-b-audit\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave200-two-face-gluing-proof-b-audit\test_exact_check.py
```

Status: `AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
