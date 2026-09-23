# Discovery-to-verifier comparison

Verdict: `VERIFIED_SCOPED_RATIONAL`; no correction was required.

| Claim | Discovery | Independent result |
|---|---:|---:|
| image dimension | 54 | 54 |
| dual dimension | 45 | 45 |
| subset maps injective through size 3 | yes | yes |
| three-subset total | 156,849 | 156,849 |
| image forced weights | 7 entries | exact match |
| dual forced weights | 8 entries | exact match |
| dual complement bounds | 8 entries | exact match |
| forward MacWilliams rows | 100 | 100 passed |
| inverse MacWilliams rows | 100 | 100 passed |
| formal distances | `(14,15)` | `(14,15)` |
| image fractional coefficients | 34 | 34 |
| dual fractional coefficients | 32 | 32 |
| integral scout | `UNKNOWN` | `UNKNOWN` |

The verifier independently checked 200 coefficients, 200 transformation
rows, and 23 forced lower bounds.

The bounded integral process was not treated as a proof-producing run.
Its sealed result has no model and no infeasibility certificate.  The only
valid conclusion is `UNKNOWN`.

Ordinary weight coefficients do not encode `C intersect C^perp`, the 99
labelled neighborhood rows, their Gram matrix, or a graph.
