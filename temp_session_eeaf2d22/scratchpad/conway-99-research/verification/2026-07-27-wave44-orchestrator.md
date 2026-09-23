# Waves 43--44 orchestrator decision

Date: 2026-07-27 UTC

## Decision

Publish the conditional theorem

```text
n3=4158  ==>  rank_F7(M)>=28
```

as `VERIFIED`. Publish the all-rank33 and branch-15 results as
`VERIFIED_SCOPED`. Publish the unrooted and aggregate rooted order-seven
systems as exact feasible relaxation controls. Do not present any of them as
a graph, endpoint construction, endpoint exclusion, strict general upper
bound, Conway-99 resolution, or novelty/priority result.

## Why the rank theorem is promoted

The verifier uses a separate implementation, reconstructs all endpoint local
matrices, exhausts both possible rank-27 mechanisms, and agrees on all
36 compared fields. It explicitly accepts planted witnesses for the two CSP
forms, so the zero-survivor conclusions are not vacuous.

All four endpoint local blocks have characteristic-seven rank at least 28.
Their principal-block embedding in the transported global matrix gives the
conditional global result. The ceiling 44 remains compatible, so the
endpoint stays open.

## Why the count systems are not promoted further

Both exact count witnesses are aggregate isomorphism-class multiplicities.
They do not assign types consistently to overlapping subsets. The rooted
system distinguishes one root or an ordered root pair but still averages
over all embeddings. Exact feasibility therefore proves only that these
linear relaxations cannot exclude the endpoint.

The first rooted discovery run produced a floating HiGHS `infeasible` status.
An exact integer witness refutes that output. The false result and its
correction are retained as a solver-calibration lesson; no solver exit code
is a certificate.

## Continuation

The most promising next routes are:

1. impose positive-semidefinite finite flag moment matrices and use exact
   rational quadratic cuts;
2. solve the complete three-way-matching plus compatible outside-graph `H`
   problem across the 264 rank-33 lifts;
3. add non-coordinate-anchored triangle cuts and proof-producing higher-order
   propagation to all 33 endpoint cases; and
4. derive a cross-block rank or orthogonal-geometry bridge that cannot be
   satisfied one local block at a time.

## Publication classification

```text
conditional endpoint rank_F7(M)>=28:     VERIFIED
all-rank33 necessary reduction:           VERIFIED SCOPED
branch-15 two-triangle clause family:      VERIFIED SCOPED
order-seven linear count relaxations:      EXACT FEASIBLE
endpoint proof coverage:                   0/33
upper bound below n3<=4158 in general:     NOT PROVED
target, novelty, and priority:              UNKNOWN
```
