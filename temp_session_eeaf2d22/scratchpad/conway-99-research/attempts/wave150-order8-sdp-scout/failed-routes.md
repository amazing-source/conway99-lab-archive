# Wave 150 failed routes

## Uncentered SDP

SCS and Clarabel put the uncentered common PSD margin near zero and produced
nearly rank-one moment matrices.  This suggested the centered covariance
face but gave no bound.

## Floating centered margin

SCS and Clarabel returned centered margins of opposite sign at roughly
`1e-9` or smaller.  Neither status is evidence for feasibility or
infeasibility.

## HiGHS bound/presolve false infeasibility

HiGHS initially reported the rank-one and diagonal-only linear systems
infeasible when CVXPY encoded nonnegativity as column bounds and presolve was
enabled.  The same mathematical systems became feasible to about `1e-13`
when nonnegativity was written as explicit inequalities and presolve was
disabled.

The infeasible statuses and zero dual rays are rejected.  They are retained
because this is a concrete warning against treating a solver exit code as a
certificate in a highly degenerate model.
