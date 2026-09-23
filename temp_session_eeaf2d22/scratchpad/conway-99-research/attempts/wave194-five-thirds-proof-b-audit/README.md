# Wave 194 five-thirds proof-B audit

This package independently audits the doubled type-two residual lemma, the
sharpened type-three-label-union capacity, and the resulting exact
certificate

```text
Q>=5*4158/3=6930.
```

The audit uses exact ternary support subtraction and rational arithmetic.
It performs no graph, cover, code, SAT, LP, configuration, isomorphism, or
exhaustive search.

Run:

```powershell
python -B attempts/wave194-five-thirds-proof-b-audit/exact_check.py --verify attempts/wave194-five-thirds-proof-b-audit/exact-results.json
python -B -m unittest -v attempts/wave194-five-thirds-proof-b-audit/test_exact_check.py
```

Status: `DERIVED`; verifier promotion is pending.

