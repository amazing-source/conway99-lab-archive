# Wave 35 construction: prism-free rooted and local-extension reductions

```yaml
role: construction
date_utc: 2026-07-26T22:12:00Z
git_commit: 6d98cb5f73c1f56d227e97b1c3e70d363669bf87
claim_label: CANDIDATE
scope: >
  Exact necessary rooted and one-edge local-extension models for the
  conditional endpoint n3=4158, equivalently zero induced triangular prisms.
inputs:
  code/root_model.py: repository baseline
  code/sat_model.py: repository baseline
  code/matching_orbits.py: repository baseline
method: >
  Translate prism-freeness into rooted residual-edge units; intersect them
  with the verified 12-way N3 joint cover; enumerate every locally admissible
  outside-neighborhood type for the four endpoint cycle partitions; and run
  explicitly bounded discovery-only solver scouts.
command: |
  python -B -m unittest discover -s code -p "test_wave35_n3_endpoint_local_extension.py" -v
outputs:
  code/wave35_n3_endpoint_root_scout.py: 04ef058c3a14ed8790773f015edc16f4ae1da1bcb011e3b795f0d16229f7ff7e
  code/wave35_n3_endpoint_local_extension.py: 41f3fb71c34bf4cc5b9d539a27f86ad644dbb7d2f86a1bbd77826f655628f580
  code/test_wave35_n3_endpoint_local_extension.py: 351e81fa0d5509c5851fa3714bc81bb3fa0ceea18944f5265372e28fdf0d4ae3
  attempts/wave35-n3-upper-triple-overlap/root-endpoint-reduction.json: 7551c7b9d956705e41f9feb42d76d3bb5ab60dab0b46416fa9c0e58e5346a46a
  attempts/wave35-n3-upper-triple-overlap/root-endpoint-bounded-scout.json: 31535540e66889ac6a17c476bc41b650038c04f73a0566c3738d66684bf4dae1
  attempts/wave35-n3-upper-triple-overlap/local-extension-bounded-scout.json: 8922fc4d0e5e056c69685d42377f71ed70d0bf17574e4a6a7219ce1ad0794685
limitations:
  - The local-extension systems omit all adjacencies among the 72 outside vertices.
  - The full-target and local integer scouts all stopped at budgets or time limits.
  - The transcribed scout records are not raw solver logs or proof certificates.
  - No SAT assignment, checked UNSAT proof, endpoint exclusion, or graph is supplied.
```

## Exact rooted reduction

Freeze a root vertex `o`. Its 14 neighbors form seven mate pairs
`(a_i,b_i)`, and the remaining 84 vertices are labeled by the nonmate
coordinate pairs among those 14 neighbors.

For each root triangle `{o,a_i,b_i}` and each of the other 12 root-neighbor
coordinates `r`, the residual edge

```text
{a_i,r} -- {b_i,r}
```

would close an induced triangular prism. Therefore the endpoint `P=0`
forces exactly

```text
7 * 12 = 84
```

negative residual-edge units. This uses the complete rooted labeling and
assumes no automorphism.

Intersecting those units with the previously verified 12-way normalized
`N3` joint cover rejects branches

```text
1, 2, 3, 6, 7, 9, 11
```

immediately. Exactly five normalized branches remain:

```text
4, 5, 8, 10, 12.
```

This is a complete branch reduction conditional on the earlier universal
`N3` occurrence theorem and on `P=0`. It is not an endpoint exclusion.

## Four one-edge local-extension systems

Around a fixed graph edge, endpoint prism-freeness leaves four cycle
partitions:

```text
2+2+2, 2+4, 3+3, 6.
```

Each produces a 27-vertex seed. For one of the other 72 vertices, exact
degree and common-neighbor constraints allow 5,500 neighborhood masks:

```text
size 0:    1
size 1:   27
size 2:  288
size 3: 1584
size 4: 3600
```

After eliminating masks that cannot be selected, each exported binary OPB
model has 5,184 variables and 380 equality rows. The OPB files are
deterministic and their hashes are checked by the focused test suite.

The ordinary linear-programming relaxation is feasible for all four
partitions. That is only a fractional positive control, not an integer
neighborhood multiset and not a graph.

## Bounded scouts

The five full rooted branches each reached a 100,000-conflict MiniCard budget
with status `BUDGET_UNKNOWN`.

The first integer local-extension scouts gave:

```text
2+2+2: TIMEOUT_UNKNOWN_NO_INCUMBENT
2+4:   TIMEOUT_UNKNOWN_NO_INCUMBENT
3+3:   TIMEOUT_UNKNOWN_NO_INCUMBENT
6:     TIMEOUT_UNKNOWN_NO_INCUMBENT
```

A 120-second binary reduction and a separate native-cardinality benchmark
also ended `UNKNOWN`. No run emitted an infeasibility certificate or a
candidate assignment.

## Publication boundary

The exact 84-unit and five-branch reductions are reproducible necessary
conditions. The local systems are reproducible candidate relaxations. Every
solver stop is non-evidentiary:

```text
n3 upper bound: 4158
n3=4158:        UNKNOWN
Conway-99:      UNKNOWN
```
