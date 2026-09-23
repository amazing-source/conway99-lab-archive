# Discovery-to-verifier comparison

Verdict: `VERIFIED_SCOPED`; no mathematical correction was required.

| Claim | Discovery | Independent result |
|---|---|---|
| Pattern histogram | `3,48,36` | exact match |
| `det(Lambda)` | `6191736422400` | exact match |
| `A_U,2` valuations | `2,8` | exact match |
| `A_K,2` valuations | `3,3,3,3` | exact match |
| `A_U,3` valuations | `1,1,2,2` | exact match |
| `A_K,3` valuations | `1,1,2` | exact match |
| `A_U,5`, `A_K,5` | `1,1`; trivial | exact match |
| non-seven phases `(U,K)` | `(-i,-1)` | exact match |
| seven phases `(U,K)` | `(-1,-1)` | exact match |
| seven types | both `O^-(k,7)` | exact match |
| rootlessness | both minima at least four | exact match |
| live rows | all `k=16,18,...,30` | exact match |

The nontrivial cyclotomic-remainder hashes also match exactly.  The trivial
`K,p=5` remainder is serialized differently (`[1]` compactly in discovery
versus canonical indented JSON here); its module order, denominator, and
phase all match.

Two scope clarifications are retained:

1. Existence of the finite quadratic space `O^-(k,7)` is only compatibility
   with a local necessary condition.  It does not construct either integral
   eigenlattice.
2. The rootlessness proof depends on the ambient coordinate realization and
   on `D` being a simple-graph adjacency matrix.  It is valid under the
   frozen graph hypothesis, not for an arbitrary abstract lattice with the
   same discriminant form.
