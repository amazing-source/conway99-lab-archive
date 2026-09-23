# Wave 197: degree-ten flag incidence

This package derives, conditionally on the prism-free rank-11 endpoint and
the sealed Wave196 local theorem,

```text
Q>=7033.
```

A fixed nonedge belongs to at most five selected exact-three flags in
either orientation, hence at most ten total. Applying this degree cap to
the selected exact-three label union and combining it with Wave196's
`F<=1287` and `J<=3564` gives a new global row. An exact rational
certificate yields `Q0>=7032.3`, so integrality gives 7,033.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave197-degree10-flag-cap-proof-a\exact_check.py --verify attempts\wave197-degree10-flag-cap-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave197-degree10-flag-cap-proof-a\test_exact_check.py
```

No graph, code, cover, SAT, LP, configuration, enumeration, or
isomorphism search is performed.

Status: `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.
