# Wave153: complete bounded rational triangle-root projection

Status: **CANDIDATE exact null result, awaiting independent verification**.

## Result

At the conditional prism-free `n3=4158`, `kappa=3` endpoint, Wave153 tested
the complete fixed-triangle pair-correlation projection

```text
sum_s x_s a_s = vec_upper(G),       0 <= x_s <= 1.
```

Here `s` runs through the allowed distinct six-vertex incidence columns,
`a_s` records the 630 unordered row pairs in `s`, and `G` is the exact
target Gram matrix. Every column contains two vertices from each of the three
components and two from each of the three fibres.

Exact rational witnesses exist for all 275 safe coordinate-orbit
representatives. The frozen coordinate action transfers those witnesses to
all 1,140 unordered triples of the 18 classified component types.

| Exact quantity | Result |
|---|---:|
| component types | 18 |
| unordered type triples | 1,140 |
| safe coordinate orbits | 275 |
| orbit representatives with exact witnesses | 275 |
| pair coordinates replayed per representative | 630 |
| row margins replayed per representative | 36 |
| candidate columns per representative | 15,936 to 27,200 |
| rational witness support | 438 to 462 |
| coefficient bounds | `0 < x_s <= 1` on the emitted support |

All 275 witnesses replay exactly, including zero pair targets, row margins
equal to 10, and total column weight equal to 60. Floating-point optimization
was used only to select a support; the emitted coefficients were reconstructed
with exact rational arithmetic and then replayed without tolerances.

## Interpretation

This is a useful negative result about a proposed obstruction, not a solution
of the graph problem. The complete bounded rational pair projection is too
weak to exclude any fixed-triangle component triple. In particular, adding
the natural distinct-column inequalities `x_s <= 1` does not repair the gap
left by an unbounded nonnegative pair cone.

The remaining compatibility gap is integral and higher-order:

- rational column weights need not select exactly 60 distinct columns;
- pair marginals need not admit one common integral three-way coupling;
- even a binary incidence design would still need a compatible residual
  60-vertex graph.

The next prudent shift is therefore to a projection that retains at least
triple intersections or integral coupling across component blocks, rather
than adding more pair-coordinate inequalities to this relaxation.

## Reproduce

The main certificate is `exact-results.json.gz`. It is deterministic,
canonical gzip JSON (`mtime=0`).

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave153-alternative-compatibility\correlation_polytope.py verify `
  attempts\wave153-alternative-compatibility\exact-results.json.gz
```

Expected:

```text
Wave153 final exact replay: PASS_WITH_SCOPE
```

The discovery command and batch ranges are recorded in `run-report.yaml`.
`protocol.md` freezes the scope and certificate gate; `derivation.md` derives
the finite system; `failed-routes.md` records bounded alternatives that did
not yield a certificate; and `verifier-request.md` specifies the independent
check.

## Scope wall

Discovery cannot promote its own result to `VERIFIED`. This package provides
no binary incidence design, residual graph, endpoint construction or
exclusion, strict upper bound, Conway-99 resolution, or external novelty
claim. Those fields remain `UNKNOWN` or `NOT_OBTAINED` in the artifact.

