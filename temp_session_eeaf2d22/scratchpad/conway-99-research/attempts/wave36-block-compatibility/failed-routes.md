# Retained failed and nondecisive routes

The frozen target in this lane is the conditional endpoint `n3=4158`.
Nothing below is evidence for existence or nonexistence.

## Full restricted-core sparse MILP

The Wave 35 restricted core has `183980` individually admissible triples
under the old induced-matching cut.  A sparse binary MILP used one variable
per triple and imposed:

- one use of each of the `60` allowed pairs in each fibre; and
- all three forced `12 x 12` cross-fibre concurrence matrices.

The model had `612` equality rows.  A zero-objective HiGHS run did not return
a result before the outer process timeout.  No partial output survived.
Classification: `FAILED_RUN`, not evidence.

## MiniCard native-cardinality attempt

The same `183980` triples were encoded with:

- exactly one selected triple for each fibre-0 pair;
- at most one use of every fibre-1 and fibre-2 pair; and
- at-most bounds equal to every required cross-concurrence entry.

Sixty selected rows and the fixed total cross incidences make all of the
at-most constraints exact.  The model built `672` native constraints over
`183980` variables.  MiniCard exited with code `1` during `solve_limited`
without a Boolean result or traceback.  This repeats the Wave 35 failure
mode.  Classification: `FAILED_RUN`, not evidence.

## Fixed Wave 35 pairwise certificate

Holding the published `X0-X1` edge permutation fixed leaves:

```text
3600 raw X2 choices
3266 choices after the old induced-matching cut
2939 choices after the new mixed-equation cut
```

The exact linear equality system on the `3266` old-cut choices is feasible
over the reals.  HiGHS returned an LP point with `361` nonzero fractional
coordinates and residual below `9e-13`.  Therefore no linear Farkas
contradiction exists for that formulation.

The same equality system is consistent over `GF(2)`, `GF(3)`, `GF(5)`, and
`GF(7)`; its row rank is `361` in each field.  Thus the most immediate modular
linear contradictions also fail.

A binary HiGHS run on the `3266` choices reached its `60` second limit with
no incumbent and no conclusion.

Finally, the strengthened `2939`-choice model was compiled with sequential
counter encodings:

```text
CNF variables including auxiliaries: 47601
CNF clauses:                        117574
solver:                             CaDiCaL 1.9.5
conflict budget:                    250000
result:                             UNKNOWN
restarts:                           1973
decisions:                          553730
propagations:                       293791545
observed wall time:                 60.1 seconds
```

The solver returned `None` at the budget.  Failure to find a model or a
refutation is not evidence.  Even a proved contradiction for this fixed
pairwise certificate would concern only that certificate, not all pairings
or all local cores.

## Boundary

The new mixed-equation cut, component-balance lemma, disconnected-pattern
constraints, and spectral transfer survive exact checks.  Simultaneous
60-block compatibility, a compatible `H`, endpoint exclusion, and
Conway-99 remain `UNKNOWN`.
