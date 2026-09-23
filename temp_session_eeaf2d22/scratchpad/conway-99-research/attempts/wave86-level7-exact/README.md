# Wave 86: exact level-7 Fricke theta pair

Status: **DERIVED - discovery, independent verification required**.

For the Wave 71 `q=16` row, exact weight-22 level-7 modularity and the
Fricke exchange imply

```text
N14+N16+N18 >= 5868.
```

The proof is an explicit positive-coefficient identity in the first 15
Fourier coefficients, followed by the verified Wave 71 congruence modulo
14.  No floating optimization or solver nonhit is used.

An exact formal modular pair attains the scalar bound through Sturm and
remains integral, even, and nonnegative through `q^50`.  It is not a
lattice or graph.  The `q=16` row, Conway-99, and novelty remain `UNKNOWN`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe attempts\wave86-level7-exact\exact_check.py --verify
.\.venv\Scripts\python.exe -m unittest -v attempts\wave86-level7-exact\test_exact_check.py
```
