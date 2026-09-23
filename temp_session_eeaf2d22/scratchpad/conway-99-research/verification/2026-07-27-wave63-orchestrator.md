# Waves 60--63 orchestrator decision

```yaml
role: orchestrator
date_utc: 2026-07-27T22:20:38Z
git_commit: 81c8d45426938ea8490af55d81f05b7c2ad99035
claim_label: VERIFIED
scope: publication decision for conditional alternative-space Waves 60--63
inputs:
  - verification/2026-07-27-wave59-integration-audit.md
  - verification/wave60-c3-incidence-design/audit.md
  - verification/wave61-c3-finite-field/audit.md
  - verification/wave62-terwilliger-sdp/verification-report.md
  - verification/wave63-c3-integer-cone/verification-report.md
  - verification/2026-07-27-wave63-integration-audit.md
method: enforce discovery-verifier separation, exact certificate scope, and the unresolved endpoint wall
outputs:
  - verification/2026-07-27-wave63-orchestrator.md
limitations:
  - no endpoint case is closed
```

## Decision

Publish the independently verified component census, safe coordinate-orbit
reduction, finite-field null results, exact one-root invariant-SDP null
result, and 74 rational pair-cone witnesses. Publish both verifier
clarifications prominently.

Do not promote:

- binary rank or finite-field feasibility to an integer design;
- the cubic margin identity to existence of a nonnegative integral tensor;
- scaffold-averaged SDP feasibility to a residual graph;
- rational coefficients in `[0,1]` to zero-one columns;
- a bounded binary MILP timeout to nonexistence; or
- any conditional endpoint restriction to a strict global upper bound.

## Continuation

The pair-coordinate cone has reached a clean wall. The next construction lane
must retain zero-one semigroup membership and third/higher overlaps. In
parallel, the rooted residual graph should be recoded as a transition system
on the 84 edges of `K14-7K2` plus 140 selected three-edge matchings. This
separates the linear exact-cover layer from the genuinely nonlinear residual
common-neighbor constraints and supports proof-producing lazy cuts. A second
proof lane should retain two-root rather than one-root correlations; the
one-root invariant SDP is now exactly known to be too coarse.

## Status wall

```text
accepted Waves 60--63 finite claims: VERIFIED SCOPED
endpoint proof coverage:              0/33
strict upper bound below 4158:        NOT PROVED
rigorous interval:                    708 <= n3 <= 4158
n3=4158 / graph / Conway-99 / novelty: UNKNOWN
```
