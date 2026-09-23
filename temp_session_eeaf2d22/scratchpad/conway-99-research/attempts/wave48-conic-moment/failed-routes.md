# Wave 48 failed and bounded routes

## Direct common-identity margin

Subtracting `t I` from every full moment matrix is not a useful strict-margin
objective. The Wave 45 ordered-edge and ordered-nonedge matrices are
identically rank one, and all other families also have universal kernel
directions on the Wave 44 affine space. This artificially forces `t <= 0`.

The retained exact facial calculation resolves this formulation error.

## Floating status disagreement

Clarabel and SCS returned boundary-scale candidates with different residual
sizes and both small negative probabilities/eigenvalues. Clarabel also marked
its solutions `optimal_inaccurate`. None is retained as a feasible witness or
an infeasibility signal.

## Margin-zero and log-det follow-up

A facially reduced margin-zero feasibility run followed by a log-det
analytic-center objective exceeded the bounded wall-time twice. The exact
targets were stopped explicitly; no result artifact or candidate was emitted.
Host free memory remained far above 20%.

## Rational dual reconstruction

No rational dual reconstruction was attempted because no solver returned a
stable, significantly negative separating margin. Reconstructing noise at
`1e-6` through `1e-10` would risk manufacturing a false certificate.

## CVXOPT

CVXOPT was not installed in the environment. No installation or additional
memory-heavy solve was justified by the already inconsistent boundary-scale
diagnostics.
