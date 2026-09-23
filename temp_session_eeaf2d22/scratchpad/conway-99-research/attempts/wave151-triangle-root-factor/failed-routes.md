# Failed and incomplete routes

## Fixed-Q1 third-group exact model

The stored exact `Q1` was frozen. After removing mappings that would
contribute to a zero target entry, the `Q2` problem had:

- 1,620 Boolean variables;
- 60 domain exact-one equations;
- 60 image exact-one equations;
- 288 exact vertex-pair capacity equations.

Z3 returned `unsat` in 40.46 seconds. No proof trace was exported, so the
status is not treated as a certificate. Even a proof would refute only this
`Q1`, not all first-stage factors.

## Fixed-Q1 heuristic Q2

Seeded permutation-swap search retained an exact squared residual of 80 for
the two cross targets. The permutation is stored in `exact-results.json` so a
future exact repair can resume from the same point. A nonzero residual is not
negative evidence.

## Unrestricted joint C search

A seeded 240-second local search varied both edge permutations simultaneously
and minimized the sum of squared residuals for `G_01,G_02,G_12`. Its best
exact score was 108. It found no complete factor and supplies no negative
certificate.

## Residual D layer

Not run. Entering the `D` layer without a complete exact `C` would change the
finite problem. Its status is `NOT_REACHED`, not infeasible.
