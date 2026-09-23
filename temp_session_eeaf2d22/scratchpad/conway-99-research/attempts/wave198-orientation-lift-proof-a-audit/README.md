# Wave 198 proof-A hostile audit

This package independently audits the sealed Wave198 proof-B
orientation-lift theorem. It reconstructs the row

```text
S5=180V-3*n3-4*p3-5*a3-5*b3>=0
```

and the exact certificate proving the conditional bound `Q>=7037`.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave198-orientation-lift-proof-a-audit\exact_check.py --verify attempts\wave198-orientation-lift-proof-a-audit\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave198-orientation-lift-proof-a-audit\test_exact_check.py
```

Status: `ACCEPTED_AS_DERIVED`; clean-room verifier promotion is pending.
