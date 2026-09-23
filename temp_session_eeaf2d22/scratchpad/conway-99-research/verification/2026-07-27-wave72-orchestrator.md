# Waves 69 and 72 orchestrator decision

```yaml
role: orchestrator
date_utc: 2026-07-27T23:34:54Z
git_commit: 5f497b545c536de90a1a557c51b53f041fecf7db
claim_label: VERIFIED
scope: publication decision for restricted order-11 and Cayley exclusions
inputs:
  - verification/wave72-order11-automorphism/audit.md
  - verification/wave69-cyclic-cover-shift/audit.md
  - verification/2026-07-27-wave72-integration-audit.md
method: combine only separately verified implications and preserve the unrestricted symmetry wall
outputs:
  - verification/2026-07-27-wave72-orchestrator.md
limitations:
  - asymmetric targets remain possible
```

## Decision

Publish:

- the exact order-11 fixed-point theorem;
- all seven quotient row shapes and three diagonal cases;
- the label-complete and canonical zero-candidate censuses;
- exclusion of every order-11 automorphism;
- exclusion of every vertex-transitive realization; and
- the independent Fourier exclusion of every Cayley realization.

Do not promote:

- a restricted symmetry exclusion to unrestricted nonexistence;
- diagonal sorting to an automorphism assumption;
- the canonical search alone to proof completeness;
- a solver nonhit in place of the label-complete tree;
- exclusion of order 11 to exclusion of other automorphism orders; or
- project-local derivations to literature novelty.

## Strategic consequence

Highly symmetric construction spaces are now closed. Continued construction
search should not impose transitivity, Cayley structure, or an order-11
action. The unrestricted attack should stay in the labelled rooted-design,
lattice/modular-form, and proof-producing SAT spaces.

## Status wall

```text
order-11 / vertex-transitive / Cayley targets: EXCLUDED
asymmetric targets:                            UNKNOWN
endpoint proof coverage:                       0/33
strict upper bound below 4158:                 NOT PROVED
rigorous interval:                             708 <= n3 <= 4158
unrestricted Conway-99 / novelty:             UNKNOWN
```
