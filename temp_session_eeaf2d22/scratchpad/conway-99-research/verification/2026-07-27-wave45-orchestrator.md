# Wave 45 orchestrator decision

```yaml
role: orchestrator
date_utc: 2026-07-27T17:02:06Z
git_commit: 4636864ffc6310acaa71a41fff239a24e28404fc
claim_label: VERIFIED
scope: publication decision for immutable rooted-flag checkpoint v1
inputs:
  - verification/wave45-flag-moment/verification-report.md
  - verification/2026-07-27-wave45-integration-audit.md
method: enforce discovery-verifier separation and the endpoint status wall
outputs:
  - verification/2026-07-27-wave45-orchestrator.md
limitations:
  - this decision cannot promote a timeout or a finite cut sequence to UNSAT
```

## Decision

Publish the finite rooted-flag moment construction, the exact refutation of
the two stored aggregate witnesses, and the independently replayed immutable
17-cut checkpoint.

Do not publish any of the following as a theorem:

- endpoint infeasibility;
- a strict upper bound `n3<4158`;
- solver `unknown` or timeout as nonexistence evidence;
- mutable post-checkpoint search state;
- novelty or priority.

## Research direction

The rooted moment space is retained as the primary proof lane because it is
the first count-space strengthening that rejects every supplied exact
aggregate witness. The next decisive object must be one of:

1. a finite exact separating family whose integer system has a checked
   proof-producing infeasibility certificate;
2. an exact positive-semidefinite count witness, which would close this
   particular relaxation as feasible;
3. a stronger rooted/order-eight moment system;
4. a bridge from aggregate moments to the explicit `B/H` completion or to
   multiple overlapping rank blocks.

Coding-theoretic, polynomial-calculus, and signed-matrix/star-complement
reformulations remain parallel scouts. They are useful only if they introduce
new compatibility constraints.

## Status wall

```text
stored count witnesses:        REFUTED
finite checkpoint:             VERIFIED INCOMPLETE
full moment region:            UNKNOWN
endpoint proof coverage:       0 / 33
rigorous interval:             708 <= n3 <= 4158
Conway-99:                     UNKNOWN
```

