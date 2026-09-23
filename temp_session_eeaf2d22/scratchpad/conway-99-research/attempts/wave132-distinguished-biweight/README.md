# Wave 132: distinguished-row biweight projection

Published claim labels: `DERIVED` and `CANDIDATE`. Integral and full-genus
statuses remain `UNKNOWN`. Independent
verification is required.

This wave retains exact pair compositions involving the 99 distinguished
weight-14 neighborhood rows `r_u` and the 99 distinguished weight-15
closed-neighborhood rows `q_u`.

The ordered pair tables are forced:

```text
r_u,r_v: intersection 14 / 1 / 2
           counts       99 / 1386 / 8316

q_u,q_v: intersection 15 / 3 / 2
           counts       99 / 1386 / 8316

r_u,q_v: intersection 14 / 2
           counts       99 / 9702.
```

For every image word `x` of weight `w`, the 99 intersections with
neighborhood rows obey

```text
sum counts = 99,
sum intersection sizes = 14w,
number of odd intersections = w.
```

This is already strictly stronger than ordinary MacWilliams.  An odd
intersection is at most 13 and an even one at most 14, so

```text
14w <= 13w+14(99-w) = 1386-w.
```

Hence every even image weight satisfies `w<=92`, forcing

```text
A94=A96=A98=0.
```

The sealed Wave131 rational witness has `A98>0`, so that particular
ordinary-enumerator point is exactly refuted.

The stronger low-degree system remains rationally feasible.  A new exact
witness satisfies:

- all 200 forward/inverse ordinary MacWilliams rows;
- the Wave131 forced low-weight bounds and dual distance 15;
- `A94=A96=A98=0`;
- all four distinguished split systems: image/neighborhood, dual/closed,
  and both mixed directions;
- exact row sums, first moments, parity counts, intersection ranges, and
  the forced pair tables above.

The witness has rational coefficients and is not a code.  A hard-bounded
integral scout ended `UNKNOWN_HARD_TIMEOUT`; this proves nothing.

The full genus-two system was not materialized.  It has 171,700 raw
four-composition states, 42,925 states after imposing even weights on
`C x C`, and 7,803 `GL(2,2)` orbits.  Its partial-Hadamard transform and
cross-root coupling are the next boundary.

No binary code, adjacency matrix, graph, rank exclusion, or Conway-99
resolution is claimed.  Novelty remains `UNKNOWN`.

## Reproduce

```powershell
python -B attempts\wave132-distinguished-biweight\exact_check.py `
  --verify attempts\wave132-distinguished-biweight\exact-results.json

python -B -m unittest discover `
  -s attempts\wave132-distinguished-biweight -p "test_*.py" -v
```

The discovery and integral-scout scripts use the repository virtual
environment's Z3 package.  The exact replay uses only Python's standard
library.
