# Wave 116: C4 coordinate Jacobi/theta assessment

Status: `DERIVED`; independent verification required.

The core projected-Gram premise is correct:

```text
E_-4[C]=(3I-H_C+J/9)/7,
spec(E_-4[C])={13/63,5/7,3/7,3/7},
det(E_-4[C])=65/2401.
```

The naive small-index Jacobi interpretation needs correction.
`u_i/sqrt(7)` is not proved to lie in `K*`.  A conventional common-index
Jacobi sum uses `g_i=3sqrt(7)u_i in K`, with cycle Gram
`G_K=441E`; its determinant is `1,023,942,465`.  The sum over all 2,079
cycles is a single Jacobi object without any automorphism assumption because
every summand has the same induced-cycle Gram.

Its coefficients at `q^7,q^8,q^9` and Fourier pattern
`21(1,-1,1,-1)` count **antipodal** cycle incidences.  Their sum is at least
52,812 in the rank-28 row; the oriented count is twice this.  An exact upper
bound of 51,975 would close the row.

Poisson/Fricke couples this `K` form to an `L` form of index divided by
seven.  No exact Jacobi basis or upper certificate is produced here, so
there is no new upper bound or rank exclusion.  A degree-32 harmonic
interpolation is recorded as a smaller-index alternative.

Reproduce:

```powershell
python -B attempts\wave116-c4-jacobi-theta\exact_check.py `
  --verify attempts\wave116-c4-jacobi-theta\exact-results.json
python -B -m unittest discover `
  -s attempts\wave116-c4-jacobi-theta -p "test_*.py" -v
```

Rank 28, Conway-99, and novelty remain `UNKNOWN`.
