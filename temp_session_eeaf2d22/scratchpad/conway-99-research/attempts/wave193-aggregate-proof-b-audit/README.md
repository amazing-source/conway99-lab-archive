# Wave 193 aggregate proof-B audit

This package independently checks the proposed aggregate low-target
certificate and its two delicate collision rows.

Verdict:

```text
AUDIT_PASS
Q>=ceil(59*4158/39)=6291
```

The work is analytic.  It performs no graph, cover, code, SAT, LP,
configuration, isomorphism, or exhaustive search.

Run:

```powershell
python -B attempts/wave193-aggregate-proof-b-audit/exact_check.py --verify attempts/wave193-aggregate-proof-b-audit/exact-results.json
python -B -m unittest -v attempts/wave193-aggregate-proof-b-audit/test_exact_check.py
```

Status: `DERIVED`; verifier promotion remains pending.

