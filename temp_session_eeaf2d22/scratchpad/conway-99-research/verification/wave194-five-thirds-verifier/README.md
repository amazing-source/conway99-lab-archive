# Wave194 five-thirds verifier

This package clean-room verifies the conditional analytic theorem

```text
3Q>=5C,
Q>=6930 for C=4158.
```

The independent mathematical result was frozen before either Wave194 source
package was inspected. The verifier audits:

- exact-three type-two residual existence;
- same-private-label double-residual distinctness;
- exact-one, exact-two, exact-three, and opposite-companion collisions;
- split `y`/`g` residual capacities;
- the `k`-cancelled type-three union row;
- the exact five-thirds coefficient identity; and
- the full arithmetic equality face.

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave194-five-thirds-verifier\independent_check.py --verify-math verification\wave194-five-thirds-verifier\independent-math-result.json
.\.venv\Scripts\python.exe -B verification\wave194-five-thirds-verifier\independent_check.py --verify verification\wave194-five-thirds-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave194-five-thirds-verifier\test_independent_check.py
```

Status: `VERIFIED_WITH_SCOPE`. The equality rows are arithmetic only; rank
11, endpoint existence, and Conway-99 remain `UNKNOWN`.
