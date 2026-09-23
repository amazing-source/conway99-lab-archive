# Wave 43 failed routes and null diagnostics

None of the entries below is mathematical evidence for nonexistence.

## Direct six-set formulation

The first exact model used one Boolean per Wave 42 candidate. Sequential
counter expansion gave `1,144,460` variables and `2,872,716` clauses. A
CaDiCaL run remained unresolved after `20,000` conflicts. Its observed peak
working set was approximately `1,010 MiB`.

This formulation is exact, but the compact pairing formulation strictly
improves its representation and supersedes it for continuation.

## Compact pairing formulation

The exact compact model has `8,456` semantic variables, `82,532` variables
including auxiliaries, and `338,528` clauses.

Bounded diagnostics:

- CaDiCaL: unresolved after `700,004` conflicts and `65.79` seconds;
  externally observed peak working set `145 MiB`, minimum host-free memory
  `69.03%`.
- Glucose: unresolved after `500,155` conflicts and `68.32` seconds;
  externally observed peak working set `127.6 MiB`, minimum host-free memory
  `61.84%`.
- Minicard seed `0`: unresolved after `969,623` conflicts and `55.14`
  seconds; peak working set `302.3 MiB`, minimum host-free memory `67.82%`.
- Minicard seed `1`: unresolved after `890,780` conflicts and `55.08`
  seconds; peak working set `296.3 MiB`, minimum host-free memory `62.03%`.
- Minicard seed `2`: unresolved after `888,760` conflicts and `55.00`
  seconds; peak working set `308.5 MiB`, minimum host-free memory `62.24%`.

The Minicard binding crashed on the larger direct formulation, and the
Kissat Python binding crashed on the compact formulation. These binding
failures were isolated, left no worker processes, and are not retained as
claim evidence.

## Longer compact CaDiCaL scout

Variable-numbering seed three was run to a five-million-conflict boundary:

```text
conflicts:       5000000
decisions:      21839078
propagations: 2391245003
restarts:         163357
status:       INTERRUPTED
```

The retained result is
`solve-result-pairing-cadical-seed3-c5000000.json`. It contains no model and
no UNSAT proof, so it is `UNKNOWN`.

## Sparse exact MILP formulation

A second encoding uses one binary variable per retained six-set and imposes
all constraints as 612 sparse equalities:

```text
45032 variables
180 exact pair-partition rows
432 exact cross-fibre Gram rows
675480 nonzero coefficients.
```

The model is exact, not a relaxation. A 600-second zero-objective HiGHS run
returned no incumbent and no negative certificate. The retained
`solve-result-milp-t600.json` is therefore also `UNKNOWN`.

## Exact remaining boundary

A complete search must terminate on the compact exact model. A negative
result is publishable only with a frozen DIMACS instance, a proof trace, and
an independently replayed proof checker. A positive result is publishable
only with the sixty selected triples and independent reconstruction of all
pair partitions, all cross-fibre concurrences, and all local feasibility
filters.

No such terminal certificate was obtained.
