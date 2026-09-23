# Wave130 independent no-cache audit

Verdict: **VERIFIED_SCOPED_FINITE**.

The sealed Wave130 cutoff-28 primal is an exact rational feasible point for
the stated finite Jacobi necessary-condition relaxation.

```text
module variables:       239
equalities replayed:    454 / 454
inequalities replayed:  1686 / 1686
failed rows:            0
tight inequalities:     506
candidate SHA-256:      05ad8cf461cc7c79f85300d45492f1f30e3c1030a3c1943a9da3984d5add39a3
```

This is a no-cache audit.  The verifier independently reconstructs the
239 Fourier columns from the defining theta, Eisenstein, and Fricke formulas
using exact `Fraction` arithmetic.  It imports no discovery code, reads no
pickle/cache, and does not reuse the cddlib candidate generator.

The result corrects the prior cutoff-28 `UNKNOWN` boundary and verifies that
this finite relaxation is feasible through `q^28`.  It does not construct a
graph or lattice, realize or exclude rank 28, establish a complete integral
modular object, or resolve Conway-99.

Reproduce:

```powershell
python -B verification/wave130-cdd-exact-lp/independent_no_cache_verify.py `
  --verify verification/wave130-cdd-exact-lp/independent-results.json
python -B -m unittest discover `
  -s verification/wave130-cdd-exact-lp -p "test_*.py" -v
```
