# Wave195 Hilton--Milner verifier

This package clean-room verifies the conditional analytic theorem

```text
Q>=6980.
```

The independent result was frozen before either Wave195 source package was
opened. The verifier checks:

- canonical exact-three flag simplicity and fixed-center injection;
- pairwise intersection from dual distance;
- the exact `(n,k)=(7,3)` Hilton--Milner specialization;
- the common-star bound `j_x<=12+12+c_x<=39`;
- distinct oriented `a3+b3` labels, including opposite type-two
  orientations;
- inherited pool separation and the global `SG` row;
- the exact rational certificate, rounding, and circuit counts;
- three independent rational null controls; and
- quarantine of the failed mixed type-one orientation route.

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave195-hilton-milner-verifier\independent_check.py --verify-math verification\wave195-hilton-milner-verifier\independent-math-result.json
.\.venv\Scripts\python.exe -B verification\wave195-hilton-milner-verifier\independent_check.py --verify verification\wave195-hilton-milner-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave195-hilton-milner-verifier\test_independent_check.py
```

Status: `VERIFIED_WITH_SCOPE`. Rank 11, endpoint existence, and Conway-99
remain `UNKNOWN`.
