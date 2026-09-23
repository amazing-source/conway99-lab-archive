# Wave 201 proof-B hostile audit

This analytic audit confirms the multiplicity-weighted fiber row

```text
delta>=3q-epsilon,
```

including empty, singleton, and multiple selected leaf values in one
four-element fiber. It verifies the exact budget floor `B>=891` and the
conditional conclusion `Q>=7059`.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave201-multiplicity-weighted-fiber-loss-proof-b-audit\exact_check.py --verify attempts\wave201-multiplicity-weighted-fiber-loss-proof-b-audit\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave201-multiplicity-weighted-fiber-loss-proof-b-audit\test_exact_check.py
```

No search is performed. Status:
`AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
