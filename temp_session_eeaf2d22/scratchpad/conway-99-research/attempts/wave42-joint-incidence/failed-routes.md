# Wave 42 failed routes and exact boundary

## Generic MILP timeout

A 118,718-variable binary feasibility model for the forced `BB^T` equations
found no incumbent in a bounded 45-second run. A timeout is not evidence of
infeasibility and is not used in any claim.

## One fixed staged extension

An exact SAT formulation found a concurrence-preserving pairing for the
first two fibres. Holding one such first-stage model fixed, its third-fibre
extension was reported unsatisfiable. No proof was retained, and the other
first-stage models were not exhausted.

Classification: **diagnostic only / non-evidence**. It does not prove that
the emitted two-fibre certificate is unextendable, much less that no `B`
exists.

## Local optimization

Bounded permutation searches approached but did not reach all three
cross-fibre concurrence matrices simultaneously. Near solutions, objective
values, and timeouts are not certificates and are omitted from the theorem
artifact.

## Why the two-fibre certificate is only a positive control

The retained 60-entry certificate realizes `Q_01` exactly. It contains no
fibre-2 pairs, so it does not define a six-point block system, a matrix `B`,
or any outside graph `H`.

## Remaining complete finite problem

The exact checker leaves 45,032 individually necessary six-sets. A complete
`B` must select sixty subject to all three pair-set partitions and all 432
cross-fibre concurrence entries. A compatible `H` must then satisfy the
mixed equation, eight-regularity, and every pointwise `YY` common-neighbor
equation.

No full `B`, `H`, 99-vertex graph, contradiction, endpoint exclusion, upper
bound below 4158, solution, or novelty claim is supplied.

