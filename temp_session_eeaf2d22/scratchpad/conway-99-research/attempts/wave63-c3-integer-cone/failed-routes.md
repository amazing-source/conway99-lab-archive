# Failed routes and retained boundaries

## More finite-field rank tests

Wave 61 already showed that every one of the 1,140 component triples passes
the full 630-pair parity-span test.  Repeating ranks over more primes would
again forget nonnegative multiplicity and distinctness, so Wave 63 moved to
the rational cone and integer semigroup.

## Pair-coordinate Farkas separation

No such separation exists on the tested 74 lanes: each has an exactly
replayed nonnegative rational witness for all 630 pair coordinates.  In
fact, the independent checker finds all recorded coefficients at most one.
Consequently no valid linear inequality in only these pair coordinates can
separate the target from the allowed-column polytope on a tested lane.

This says nothing about the other 1,066 unordered triples.

## Independent coefficient rationalization

Rounding each floating LP coefficient separately with denominators up to
one million did not replay the exact equations.  The basic solutions have
large exact denominators (up to 340 bits in this run).  The retained method
instead solves a square integer minor exactly with FLINT/Dixon and replays
all equations.

## Binary MILP

The first minimum-support lane has 15,936 binary variables.  A single
30-second HiGHS MILP run reached its time limit without a model or
certificate.  This bounded nonhit remains `UNKNOWN`.

Running many memory-heavy MILP instances in parallel was rejected by the
resource protocol.  The final run used one solver process and stayed above
54 percent free physical memory.

## Sparse triple-coordinate duals

The pair target determines only the marginal identity

```text
sum_{k not in {i,j}} T_ijk = 4 G_ij.
```

Adding only those implied equalities cannot cut off an exact pair-cone
witness.  A useful third-order route must retain a common nonnegative
integral tensor, column distinctness, and realizability by the same sixty
six-sets.  No exact sparse violated inequality with those stronger variables
was found in this package.
