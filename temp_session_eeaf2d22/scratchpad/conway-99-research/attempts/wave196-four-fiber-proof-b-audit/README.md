# Wave 196 proof-B four-fiber audit

Independent conditional derivation of

```text
c_x<=13, j_x<=36, F<=1287, J<=3564, Q>=7029.
```

Run:

```powershell
python -B attempts/wave196-four-fiber-proof-b-audit/exact_check.py --verify attempts/wave196-four-fiber-proof-b-audit/exact-results.json
python -B -m unittest -v attempts/wave196-four-fiber-proof-b-audit/test_exact_check.py
```

Status: `AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
