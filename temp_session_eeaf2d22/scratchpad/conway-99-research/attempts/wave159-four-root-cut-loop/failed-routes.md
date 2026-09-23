# Failed and bounded routes

## Relative-path evaluator invocation

The first four-root reevaluation completed its mathematical work but failed
while packaging the output because the frozen Wave152 evaluator calls
`Path.relative_to(ROOT)` on the supplied witness path. A repository-relative
argument is not a subpath of the evaluator's absolute `ROOT` object.

No output artifact was written by that failed invocation. The evaluator was
rerun unchanged with an absolute witness path and completed successfully.
Wave152 remained immutable.

## Numerical feasibility is not proof

The tight HiGHS scout reported `optimal` with residuals of order `1e-14`, and
the two fresh normalized cuts were active to floating precision. This was
used only to choose a support and active rows. The solver exit status was not
treated as a certificate; exact rational reconstruction and replay were
required.

## Another cut-loop iteration was stopped

The fifteen-cut exact pseudowitness is separated again by root-mask-3 and
root-mask-12 covariance directions. No seventeenth-cut scout or solve was
started. Repeating the same loop may continue producing feasible
pseudowitnesses without resolving the full matrix constraint, so the next
lane should target whole-block structure, exact facial reduction, or a
rational dual certificate.
