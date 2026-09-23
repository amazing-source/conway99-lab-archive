# Wave 27 literature protocol addendum: A20

Frozen: 2026-07-24T00:57:55Z

This addendum postdates and does not modify `protocol.md` or
`protocol-correction.md`. It was frozen before the late Wave 27 A20 artifact
was opened.

## Target

Search for direct or near-direct precedent for the identity

```text
tr(A_n Q)
  = Q(e_1) + Q(e_n) + sum_{i=1}^{n-1} Q(e_i-e_{i+1})
  >= 2(n+1),
```

under the relevant positive-definite even-integral hypotheses, and for its use
at `n=20` to exclude an orthogonal `A20` lattice summand.

## Frozen queries

Inspect at most the first ten results in service-default relevance order.

1. `A20-C01`, Crossref:
   `"A20 lattice" "orthogonal summand" trace quadratic form`
2. `A20-O01`, OpenAlex:
   `"A20 lattice" "orthogonal summand" trace quadratic form`
3. `A20-Z01`, zbMATH Open:
   `A20 lattice orthogonal summand trace`
4. `A20-G01`, general web:
   `"tr(A_n Q)" "Q(e_1)" "Q(e_n)"`
5. `A20-G02`, general web:
   `"A20 lattice" "orthogonal summand"`
6. `A20-G03`, general web:
   `"A_n lattice" trace "even integral" quadratic form`

The classification vocabulary, source policy, review cap, and stopping rules
from `protocol.md` apply. Bounded non-discovery cannot establish novelty,
priority, or nonexistence. Those statuses remain `UNKNOWN`.
