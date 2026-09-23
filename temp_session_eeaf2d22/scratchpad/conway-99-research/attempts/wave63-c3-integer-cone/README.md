# Wave 63: exact rational cone for the `kappa=3` incidence lane

Wave 61 identified the missing invariant: parity forgets the nonnegative
integer multiplicities of the same distinct six-set columns.  This package
moves to that nonnegative cone and semigroup space.

## Exact result

The independent checker reconstructs all 18 frozen component types and all
1,140 candidate counts.  It confirms the Wave 60 extrema
`15,936..27,200` exactly.

A fixed 74-lane subset was then tested: all 56 global minimum-support
triples, the unique maximum-support triple, all 18 diagonal triples, and the
first representative of every full-pair `F2` rank stratum, with overlaps
removed.

Every one of the 74 lanes has an exact nonnegative rational solution of all
630 pair equations.  The certificates have 438--462 positive coefficients,
and the checker additionally finds every recorded coefficient is at most
one.  Thus even the rational relaxation of the distinct-column bounds
`0 <= x_s <= 1` is feasible on every tested lane.

This is a useful negative boundary, not a construction: rational
coefficients need not be zero or one.

## Integer status

One 30-second binary MILP probe on the minimum-support triple `(0,0,0)`
timed out without a model or proof.  Its status is `UNKNOWN`; it is not
evidence of nonexistence.

No integer `36 x 60` incidence matrix, compatible `Y` graph, endpoint graph,
endpoint contradiction, general upper-bound improvement, or Conway-99
resolution is supplied.  Novelty is `UNKNOWN`.

## Reproduce

Install the discovery dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r attempts\wave63-c3-integer-cone\requirements.txt
```

Run the discovery:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave63-c3-integer-cone\integer_cone.py --lp-time-limit 60 --milp-time-limit 30 --milp-lane-count 1 --output attempts\wave63-c3-integer-cone\exact-results.json
```

Replay the saved certificates with the standard-library checker:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave63-c3-integer-cone\exact_check.py --verify attempts\wave63-c3-integer-cone\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest discover -s attempts\wave63-c3-integer-cone -p "test_*.py" -v
```

The exact claims are `DERIVED`.  Discovery does not verify itself.
