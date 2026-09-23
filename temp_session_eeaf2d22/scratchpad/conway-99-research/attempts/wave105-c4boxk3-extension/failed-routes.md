# Wave 105 retained boundaries

## Aggregate graphicality

The six separate Erdős-Gallai and Gale-Ryser tests leave 34 aggregate
degree rows. Passing these tests does not show that the six type graphs can
be realised simultaneously, much less that all pair codegrees are correct.

## Linear block feasibility

The archived 549-edge witness satisfies degrees and `DP=2J-P-PH`.
It does not satisfy or test the quadratic outside-pair equation. Linear
feasibility therefore blocks any attempted exclusion using only the first
two block equations.

## MiniCard linear-witness wrapper

The untimed MiniCard wrapper exited abnormally on Windows while extracting a
linear witness. The same 0-1 equality problem was solved with SciPy/HiGHS
and the result was checked directly. The wrapper failure is a software
event, not mathematical evidence.

## Bounded full search

Four complete-domain encoding branches were run for 45 seconds each. Every
run timed out and is recorded as `UNKNOWN`. No solver exit code has been
promoted to a theorem, and no uncertified UNSAT result was obtained.

## Local motif versus global graph

`C4 box K3` is a parity-null local configuration. Its survival through the
linear extension layer does not show that it extends to 99 vertices. It
also does not show that every hypothetical target must contain the motif.
