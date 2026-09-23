# Wave 185: local A6 transition collapse

This package continues the conditional Wave 181 equality face without a
construction search.  It combines the verified global-root support theorem
with the rooted `K_{2,2,2,2,2,2,2}` transition geometry.

The main conclusions are:

```text
n_7=0,
5*n_5+6*n_6=2079,
(n_5,n_6)=(15+6u,334-5u), 0<=u<=66,
349<=|mathcal R|<=415.
```

The key step is geometric: an internal edge of one four-point local-root
cell that shares an actual rooted endpoint would create an induced triangular
prism.  Prism-freeness therefore makes every cell graph a matching, excluding
the former multiplicity-seven `P4` case.

The exact checker validates only the finite arithmetic and transition table;
the proof of the induced-prism implication is in `derivation.md`.

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave185-local-a6-transition-collapse\exact_check.py --verify `
  attempts\wave185-local-a6-transition-collapse\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave185-local-a6-transition-collapse\test_exact_check.py
```

All conclusions are conditional on Wave 181 equality.  They do not exclude
the endpoint or resolve Conway 99.
