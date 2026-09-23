# Failed and bounded routes

## Pair-root order-eight covariance

The Wave150 vector exactly satisfies both centered pair-root covariance
blocks with equality. Independent verification confirms this is a true null
of that relaxation, not a numerical artifact.

## Treating the first separation as an endpoint proof

Invalid. The two exact directions refute only one rational count vector.
After both cuts were added, a different numerical point appeared on the
`h11=16632` slice and was reconstructed exactly.

## Confusing the Wave44 slice

The first Wave150 witness has `h11=8316` (`y=2079`). The first feedback point
has `h11=16632` (`y=4158`). Both lie in the frozen conditional endpoint
system. Replays and reports must state which slice is used.

## Trusting HiGHS status

The feedback status `optimal` is reconnaissance. Exact reconstruction, not
the solver exit status, establishes feasibility of the retained finite
system.

## Declaring unseparated blocks PSD

For blocks without a stored negative direction, small floating eigenvalues do
not prove positive semidefiniteness. They remain
`NUMERICALLY_NO_SEPARATION` unless an exact factorization or exact
nonnegative-pivot certificate is supplied.

