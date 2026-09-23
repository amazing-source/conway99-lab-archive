# Wave 74 clean-room verification

Status: **VERIFIED, conditional on Wave 71's stated support reduction**.

The verifier independently confirms the Wave 74 branch closure for an
\(\operatorname{srg}(99,14,1,2)\) carrying the signed unit
\(-4\)-eigenvectors described by Wave 71:

- norm 18 with two same-sign edges per side is impossible;
- the adjacent two-edge shape already needs 71 opposite-support
  common-neighbor incidences against capacity 70;
- the disjoint two-edge shape leaves zero outside pair incidences, so every
  outside vertex meets at most one vertex of each sign side, while 82
  incidences must fit into only 81 outside vertices;
- an independent exhaustive enumerator reproduces exactly 4 norm-16
  \(h=0\), 20 norm-18 \(h=0\), and 6 norm-18 \(h=1\) histograms.

This package does **not** verify Wave 71's modular-form, lattice, or support
reduction. The 30 surviving histograms are necessary aggregate conditions,
not incidence matrices and not graph constructions. Norm 14, norm 16
\(h=0\), and norm 18 \(h=0,1\) remain live. Conway-99 and novelty remain
`UNKNOWN`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe verification\wave74-short-vector-closure\independent_check.py --verify
.\.venv\Scripts\python.exe -m unittest -v verification\wave74-short-vector-closure\test_independent_check.py
```

The verifier imports no discovery Python code. Its enumeration searches
\((n_2,\ldots,n_7)\) directly and uniquely solves for \(n_1,n_0\), unlike
the discovery checker's recursive enumeration over every \(n_d\).
