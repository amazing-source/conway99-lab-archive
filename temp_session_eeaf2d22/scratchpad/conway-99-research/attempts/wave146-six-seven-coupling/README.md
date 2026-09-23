# Wave 146: rooted six-to-seven coupling

Status: **exact rational endpoint relaxation witness; Conway-99 unknown**.

Wave 144 assigned a 64-cell outside-neighborhood profile to each induced
six-set class.  Wave 146 first requires every positive cell to be a locally
admissible rooted seven-vertex graph, then glues the resulting rooted orbit
counts to the complete 208-class order-seven deck.

## Exact results

The seventh-vertex filter removes 25 output-weight cells across 16 of the 62
six-vertex classes.  All 65 cells used by the particular Wave 144 endpoint
table remain locally supportable, but its selected profiles fail the exact
rooted identity

```text
R_(38,8) = 2 R_(37,12)
```

by `3,076,026,288`.  Allowing every local profile to vary still refutes that
fixed table numerically, but no solver status is promoted.

The complete endpoint model then frees all 343 surviving
`(six-class, output-weight)` cells.  It contains

```text
variables:            13,973
equalities:            8,981
integer nonzeros:    110,269
rooted orbit types:       944
```

Column-aware numerical discovery reconstructs an exact nonnegative rational
witness with 2,998 positive coordinates and maximum denominator four.  All
8,981 equations replay exactly.  The witness has `h11=16632`.

Therefore this complete **one-root** six-to-seven aggregate relaxation does
not exclude `n3=4158` and cannot improve the rigorous upper bound `4158`.

## What the witness is not

The variables aggregate profiles over all six-sets.  They need not decompose
into a compatible profile for every individual six-set, and two rooted
seven-set views are not required to agree on an eight-vertex union.  The
witness is not an adjacency matrix, graph, or code.

The next exact lift is a two-root/order-eight coupling: retain two outside
vertices simultaneously, including whether they are adjacent, and impose
both seven-deletion marginals.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave146-six-seven-coupling\exact_witness.py `
  --verify attempts\wave146-six-seven-coupling\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave146-six-seven-coupling -p "test_*.py" -v
```

The stored witness is the certificate.  HiGHS status, including the retained
false-infeasibility explorations, is not certificate authority.
