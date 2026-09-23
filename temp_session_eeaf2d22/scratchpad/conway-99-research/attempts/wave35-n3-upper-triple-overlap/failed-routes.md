# Retained failed and bounded Wave 35 construction routes

All entries below concern the conditional endpoint

```text
n3=4158, equivalently zero induced triangular prisms.
```

None is evidence for existence or nonexistence.

## Full rooted branch scouts

The exact endpoint units immediately reject seven of the twelve previously
verified normalized `N3` branches. The five surviving branches
`4,5,8,10,12` were each passed to the compact native-cardinality model with
a 100,000-conflict budget.

Every branch returned `BUDGET_UNKNOWN`. No model, UNSAT result, formula
export, or proof trace was produced. The retained JSON is a transcription of
the live console record rather than a raw solver log.

## Fractional local-extension controls

The ordinary LP relaxation of all four 27-vertex seed systems is feasible.
This only shows that a particular linear obstruction fails. Fractional type
multiplicities do not describe 72 vertices and do not construct a graph.

## Integer local-extension scouts

The four 5,500-variable nonnegative-integer models each stopped after a
60-second limit without an incumbent. A reduced 5,184-binary-variable model
for partition `2+2+2` stopped after 120 seconds without an incumbent.

These statuses are `TIMEOUT_UNKNOWN_NO_INCUMBENT`, not UNSAT.

## Native-cardinality benchmark

One `2+2+2` Gluecard benchmark stopped at its conflict budget with
`BUDGET_UNKNOWN`. It was not calibrated as a proof-producing route and
emitted no proof.

## Boundary

The 84 forbidden residual edges, five surviving normalized branches, four
local seed partitions, and deterministic OPB instances remain useful exact
reductions. The endpoint and Conway-99 both remain `UNKNOWN`, and the general
upper bound remains `n3<=4158`.
