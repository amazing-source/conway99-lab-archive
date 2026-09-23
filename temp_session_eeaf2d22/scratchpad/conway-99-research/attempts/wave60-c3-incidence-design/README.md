# Wave 60: three-component incidence design

This package attacks the `kappa=3` disconnected neighbour-core case at the
prism-free endpoint.  It independently classifies the 12-vertex
fibre-labelled components, reduces the 60-column Gram problem, and records
bounded exact and heuristic construction probes.

## Exact results

- The complete coordinate-normalized component census has 216 records.
- Exactly 50 are connected, cubic, triangle-free, and obey the sector-aware
  SRG codegree caps.
- Full `S4 x S4 x S4` canonicalization, without permuting fibres, gives 18
  fibre-preserving component types.
- Their labelled four-cycle distribution is `2:6, 4:30, 6:14`.
- The 18 types give 1,140 component multisets.  Simultaneously relabelling
  the fixed triangle and all three fibres reduces these safely to 275
  coordinate orbits; no target automorphism is assumed.
- An exact `F2` rank filter rejects none.  Target ranks range from 14 to 24.
- Every triple has at least 15,936 individually allowed distinct columns.

For the aligned type triple `(4,4,4)`, the exact enumerator finds 20,928
candidate columns and all 21 formal component/fibre pattern matrices.  The
within-component pair targets themselves force sixty selected columns and
row sum ten, permitting the SAT encoding to omit redundant diagonal and
global-cardinality constraints.

## Status

The bounded 10,000-conflict Glucose run is `UNKNOWN`, and exact-marginal
local search did not reach zero cross-Gram error.  No full `B`, proof
certificate, compatible `Y` graph, endpoint contradiction, or upper-bound
improvement is supplied.  The `kappa=3` incidence problem and Conway-99
remain `UNKNOWN`.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave60-c3-incidence-design\test_exact_check.py
.\.venv\Scripts\python.exe -B attempts\wave60-c3-incidence-design\exact_check.py --output attempts\wave60-c3-incidence-design\component-census.json
.\.venv\Scripts\python.exe -B attempts\wave60-c3-incidence-design\invariant_scan.py --output attempts\wave60-c3-incidence-design\invariant-results.json
.\.venv\Scripts\python.exe -B attempts\wave60-c3-incidence-design\exact_check.py --triple-index 580 --solver glucose42 --conflict-budget 10000 --output attempts\wave60-c3-incidence-design\triple-0580-glucose-10k.json
```

The exact claims are `DERIVED`; the search results are `UNKNOWN`.  Discovery
does not verify itself.
