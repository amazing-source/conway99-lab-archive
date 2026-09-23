# Wave 107 failure boundary

Claim label: `UNKNOWN`.

## Refuted route

The proposed characteristic-polynomial factor

```text
x^2-9x-38
```

is false. It predicts `tr(D^2)=1082`, while the Wave 105 type census
forces `tr(D^2)=1098`. The exact Jacobi calculation replaces it by
`x^2-9x-46`.

## Spectral obstruction route

The corrected exceptional eigenvalues

```text
(9+sqrt(265))/2 and (9-sqrt(265))/2
```

lie strictly between `12.5,13` and `-4,-3.5`, respectively. They obey
Cauchy interlacing with the global eigenvalues `14,3,-4`. The positive
Perron vector forces the outside graph to be connected, but creates no
contradiction.

The exact triangle, four-cycle, nullity, and shifted-rank values are also
arithmetically admissible. They are necessary rejection checks for any
future candidate, not an existence or nonexistence certificate.

No motif exclusion, full extension, or Conway-99 resolution follows.
Literature novelty remains `UNKNOWN`.
