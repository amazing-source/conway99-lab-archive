# Wave 194: type-two residuals and joint low-target capacity

This package proves the derived conditional bound

```text
3Q>=5C,
Q>=6930 when C=4158.
```

The analytic refinements are:

- cancel an exact-three type-two raw inside its translated `6+2` or `2+6`
  relation to force a distinct exact-one/exact-three residual;
- distinguish the two same-label residuals by singleton-side support and
  opposite exact-three centers;
- split the new residual pool into `y` exact-one circuits and `g`
  exact-three companion pairs; and
- couple selected type-two incidence inside and outside the
  selected-type-three label union.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave194-type2-residual-low-u-proof-a\exact_check.py --verify attempts\wave194-type2-residual-low-u-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave194-type2-residual-low-u-proof-a\test_exact_check.py
```

The checker verifies a fixed rational coefficient identity and the full
one-parameter equality-face formulas. It performs no graph, code, cover,
SAT, LP, configuration, enumeration, or isomorphism search.

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
