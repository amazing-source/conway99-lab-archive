# Wave 148 retained boundaries

## No numerical feasibility run

The package emits exact, solver-neutral rows only.  No SDP or LP feasibility
status was requested from a numerical solver, so there is no reconnaissance
result to interpret or rationalize.

## Necessary does not mean realizable

The marked rows enforce degree and common-neighbor extension counts between
orders seven and eight.  They do not impose every higher overlap and do not
construct compatible adjacency choices on 99 vertices.

## Zero-capacity rows

There are 893 ordered-pair types for which all allowed common neighbors are
already present inside the seven-set.  Their left coefficient and exact right
side are both zero.  They are consistency checks, not contradictions.

## First test failure

The retained test-only sparse-zero issue and repair are recorded in
`failed-runs.md`.  No mathematical row or stored artifact changed.

## Status

```text
marked rows:                  DERIVED
independent verification:    PENDING
combined Wave147/148 solve:   NOT RUN
strict n3 upper bound:        UNKNOWN
rational dual certificate:   NOT OBTAINED
Conway-99:                    UNKNOWN
```

