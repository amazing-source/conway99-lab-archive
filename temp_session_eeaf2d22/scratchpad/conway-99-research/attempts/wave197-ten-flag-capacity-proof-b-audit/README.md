# Wave 197 proof-B ten-flag capacity audit

For each nonedge there are at most five canonical exact-three flags in
each orientation.  Coupling this capacity to the Wave196 global flag and
label caps gives a conditional exact certificate for

```text
Q>=7033.
```

Run:

```powershell
python -B attempts/wave197-ten-flag-capacity-proof-b-audit/exact_check.py --verify attempts/wave197-ten-flag-capacity-proof-b-audit/exact-results.json
python -B -m unittest -v attempts/wave197-ten-flag-capacity-proof-b-audit/test_exact_check.py
```

Status: `AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
