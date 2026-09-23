# Wave 101: all-rank level-7 scalar theta LP

Status: `DERIVED`, discovery only.

This package extends the exact Wave 86 calculation from the `q=16` row to
all seven surviving rows `q=2,4,...,14`. It uses the complete
15-dimensional space `M_22(Gamma0(7))`, the exact Fricke involution, and

```text
Theta_L = -7^(11-q/2) (Theta_K|W_7).
```

For `x_n=[q^n]Theta_K`, exact primal/dual rational certificates give:

| q | r=44-q | rational lower bound on x7+...+x14 | parity-rounded bound |
|---:|---:|---:|---:|
| 2 | 42 | 717848/3971 | 182 |
| 4 | 40 | 6286208/3971 | 1,584 |
| 6 | 38 | 45264728/3971 | 11,400 |
| 8 | 36 | 28919488/361 | 80,110 |
| 10 | 34 | 2228061848/3971 | 561,084 |
| 12 | 32 | 15580466396938/82045 | 189,901,474 |
| 14 | 30 | 6793429016900/3709 | 1,831,606,638 |

The package also supplies exact positive prefix and low-shell-weighted
certificates. None contradicts the rigorous mod-2 lattice bounds recorded in
`derivation.md`.

The strategically important null result is that every row still has an exact
first-15-coefficient scalar control with `x7=x8=x9=0`. Thus this scalar cone
does not force a vector in the norm `14,16,18` range where the graph-specific
signed-unit dictionary is proved. No signed-unit interpretation is assumed
for norms `20` through `28`.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave101-all-rank-level7-lp\exact_lp.py --verify

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave101-all-rank-level7-lp -p "test_*.py" -v
```

The tests are discovery regression tests, not an independent verifier.
Conway-99 and novelty remain `UNKNOWN`.
