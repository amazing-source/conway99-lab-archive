# Wave 116 verifier package

Verdict: `VERIFIED_WITH_CLARIFICATIONS`, conditional on verified Waves 66,
71, and 112.

The C4 projector, lattice-compatible `K/L` markings, discriminant sector,
Poisson-Fricke normalization, antipodal coefficient convention, thresholds
52,812 and 51,975, and degree-32 interpolation all pass independent exact
checks.

The naive marking `u_i/sqrt(7)` is definitively outside `K*`, not merely
unproved there.  The conventional marking has raw matrix-index discriminant
`1,023,942,465`, while the smaller 2,401-class sector is not known to close
without its orthogonal complement.

No upper bound or rank exclusion is proved.  Conway-99 remains `UNKNOWN`.

Reproduce:

```powershell
python -B verification\wave116-c4-jacobi-theta\independent_verify.py `
  --verify verification\wave116-c4-jacobi-theta\independent-results.json
python -B -m unittest discover `
  -s verification\wave116-c4-jacobi-theta -p "test_*.py" -v
```
