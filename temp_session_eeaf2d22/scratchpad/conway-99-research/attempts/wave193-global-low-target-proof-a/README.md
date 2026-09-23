# Wave 193: global low-target and residual flow

This package combines:

- residuals forced by exact-two type-one and type-three raw circuits; and
- one low leaf target for every label used by a selected type-three
  circuit.

An exact nonnegative certificate proves the derived conditional bound

```text
117Q>=177C,
Q>=6291 when C=4158.
```

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave193-global-low-target-proof-a\exact_check.py --verify attempts\wave193-global-low-target-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave193-global-low-target-proof-a\test_exact_check.py
```

The checker verifies a formal coefficient identity and a fixed arithmetic
null. It performs no graph, code, cover, SAT, LP, configuration,
enumeration, or isomorphism search.

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
