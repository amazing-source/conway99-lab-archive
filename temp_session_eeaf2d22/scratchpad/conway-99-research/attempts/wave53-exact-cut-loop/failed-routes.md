# Wave53 failed and bounded routes

## Numerical infeasibility is not a certificate

During development, an unsealed fourth-cut extension selected a dense Wave45
vertex cut against the terminal witness. HiGHS reported the augmented LP
infeasible. A separate numerical Farkas-support LP then returned a purported
one-generator ray whose coefficient residual was approximately
`7.431e-10`.

Exact reconstruction rejected it: the single normalized equation was not a
constant identity, its variable coefficients did not vanish, and no exact
nonnegative multiplier system was obtained. Neither solver status nor this
near-ray is retained as mathematical evidence.

This is also a useful conditioning warning. The proposed fourth cut has 208
nonzero coefficients and very large exact magnitudes. Row normalization can
make small but nonzero coefficients fall close to a floating feasibility
tolerance.

Status: **UNKNOWN**, excluded from `exact-result.json`.

## Full-PSD convergence

All 32 matrices remain exactly indefinite at each of the four retained
rational witnesses. Thus the three selected cuts do not find a PSD-feasible
aggregate point and do not show that one exists. Continuing one direction at
a time could require many cuts or a different facial/dual formulation.

Status: bounded nonconvergence, not a proof of infeasibility.
