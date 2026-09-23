# Wave 124: the index-70 C4 Jacobi reduction

Claim label: `DERIVED_AND_NULL_BOUNDARY`; independent verification required.

This package replaces the four-variable Wave 116 marking by one alternating
direction per induced four-cycle.  If

```text
epsilon=(1,-1,1,-1),  d_C=sum epsilon_i u_i,
```

then `d_C` is a primitive norm-20 vector of `L`.  Thus
`b_C=sqrt(7)d_C` is a divisibility-seven norm-140 vector of `K`, giving a
one-variable Jacobi sum of weight 22 and index 70.  Its Fricke partner on
`L` has index 10.

On the verified norm-14, 16, 18, and 20 graph shells, coefficient
`r=28` exactly selects the chosen alternating C4 pattern.  The coefficients
at `q^7,q^8,q^9,q^10` therefore count antipodal vector-C4 incidences, with
no false positives from other coordinate patterns.

The 2,079 vectors `d_C` also form a tight frame:

```text
sum_C d_C d_C^T = 945 I.
```

This gives exact second Jacobi moments.  An even degree-eight polynomial in
the one coordinate `ell_C` detects `|ell_C|=4`, so the full target can be
written using only five Taylor moments of weights 22, 24, 26, 28, and 30.

The package constructs an exact 18-vector basis of the full-level subspace
`J_22,10(SL2Z)` inside `J_22,10(Gamma0(7))`, plus its 17-dimensional cusp
subspace.  Explicit cusp directions show that modularity, Fricke,
normalization, scalar specialization, and even the first several Taylor
moments do not by themselves bound the target.  Those directions have
signed coefficients and forbidden short-shell Fourier patterns, so they do
not refute a stronger graph-compatible positive model.

No basis of the whole level-seven space and no Jacobi upper certificate are
claimed.  Rank 28, rank 30, Conway-99, and literature novelty remain
`UNKNOWN`.

Reproduce with:

```text
python -B attempts/wave124-c4-index70-jacobi/exact_check.py --verify attempts/wave124-c4-index70-jacobi/exact-results.json
python -B -m unittest discover -s attempts/wave124-c4-index70-jacobi -p "test_*.py" -v
python -B attempts/wave124-c4-index70-jacobi/seal_checkpoint.py --verify
```
