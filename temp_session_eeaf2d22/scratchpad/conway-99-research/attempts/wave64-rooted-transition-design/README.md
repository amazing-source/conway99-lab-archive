# Wave 64: rooted transition/design space

This package shifts the prism-free endpoint into a transition-system plus
3-matching-design problem on

```text
H = K14 - 7K2.
```

The shift is exact at the structural level: the 84 residual labels are the
edges of `H`; the selected intersecting-label edges are fourteen local
transition matchings; and the selected disjoint-label edges are 140
three-edge-matching blocks.  The implemented integer masters remain
relaxations until every residual codegree equation is imposed.

## Reproduce

```powershell
.venv\Scripts\python attempts\wave64-rooted-transition-design\transition_design.py census
.venv\Scripts\python attempts\wave64-rooted-transition-design\check_witness.py
.venv\Scripts\python -m unittest attempts\wave64-rooted-transition-design\test_exact_check.py -v
```

The block witness was found with:

```powershell
.venv\Scripts\python attempts\wave64-rooted-transition-design\transition_design.py solve-block --time-limit 60 --seed 0 --full-opposite-count 5
```

The bounded stronger-master SAT scout can be repeated with:

```powershell
.venv\Scripts\python attempts\wave64-rooted-transition-design\sat_scout.py --time-limit 180
```

## Main artifacts

- `derivation.md`: exact mathematics and the master/equivalence boundary.
- `exact-census.json`: finite candidate and transition counts.
- `block-witness.json`: explicit 140-block integral master witness.
- `exact-check-result.json`: solver-independent integer/rational checks.
- `fractional-control.json`: exact rational feasible point of the stronger
  linear master.
- `sat-search-result.json`: bounded `UNKNOWN` stronger-master search.
- `failed-routes.md`: non-evidentiary search outcomes.

## Status

The finite census, integral block witness, and fractional control are
`DERIVED` and await a clean independent verifier.  There is no integral
witness for the stronger master, no exact infeasibility certificate, and no
complete residual graph.  Endpoint `n3=4158` and Conway-99 remain `UNKNOWN`.

