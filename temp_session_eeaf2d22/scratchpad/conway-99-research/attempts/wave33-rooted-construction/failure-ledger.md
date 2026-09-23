# Wave 33 rooted-construction failure ledger

All entries below are retained to prevent repetition. None is a
nonexistence result.

## Reproducible MILP run: fixed simple design

Command:

```powershell
.\.venv\Scripts\python.exe attempts/wave33-rooted-construction/search_relaxation.py --output attempts/wave33-rooted-construction/bounded-relaxation-certificate.json --time-limit 25 --seed 3301 --enforce-active-zero
```

The zero-objective phase-1 MILP encoded all `70!` assignments of the one
frozen simple `2-(15,3,2)` design to the 70 labeled active vertices:

- 4,900 binary assignment variables;
- 70 one-block-per-active equalities;
- 70 one-active-per-block equalities;
- 210 support-group/point balance equalities.

SciPy 1.18.0 and its bundled HiGHS returned status `1`:

```text
Time limit reached. (HiGHS Status 13: model_status is Time limit reached;
primal_status is None)
```

No primal point, objective value, node count, or MIP gap was returned. The
active-graph phase was not entered and no output certificate was created.
The finite encoding was complete for the stated restricted assignment
domain, but the time-limited run did not cover or enumerate that domain.
Therefore it has no negative mathematical status.

## Exploratory compact assignment formulation

A 700-binary formulation fixed one pair of parallel-class resolutions and
encoded ten-by-ten assignments inside each of seven already-P-balanced
packets, plus 105 R-side point equalities. A 25-second HiGHS run likewise
returned status `1`, the same time-limit message, and no primal point.

This was a stricter subdomain than the reproducible 4,900-variable model and
was used only to diagnose the bottleneck. It was not retained as evidence
and excludes nothing.

## Exploratory SAT formulation

An equality-cardinality encoding of the same fixed-resolution 700-variable
subdomain was started with the inspected `python-sat` CaDiCaL 1.9.5 wrapper.
The harness terminated it at its 59-second wall boundary before any retained
model or proof. No solver result, proof trace, or mathematical conclusion was
produced.

## Fixed-budget partial-object search

The retained standard-library search used nine seeded restarts of 200,000
within-P-group swaps. It found an explicit active-to-Z layer with:

- all 70 active degrees equal to 3;
- all 15 Z degrees equal to 14;
- all 105 Z pairs having exactly two common active neighbors;
- nine of fourteen support groups exactly balanced;
- ten remaining support-group/point violations, five counts equal to 1 and
  five equal to 3, for squared defect 10.

This is deliberately retained as a hostile near miss. It supplies no
active-active edges and fails ten equations before the active graph is even
considered. Non-discovery of defect zero within the fixed heuristic budget
has no negative status.

## Status retained

```text
complete target graph extension: UNKNOWN
complete-domain UNSAT certificate: NONE
rooted n3=708 endpoint: UNKNOWN
Conway-99: UNKNOWN
novelty: UNKNOWN
```
