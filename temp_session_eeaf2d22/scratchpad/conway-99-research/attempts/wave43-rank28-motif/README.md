# Wave 43 prism-free rank-27 equality: even endpoint types

Status: **DERIVED, pending independent verification**.

This package classifies rank-27 equality for the three even edge-local types
allowed at the conditional prism-free endpoint:

```text
2+2+2,  4+2,  6.
```

Starting from the independently verified Wave 42 decomposition,

```text
rank_F7(K39) = (25-2e) + 2 rank(F) + rank(D),
rank(F) >= e,
```

rank 27 has exactly two mechanisms:

```text
rank(F)=e   and rank(D)=2,
rank(F)=e+1 and rank(D)=0.
```

Here `F` is the projected border matrix and `D` is its symmetric Schur
residual. At `n3=4158`, absence of induced triangular prisms makes the
cross-fibre permutation a derangement.

The exact result is:

| type | relevant derangements | matching pairs checked | rank-27 survivors |
| --- | ---: | ---: | ---: |
| `2+2+2`, `rank(F)=4` | 332 | 3,451,140 | 0 |
| `4+2`, `rank(F)=3` | 1,352 | 14,054,040 | 0 |
| `6`, `rank(F)=1` | 288 | 2,993,760 | 0 |
| `6`, `rank(F)=2` | complete pivot/mate CSP | 92,274 mate branches | 0 |

For `2+2+2` and `4+2`, a complete generated-subspace cover proves that the
listed streams contain every derangement with border rank low enough to
participate in rank 27. Every labelled third-fibre perfect matching is then
tested. For type `6`, every minimum-border pair receives all `3 x 3` minor
tests, while the higher-border mechanism is covered by a joint
permutation/matching CSP.

The SHA-256 of `exact-results.json` is
`8878b40898ba9577ef01fb51ab5631632fb0e6bca3394c594b9c399d51385230`.

The scoped derived theorem is:

```text
Conditional on n3=4158, an edge of type 222, 24, or 6 has
rank_F7(K39) >= 28.
```

The all-odd endpoint type `3+3` is intentionally outside this package.
The separate package `attempts/wave43-type33-rank2/` derives the matching
type-`3+3` obstruction. Combining the two discovery lanes gives the
candidate endpoint theorem

```text
n3=4158  =>  rank_F7(M) >= 28,
```

or contrapositively,

```text
rank_F7(M)=27  =>  at least one induced triangular prism.
```

That combination remains a candidate until a clean-room verifier
independently reconstructs both lanes. It does not exclude the endpoint,
improve the general bound `n3<=4158`, construct a graph, or solve Conway-99.

## Reproduce

The complete deterministic replay is bounded and single-process. On the
recorded host it took about 326 seconds and kept more than 60% of physical
memory free.

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave43-rank28-motif\exact_check.py `
  --verify attempts\wave43-rank28-motif\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave43-rank28-motif -p "test_*.py" -v
```

See `proof.md` for completeness, `failed-routes.md` for retained negative
results, and `run-report.yaml` for the exact evidence boundary.
