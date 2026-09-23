# Wave 90 retained null routes

## Generic spherical and harmonic bounds

The lattice minimum gives pairwise-distance bounds on the norm-14, 16, and
18 shells, but generic spherical-code bounds in dimension 44 are far above
5,868.

The marked 99-vector tight frame gives the harmonic quartic

```text
H4(x) = sum_i <x,q_i>^4 - (2/69)||x||^4.
```

On signed-unit vectors its values are exactly `574/69`, `592/69`, and
`594/69` at norms 14, 16, and 18. An exploratory exact rational
degree-four harmonic/Fricke linear program, using only the universal
pointwise frame bounds at the other coefficients, returned the upper bound

```text
25558963093916393282221013 / 103860391353024311
  = 246089608.954397...
```

for `N14+N16+N18`. This misses the provisional Wave 86 threshold by more
than four orders of magnitude. It is retained as a sharply quantified null
boundary, not as a promoted theorem of this package.

## Why the transition proof stops at norm 14

Norm-14 supports saturate every same-side pair and therefore make the
four-point root seed injective. Norm-16 and norm-18 supports have deficiency
pairs: a residual label arising from a seed pair can lie outside the signed
support. Such deficiencies can cover selected transitions, so the
`672/4` argument does not transfer without additional incidence accounting.

