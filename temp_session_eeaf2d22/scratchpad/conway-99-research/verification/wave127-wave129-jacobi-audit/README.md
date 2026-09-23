# Wave 127/129 independent Jacobi audit

Verdict: `VERIFIED_SCOPED_FINITE`.

The sealed Wave 127 and Wave 129 packages were frozen and preinspected before
execution.  A clean-room standard-library verifier, importing no discovery
module or verification routine, confirms exact rational feasibility of the
finite Jacobi relaxations at cutoffs 10, 12, 14, 16, 18, and 20.

| Cutoff | Exact equalities | Exact inequalities | Tight |
|---:|---:|---:|---:|
| 10 | 282 | 320 | 263 |
| 12 | 304 | 436 | 300 |
| 14 | 326 | 562 | 332 |
| 16 | 346 | 700 | 344 |
| 18 | 366 | 846 | 381 |
| 20 | 386 | 1,000 | 396 |
| 28 | `UNKNOWN` | `UNKNOWN` | not applicable |

The verifier also reconstructs the 239-dimensional modular/Jacobi module,
checks every Eisenstein-product rank through the Sturm bound, derives

```text
h_c = -7^(-3-c) (f_c | W_7),
```

and verifies exact consistency of all seven Fourier-column caches.

These are finite necessary-condition null results.  They do not construct a
lattice or graph, prove rank-28 realizability, exclude rank 28, or resolve
Conway-99.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave127-wave129-jacobi-audit\independent_verify.py `
  --verify `
  verification\wave127-wave129-jacobi-audit\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave127-wave129-jacobi-audit -p "test_*.py" -v
```
