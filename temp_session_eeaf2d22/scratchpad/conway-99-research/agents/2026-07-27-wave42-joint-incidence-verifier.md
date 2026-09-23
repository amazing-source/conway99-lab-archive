# Wave 42 verifier: canonical joint incidence

## Assignment

Independently verify the canonical mask-51739 joint-incidence reduction without
reading discovery artifacts before freezing the verification protocol,
implementation, tests, result, and a positive two-fibre certificate.

## Result

Claim label: **VERIFIED scoped conditional reduction**.

The standard-library verifier independently reproduces:

```text
core components:             12 + 24
per-fibre component balance:  4 + 8
forced block component split:  2 + 4
pair-pattern multiplicities:   4,4,4,16,16,16
six-set filters:               216000 -> 118718 -> 49736 -> 45032
column overlaps 0/1/2:         458 / 1004 / 308
H edges by overlap 0/1/2:       96 / 144 / 0
H triangles / four-cycles:      32 / 181
```

It also supplies a complete two-fibre concurrence permutation generated before
comparison.  This certificate differs from the discovery certificate; both
independently realize the same exact `Q_01`.

Fifteen verifier tests and nine discovery tests pass.  The discovery manifest
is exact.  The frozen independent and discovery results agree on every scoped
quantity.

## Scope

This remains conditional on `n3=4158`, `r3=12`, all edges type `2+2+2`, and
the canonical mask-51739 rank-33 block.  There is no full `B`, compatible
`H`, endpoint exclusion, strict upper bound, graph, counterexample, solution,
or novelty claim.

Reproducible evidence is in
`verification/wave42-joint-incidence/`.

