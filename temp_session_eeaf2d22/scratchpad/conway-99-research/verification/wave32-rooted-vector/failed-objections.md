# Wave 32 rooted-vector adversarial objections

These controls were run against the frozen claim. They are evidence that the
displayed hypotheses are active; they are not evidence for graph completion.

| Objection or mutation | Outcome |
|---|---|
| Drop primitivity of the column lattice | A control matrix with maximal-minor gcd 2 makes its transpose miss `(1,0)`. The integral-image bridge genuinely needs primitivity. |
| Replace `||z||^2=126` by 198 | Both nonzero residue classes survive the integer norm screen. The norm constant is active. |
| Replace the `-4` eigenvalue by `-3` | Three norm-14 distributions survive, including one with an entry 2. The amplitude argument is specific to `-4`. |
| Allow 0 in the equal-sign extreme-root Gram alphabet | Positive-semidefinite size-four fibers survive. The endpoint Gram alphabet is active. |
| Replace `mu=2` by `mu=3` | Same-sign support-edge counts `t=1,2` survive the counting screen. The design forcing is specific to `mu=2`. |
| Replace the reflection denominator 21 by 42 | The proposed coordinate map is not an involution. |
| Treat the 99-vertex partial control as a completed graph | Rejected. Its outside degree histogram is `2^28,4^42,0^15`; outside-only regularity and common-neighbor conditions remain unfilled. |

## Nonblocking v1 defect and v2 repair

The superseded v1 discovery checker and JSON result said that the three
outside classes need remaining degrees `{8,12,14}`. Their exact retained
hashes are:

```text
exact_check.py       41e077321fa691a3916da50e992a09d43d4f2d252cae39030bc2d7663bd60e97
test_exact_check.py  38b7023a66c4b3305cfb080d27cbf39dd5330dab79eaa85eb7c0fcbd3104dd76
exact-results.json   6ff9844994c2605266feaad96b4a4ebaf193b5be437bd9e4b21dbf7b98860d99
artifact manifest    a2dd5896871dda4d0dc54b56d9cb081993079ad03241113e1a36bb0ab972d291
```

Direct degree reconstruction gives:

```text
support-edge completion:     current 2, remaining 12
support-nonedge completion:  current 4, remaining 10
no-support-neighbor:         current 0, remaining 14
```

Thus the exact distribution is `10^42,12^28,14^15`. Corrected v2 computes
and tests that distribution and makes hostile `q=3` metadata parameter-derived.
Its manifest is
`ba6c7099e06e24fe2feee4d19021dac9ddf49cbfe99acdd54f905a6c40728b8e`,
which independently replayed. The v1 defect did not affect the rooted-vector
reduction because the partial object is only a local control and completion
remains open.

## Discovery-suite coverage objection

Several discovery tests compare emitted prose or fixed constants rather than
recomputing the associated bridge. The independent suite therefore rebuilds
the projector transport, triangle census, tensor constants, reflection
coefficients, and hostile partial object without importing discovery code.
