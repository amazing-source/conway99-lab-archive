# Waves 96 and 107--116 orchestrator decision

```yaml
role: orchestrator
date_utc: 2026-07-28T04:29:10Z
git_commit: f07565e59de8b9b5b53280896e85fde3387e4f3e
claim_label: VERIFIED
scope: publication decision for the C4-incidence, norm-20, conditional motif spectrum/projector/search, and corrected Jacobi-theta routes
inputs:
  - verification/wave96-norm16-norm18-upper/verification-report.md
  - verification/wave107-c4boxk3-spectrum/report.md
  - verification/wave109-c4boxk3-local-projector/report.md
  - verification/wave110-c4boxk3-symmetry-sat/verification-report.md
  - verification/wave112-c4-short-vector-incidence/verification-report.md
  - verification/wave116-c4-jacobi-theta/verification-report.md
  - verification/2026-07-28-wave116-integration-audit.md
method: publish only independently reconstructed scoped results, retain the invalid-small-index correction and all UNKNOWN solver outcomes, and separate the Wave 118 subjective estimate from mathematical evidence
outputs:
  - verification/2026-07-28-wave116-orchestrator.md
limitations:
  - no graph or nonexistence proof is produced
  - no rank row or prism-free endpoint is excluded
  - no strict n3, N16, or N18 upper bound is proved
```

## Decision

Publish as independently verified:

- the exact four-cycle count, short-support incidence minima, and fixed-cycle
  partition;
- the weighted cap-25 implication and the 80-point cross-polytope null
  control;
- the norm-20 `10+10` graph dictionary and cap-24 implication;
- the conditional outside spectrum and local characteristic-seven lattice;
- the shared-potential simultaneous row-lex theorem and complete branch
  coverage; and
- the corrected lattice-compatible aggregate Jacobi reduction and exact
  coefficient target.

Publish the four fresh SAT runs only as `UNKNOWN_TIMEOUT`. Do not promote a
timeout to search evidence.

Publish the Wave 118 probability report as a subjective strategy assessment,
not as a mathematical or empirical claim.

## Strategic decision

The pointwise cap program remains useful as a crisp falsifiable target, but
its Euclidean relaxation is too loose. Allocate the main effort to
coordinate-sensitive aggregate bounds:

- the corrected `K/L` Jacobi pair;
- degree-32 harmonic-theta moments with an exact PSD interpretation;
- vector-valued discriminant-code theta components; and
- proof-producing local extension constraints that import nonlinear
  common-neighbor compatibility.

The conditional motif lane remains a secondary exact-search target. Safe
symmetry now reduces redundancy, but bounded reruns have not changed its
evidence status.

## Status wall

```text
pointwise cap 25 / cap 24:  NOT PROVED
Jacobi aggregate upper:     NOT PROVED
all surviving rank rows:    UNKNOWN
full motif extension:       UNKNOWN
strict n3 upper bound:      NOT PROVED
rigorous interval:          708 <= n3 <= 4158
Conway-99 / novelty:        UNKNOWN
```
