# Wave 172 independent verification

Verdict: `VERIFIED_WITH_SCOPE`.

At the prism-free endpoint, every weight-three word in the dual of the
centered ternary block code has equal nonzero coefficients.  Its support is
an induced `3K3` of triangle blocks, and the corresponding three centered
rows have joint counts

```text
000: 15
111: 144
222: 18
012 permutations: 54
```

The verifier used a derivation materially different from the discovery
count: a normalized integer lift for the mixed-sign exclusion and pairwise
row-distance energy for the joint composition.

The endpoint entry alphabet is essential.  The conditional rank hypothesis
`r3=12` is not used.  This is a marked dual-code constraint, not an endpoint
exclusion.
