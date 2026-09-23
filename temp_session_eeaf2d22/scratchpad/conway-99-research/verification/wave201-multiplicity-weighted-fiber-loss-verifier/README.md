# Wave201 multiplicity-weighted fibre-loss verifier

This package independently verifies, conditionally on the frozen
prism-free rank-11 endpoint,

```text
delta_x >= sum_nonprivate_y (m_x(y)-2)
```

at every center, and consequently

```text
Q>=7059.
```

The source-blind result was hash-frozen before either Wave201 source was
opened.  It explicitly treats multiple selected labels in one
four-point fibre, multiplicity one, selected-versus-full incidence,
deficient centers, and the three exact Hilton--Milner baselines at a
tight center.

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave201-multiplicity-weighted-fiber-loss-verifier\independent_check.py --verify verification\wave201-multiplicity-weighted-fiber-loss-verifier\independent-math-result.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave201-multiplicity-weighted-fiber-loss-verifier\test_independent_check.py
```

No graph, configuration, family, cover, SAT, LP, enumeration,
isomorphism, or brute-force search is used.
