# Failed routes and bounded-search ledger

## Fixed block witness does not extend in the tested linear subproblem

The exact block witness with relation counts `(5,74,341)` was fixed and the
840 transition variables were asked to satisfy 168 matching equations, 1,176
endpoint-profile equations, and 280 transition-triangle cuts.  SciPy/HiGHS
reported infeasible in about 0.01 seconds.

This is **not** promoted to a mathematical refutation:

- no exact infeasibility certificate was exported or checked;
- it concerns only one block witness among many;
- even an extending witness would satisfy only the stronger linear master.

The machine-readable observation is in
`fixed-extension-search-result.json`.

## Profile-bounded staged block search

A block search augmented with all 1,176 necessary endpoint-profile upper
bounds was run for 120 seconds.  HiGHS returned no incumbent at the time
limit.  This is `UNKNOWN`, not evidence of infeasibility.

## Direct stronger-master searches

An earlier direct HiGHS run of the 36,400-variable transition/block master
reached its 90-second time limit without an incumbent.  The package's
independently built MiniCard formulation used 38,962 primary variables,
112,602 clauses, and 5,796 native at-most constraints.  It reached its
180-second limit with status `UNKNOWN`; see `sat-search-result.json`.

The exact rational feasible point in `fractional-control.json` confirms that
the linear relaxation itself is feasible.  The unresolved issue is integral
compatibility, followed by the still-missing full residual-codegree closure.

## Boundary

No solver exit code in this ledger is a certificate.  No search here proves
existence or nonexistence of the endpoint graph.  Conway-99 remains `UNKNOWN`.

