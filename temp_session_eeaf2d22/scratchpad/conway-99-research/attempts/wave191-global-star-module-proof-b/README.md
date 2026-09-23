# Wave 191 global-star module package

This package freezes the proof-B result obtained by imposing all 99
all-one point-star relations simultaneously in the modular
point-triangle incidence representation.

At the conditional rank-11 endpoint it derives

```text
66<=rank_F3(B)<=82,
17<=ell=dim ker(B^T)<=33,
rank of the standard form on ker(B^T)=2ell-34.
```

The full run report is
`agents/2026-07-29-wave191-global-star-module-proof-b.md`.  The compact
derivation, protocol, exact checker, frozen results, tests, and input hashes
are included here.

Run:

```powershell
python -B attempts/wave191-global-star-module-proof-b/exact_check.py
python -B -m unittest -v attempts/wave191-global-star-module-proof-b/test_exact_check.py
```

The package status is `DERIVED`.  It has not been independently verified.
