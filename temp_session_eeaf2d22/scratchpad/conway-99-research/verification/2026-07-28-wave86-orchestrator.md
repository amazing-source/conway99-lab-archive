# Waves 80--86 orchestrator decision

```yaml
role: orchestrator
date_utc: 2026-07-28T00:44:19Z
git_commit: fd88280eb25aecd8c40d9e82f572813f1c850ec5
claim_label: VERIFIED
scope: publication decision for the coding, labelled-design, integral-orthogonal, SAT-null, and full level-seven modular-form routes
inputs:
  - verification/wave80-f7-overlattice-code/audit.md
  - verification/wave81-norm16-labeled-design/verification-report.md
  - verification/wave81-norm16-graphical-refinement/verification-report.md
  - verification/wave82-seidel-orthogonal/verification-report.md
  - verification/wave86-level7-exact/audit.md
  - verification/2026-07-28-wave86-integration-audit.md
method: publish independently reconstructed scoped theorems, retain the source correction, and label the solver portfolio UNKNOWN
outputs:
  - verification/2026-07-28-wave86-orchestrator.md
limitations:
  - no rank row or short-vector branch is excluded
```

## Decision

Publish as independently verified:

- the `[99,44]_7` evaluation code, exact hull, orthogonal quotient, and
  support-five dual exclusion;
- the complete norm-16 anchored support and deficiency-coupling censuses;
- the separately checked graphicality refinement from 50 to 47 degree rows;
- the exact integral-orthogonal equivalence and conditional Smith form; and
- the full level-seven modular-form lower bound
  `N14+N16+N18>=5868` in the rank-28 row.

Publish Wave 84 only as an `UNKNOWN` computational report. Retain the Wave 86
literature correction explicitly: the mathematical Fricke factors are
verified, but they must be derived from the cited source's normalization and
preceding transformation equation rather than copied from its printed
combined equation.

Do not promote:

- an abstract orthogonal code or Smith profile to a realized graph;
- marginal norm-16 flows or graphical degree rows to a simultaneous outside
  graph;
- a scalar formal modular pair to a lattice theta pair;
- a 900-second solver timeout to evidence for either outcome;
- the rank-28 lower bound to exclusion without a strict compatible upper
  bound; or
- new-to-project status to literature novelty.

## Strategic consequence

The rank-28 case now has a precise squeeze target:

```text
full modularity:  N14+N16+N18 >= 5868
packing/design:   each shell has rigid labelled support constraints
```

The highest-leverage continuation is therefore a proof-producing upper bound
on the combined three shells, not another scalar theta relaxation. In
parallel, the characteristic-seven quotient and the exact integral-orthogonal
matrix provide independent local-global spaces in which a contradiction could
surface.

## Status wall

```text
q=16 / r=28 combined-shell lower bound:  VERIFIED
matching strict upper bound:             UNKNOWN
rank r=28:                               UNKNOWN
all target graphs:                       UNKNOWN
strict upper bound below 4158:           NOT PROVED
rigorous interval:                       708 <= n3 <= 4158
Conway-99 / novelty:                     UNKNOWN
```
