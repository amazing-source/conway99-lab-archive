# Discovery-to-verifier comparison

Verdict: `VERIFIED_SCOPED_FINITE`; no correction was required.

| Item | Discovery | Independent verifier |
|---|---|---|
| Module dimension | 239 | 239 |
| Dimensions by `c` | `15,17,17,19,21,21,23,25,25,27,29` | exact match |
| Fricke factor | `-7^(-3-c)` | exact match |
| Cutoff 10 | exact feasible | verified, all 602 rows |
| Cutoff 12 | exact feasible | verified, all 740 rows |
| Cutoff 14 | exact feasible | verified, all 888 rows |
| Cutoff 16 | exact feasible | verified, all 1,046 rows |
| Cutoff 18 | exact feasible | verified, all 1,212 rows |
| Cutoff 20 | exact feasible | verified, all 1,386 rows |
| Cutoff 28 | `UNKNOWN` | `UNKNOWN` |

The verifier checked 616 raw Eisenstein-product Fricke involutions, exact
product ranks at all eleven weights, 3,234 exact `q^0` Fricke boundary
relations, and 706,322 exact cross-cache coefficients.

At cutoff 28, the retained artifact has no rational solution coordinates.
The floating reduced LP reported feasibility, but exact active-face recovery
failed and no exact Farkas certificate exists.  This is neither a primal nor
a dual certificate, so `UNKNOWN` is mandatory.

The verified claim is only that these six finite relaxations are feasible.
It does not promote any graph, lattice, rank-realizability, or global
Conway-99 claim.
