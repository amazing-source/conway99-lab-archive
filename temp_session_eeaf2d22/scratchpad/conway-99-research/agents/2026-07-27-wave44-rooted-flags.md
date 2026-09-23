# Wave 44 Proof Agent A: rooted flag checkpoint

```yaml
role: proof_a
date_utc: 2026-07-27T16:27:02Z
git_commit: e28f90464d00b98d37672b0b2b23dba15399a6f2
claim_label: DERIVED
scope: >
  Exact rooted order-seven flag equations at the conditional prism-free
  endpoint, their strict rank gain over the unrooted deck, and an exact
  feasible positive control.
```

## Result

The smallest rooted extension begins with seven vertex-degree rows and adds
all ordered edge/nonedge neighborhood signatures. For edge roots the other
vertices have category sizes `1,12,12,72`; for nonedge roots they have
`2,12,12,71`.

The system has:

```text
unrooted rows:      81
vertex-root rows:    7
edge-root rows:     36
nonedge-root rows:  46
total:             170
variables:         209.
```

Exact finite-field ranks are

```text
81 -> 82 -> 87 -> 93
```

over `F_101`, `F_103`, and `F_107`. The Wave 43 unrooted witness violates
`7/7`, `36/36`, and `46/46` new rows, respectively. Thus the rooted system is
strictly stronger and genuinely detects missing overlap information.

## Exact feasibility

The stronger aggregate system still survives:

```text
h11:                 16632
positive classes:       91 / 208
maximum count:       3222792342
exact residuals:          0 / 170
total:              14887031544 = binom(99,7).
```

Witness SHA-256:
`9be153b2487c3e07e20bffeb7ee6c890e69caa6e8d6b6e2936fbc5d8927bd5b9`.

Z3 discovered the vector, but the certificate checker uses only exact Python
integer arithmetic. The full 170-row coefficient system is frozen in
machine-readable JSON, with separate base, vertex, edge, nonedge, and
combined canonical SHA-256 commitments. A second standard-library-only
checker replays those hashes and all witness residuals without importing the
construction code. Eleven hostile and structural tests cover coefficient
partitions, family totals, rank increments, count mutation, sign mutation,
right-hand-side mutation, support replay, and the status wall.

## Corrected solver chronology

A preliminary SciPy/HiGHS MILP call reported infeasibility. The exact witness
refutes it, so that status is retained only as a floating numerical false
negative. The continuous LP was also numerically feasible. Neither status is
evidence.

## Mathematical boundary

The result is a rigorous reduced formulation and positive control:

```text
rooted aggregate order-seven system: EXACT FEASIBLE
endpoint n3=4158:                    UNKNOWN
strict upper bound below 4158:       NOT PROVED
graph construction:                 NONE
Conway-99:                           UNKNOWN.
```

The missing bridge is a positive-semidefinite matrix of joint densities for
pairs of rooted flags with exact gluing semantics. First moments alone do not
assign compatible types to overlapping subsets. The next verifier should
reconstruct all rooted coefficients independently, replay the 91-support
witness, and mutate row orientation/sign/category sizes before any promotion.
