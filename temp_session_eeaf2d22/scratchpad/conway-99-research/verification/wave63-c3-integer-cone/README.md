# Independent verification of Wave 63

This package independently verifies the sealed rational certificates in
`attempts/wave63-c3-integer-cone/`. It does not import or execute discovery
code.

## Verdict

`VERIFIED` within the stated conditional and finite scope:

- all 18 frozen component types pass the required cubic, connected,
  fibre-matching, and triangle-free checks;
- candidate counts were rebuilt for all 1,140 unordered component triples and
  agree exactly with Wave 60/61, including the range `15,936..27,200`;
- the fixed selection contains all 56 minimum-support triples, the unique
  maximum-support triple, all 18 diagonals, and the first representative of
  each of seven full-pair F2 rank strata, producing 74 lanes after eight
  overlapping memberships are removed;
- all 74 rational witnesses replay all 630 pair equations exactly, for 46,620
  checked equations in total;
- every recorded coefficient obeys `0 < x_s <= 1`; and
- every witness support size is its reported full-pair F2 rank, from 438 to
  462.

Eight tests reject mutations of a coefficient, denominator sign, candidate
index, duplicate candidate, target equation, and lane selection. They also
check the positive first lane and the MILP status guard.

The single 30-second binary MILP nonhit remains `UNKNOWN`: it has neither a
model nor a proof certificate and provides no negative evidence.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B verification\wave63-c3-integer-cone\independent_check.py
.\.venv\Scripts\python.exe -B -m unittest discover -s verification\wave63-c3-integer-cone -p "test_*.py" -v
```

## Boundary

These are rational pair-margin solutions, not binary incidence designs.
Coverage is the fixed 74-lane subset, not every one of the 1,140 triples or
the 275 safe coordinate orbits. No compatible `Y` graph, full strongly
regular graph, endpoint contradiction, or Conway-99 resolution is supplied.
The endpoint, conjecture, and novelty status remain `UNKNOWN`.
