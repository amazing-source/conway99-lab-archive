# Waves 90--100 orchestrator decision

```yaml
role: orchestrator
date_utc: 2026-07-28T03:09:16Z
git_commit: cbb91d1fb7e0f55f9d62a124cd4e4bfbfe739fee
claim_label: VERIFIED
scope: publication decision for the rooted norm-14, characteristic-seven exterior, and scalar-theta routes
inputs:
  - verification/wave90-short-vector-count-upper/audit.md
  - verification/wave94-general-n3-norm14-bound/audit.md
  - verification/wave97-f7-exterior-matroid/audit.md
  - verification/wave99-transition-pair-moment/verification-report.md
  - verification/wave100-general-pair-moment/verification-report.md
  - verification/2026-07-28-wave100-integration-audit.md
method: publish independently reconstructed scoped theorems, retain the provenance correction, and label the finite scalar probe UNKNOWN
outputs:
  - verification/2026-07-28-wave100-orchestrator.md
limitations:
  - no upper bound on the norm-16 or norm-18 shell is proved
  - no rank row, endpoint, or target graph is excluded
```

## Decision

Publish as independently verified:

- the prism-free first-moment bound `N14<=5544`;
- the general first-moment bound
  `N14<=floor((55440-4*n3)/7)`;
- the endpoint pair-moment bound `N14<=4950`;
- the general pair-moment theorem
  `N14<=2*floor((55440-5*n3)/14)`;
- the additional rank-28 consequence
  `407*N16+43*N18>=2165002`; and
- the scoped Wave 97 Schur, compound-code, Smith, generalized-weight, and
  orthogonal-orbit formulas.

Retain the Wave 97 provenance correction explicitly. Its quadratic circuit
and `R*R=1_perp` are verified but were already implicit in Wave 51; they are
not later project discoveries.

Publish Wave 98 only as an `UNKNOWN` finite computational report. Its
degree-1,000 positive prefix does not establish all-orders positivity or a
geometric realization.

Do not promote:

- an `N14` upper bound to an upper bound on `n3`;
- the weighted rank-28 inequality to a contradiction without an `N16` or
  `N18` upper bound;
- abstract code, Smith, or orthogonal-orbit data to a graph;
- finite scalar positivity to a lattice theta series; or
- new-to-project status to literature novelty.

## Strategic consequence

The rank-28 prism-free row now has a stronger concrete squeeze:

```text
N14 <= 4950
407*N16+43*N18 >= 2165002.
```

The highest-leverage continuation is a coordinate-sensitive upper bound on
the norm-16 and norm-18 shells. In parallel, Wave 100 exposes a different
combinatorial lane: constrain the full rooted-prism incidence vector
`(f_o)` through parity, cycle-space, or adjacency-algebra identities. Its
present scalar sum and box constraints are already sharp.

## Status wall

```text
general N14 upper bound:                 VERIFIED
matching N16/N18 upper bound:            UNKNOWN
rank r=28:                               UNKNOWN
all target graphs:                       UNKNOWN
strict upper bound below 4158:           NOT PROVED
rigorous interval:                       708 <= n3 <= 4158
Conway-99 / novelty:                     UNKNOWN
```
