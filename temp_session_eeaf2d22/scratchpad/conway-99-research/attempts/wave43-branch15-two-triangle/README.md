# Wave 43 branch-15 two-unfixed-triangle cuts

Status: `DERIVED_STRONGER_REDUCTION`; refined endpoint branch 15 remains
`UNKNOWN`, and checked endpoint coverage remains `0/33`.

## Exact structural family

For each coordinate `c`, exactly 12 of the 84 residual labels contain `c`.
Choosing two of those residual vertices gives a coordinate-anchored triangle
whose only nonfixed edge is one primary residual-edge variable. There are

```text
14 * C(12,2) = 924
```

such potential triangles. At the SHA-bound Wave 42 branch-15 closure, 7
controllers are true, 157 are false, and 760 remain unfixed.

This package exhausts every unordered, vertex-disjoint pair among those 760
unfixed coordinate triangles and all six perfect matchings between each pair.
At the conditional endpoint `n3=4158`, every such completed matching is
forbidden because it would be a triangular prism.

The rooted scaffold makes the surviving family especially rigid:

1. If the coordinate anchors `c,d` are not the paired scaffold neighbors,
   compatibility would require both triangles to contain the same residual
   label `{c,d}`, contradicting vertex-disjointness.
2. If `c,d` are paired neighbors, the residual catalogue excludes `{c,d}`.
   Thus the anchors must be matched to each other.
3. The remaining two matching edges are residual variables.

Every surviving constraint therefore has the exact four-variable form

```text
not(left triangle controller
    and right triangle controller
    and first residual cross edge
    and second residual cross edge).
```

No completed-graph automorphism is assumed.

## Exact census

```text
coordinate triangles:                         924
Wave 42 true / false / unfixed:          7 / 157 / 760
unordered unfixed pairs visited:             288,420
vertex-disjoint pairs:                       259,499
vertex-disjoint mate-anchor pairs:            20,400
perfect matchings visited:                 1,556,994
killed by fixed scaffold nonedges:         1,516,194
accepted matchings / distinct clauses:        40,800
exact rows already in Wave 37 + Wave 42:            0
```

All 40,800 retained raw clauses have width four. After exact simplification
by the Wave 42 closure, 6,460 are satisfied and 34,340 distinct new width-four
rows remain.

## Closure and bounded branch attempt

Each of the 34,340 active rows has four unassigned negative literals, hence
residual slack three. Adding the family leaves generalized-unit closure
unchanged:

```text
forced variables:                  830
forced primary variables:          174
new forced variables:                0
contradiction:                     none
```

Both polarities of the 32 unfixed coordinate-triangle controllers with
highest active-cut incidence were then replayed through:

- the complete frozen Wave 37 branch-15 OPB;
- the Wave 42 seventh-fixed-triangle delta; and
- all 40,800 new two-triangle rows.

All 64 probes reached noncontradictory fixed points. They produced zero
candidate implications and zero derivations sourced by the new rows. This is
a precise null boundary, not evidence of satisfiability.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave43-branch15-two-triangle\coordinate_triangle_cuts.py

.\.venv\Scripts\python.exe -B `
  attempts\wave43-branch15-two-triangle\coordinate_triangle_cuts.py `
  --verify

.\.venv\Scripts\python.exe -B `
  attempts\wave43-branch15-two-triangle\combined_closure_and_probes.py

.\.venv\Scripts\python.exe -B `
  attempts\wave43-branch15-two-triangle\combined_closure_and_probes.py `
  --verify

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave43-branch15-two-triangle -p "test_*.py" -v
```

## Promotion boundary

- This proof-agent package is `DERIVED`, not independently `VERIFIED`.
- The completeness statement is restricted to pairs of coordinate-anchored
  triangles unfixed at the frozen Wave 42 closure.
- Prisms involving a triangle without a coordinate anchor remain omitted.
- A propagation fixed point is not a SAT witness.
- Propagation closure alone is not promoted as branch `UNSAT`.
- No retained independently checked UNSAT proof or complete graph was found.
- Branch 15, `n3=4158`, the strict upper-bound question, and Conway-99 remain
  `UNKNOWN`.

