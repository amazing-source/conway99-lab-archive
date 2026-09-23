# Wave 43 canonical joint-completion construction

Status: **DERIVED compact exact reduction; full `B` remains UNKNOWN**.

This package continues the Wave 42 mask-`51739` problem, conditional on

```text
n3 = 4158,
rank_F3(M) = 12,
every edge has local type 2+2+2,
the canonical rank-33 mask-51739 core occurs.
```

No core automorphism or outside-vertex symmetry is assumed.

## Compact exact model

Wave 42 retained `45,032` legal triples `(i,j,k)`, where each coordinate is
one of the sixty nonmatching pairs in a fibre. A full incidence matrix `B`
would choose sixty triples and project to three perfect matchings:

```text
P01 subset [60] x [60],
P02 subset [60] x [60],
P12 subset [60] x [60].
```

Only pair-pairs occurring in at least one legal triple need variables. Their
counts are

```text
|P01 candidates| = 2,881
|P02 candidates| = 2,881
|P12 candidates| = 2,694.
```

The first two selected matchings determine a triple `(i,j,k)` for every
fibre-0 pair `i`. A binary clause forbids the choice if that triple is not one
of the `45,032`; otherwise a ternary clause forces `(j,k)` in the third
matching.

This is equivalent to the full three-way matching:

1. every full `B` projects to a satisfying triple of pairwise matchings;
2. conversely, the first two perfect matchings induce sixty distinct
   fibre-1--fibre-2 edges;
3. the compatibility clauses force all sixty edges into the independently
   perfect third matching, so the latter equals the induced matching;
4. therefore the matchings reconstruct exactly sixty legal six-sets.

Each pairwise matching is also capped at the forced Gram multiplicity for
every cross-fibre point pair. It contributes exactly `60 * 4 = 240`
point-pair incidences, and the positive Gram targets sum to `240`. Hence all
upper bounds are attained: these caps encode the exact concurrence matrices,
not a relaxation.

For variable-numbering seed zero, sequential-counter CNF has:

```text
semantic variables:             8,456
variables including auxiliaries: 82,532
clauses:                       338,528
perfect-matching exact-one rows:    360
cross-cell caps:                    412
illegal-triple binary clauses:   96,408
legal-triple ternary clauses:    45,032
```

The deterministic record is `pairing-reduction.json`.

## Search boundary

Bounded CaDiCaL, Glucose, and Minicard runs found neither a model nor a
terminal result. A longer variable-seed-3 CaDiCaL run stopped after exactly
`5,000,000` conflicts, `21,839,078` decisions, and `2,391,245,003`
propagations without a Boolean result.

The same exact problem was independently expressed as a sparse zero-objective
binary MILP:

```text
binary variables:                   45032
pair-partition equality rows:         180
cross-fibre Gram equality rows:        432
total equality rows:                   612
sparse nonzeros:                    675480
```

A 600-second HiGHS run returned no incumbent. Both results are null
diagnostics only. No solver exit code, timeout, or conflict count is treated
as evidence of nonexistence.

There is no full `B`, compatible `H`, endpoint exclusion, strict upper bound,
Conway-99 solution, or novelty claim in this package.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave43-joint-completion\solve_joint.py `
  --model pairing --variable-seed 0 --describe-only `
  --output attempts\wave43-joint-completion\pairing-reduction.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave43-joint-completion -p "test_*.py" -v
```

Any future `SAT` result must be promoted only after a separate implementation
checks all sixty blocks and every Gram entry. Any future `UNSAT` result must
include a frozen proof trace checked by a retained independent proof checker.
