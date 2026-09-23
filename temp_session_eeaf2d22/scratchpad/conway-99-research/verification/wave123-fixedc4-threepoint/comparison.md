# Discovery-to-verifier comparison

Verdict: `VERIFIED_SCOPED`; no correction was required.

| Claim | Discovery | Independent result |
|---|---:|---:|
| all-40 leverage failures | 46 | 46 |
| first-26 leverage failures | 6 | 6 |
| alternate-26 diagonal failures | 0 | 0 |
| alternate-26 maximum | `1217462.../2744155...` | exact match |
| centered endpoint blocks | 312 | 312 |
| within-block degree-two blocks | 468 | 468 |
| cross-block degree-two blocks | 1,560 | 1,560 |
| total rooted PSD blocks | 2,340 | 2,340 |
| pair-overlap tuples | 52 | 52 |
| tuples splitting by triple intersection | 28 | 28 |
| minimum tested signed triple norm | 22 | 22 |
| graph-valued invalid coordinate pairs | 352 | 352 |

The verifier checked 1,581,840 exact feature-Gram entries.  Each matrix is
PSD by its displayed rational or sparse coordinate factorization.

The sealed heuristic telemetry reports 30 restarts and 14,070 trial
removals.  The verifier did not replay that heuristic because no exhaustive
certificate or complete trace is present.  This is not a correction: the
discovery package already labels the search nonexhaustive and forbids
negative inference.

The 352 failures refute only the displayed explicit subset.  Code-only
three-point PSD and diagonal leverage do not represent one common target
adjacency.
