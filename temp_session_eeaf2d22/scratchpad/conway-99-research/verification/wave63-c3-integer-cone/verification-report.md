# Wave 63 independent verification report

## Scope and separation

The verifier froze all discovery-package bytes at
`2026-07-27T22:12:15Z`, before reading discovery implementation, result,
protocol, or prose files. The independent implementation uses only the Python
standard library and neither imports nor executes Wave 63 discovery code.

The verified target is conditional on the prism-free `n3=4158`, `kappa=3`
fixed-triangle lane. The result concerns a fixed 74-lane rational relaxation
of the incidence pair equations.

## Exact verdict

The scoped rational-certificate claim is `VERIFIED`, with zero mathematical
mismatches.

1. The package-manifest SHA-256 is
   `c85f9dcf3d0bdba2a41299c4a3c4fdd8c9802903cff04ab237f40d9840df6018`;
   all 14 manifest entries and all four mathematical upstream inputs match.
2. All 18 component types were rebuilt as connected cubic triangle-free
   12-vertex graphs whose within-fibre and cross-fibre edges are perfect
   matchings.
3. Candidate columns were recounted for all 1,140 unordered type triples.
   Every count agrees with frozen Wave 61 and the Wave 60 extrema. The exact
   range is `15,936..27,200`, with 56 triples at the minimum and one at the
   maximum.
4. The selection rule was rebuilt before witness evaluation. Its 82 raw
   category memberships are 56 minima, one maximum, 18 diagonals, and seven
   first rank-stratum representatives. Eight overlaps are removed, leaving
   exactly the recorded 74 lanes.
5. Candidate six-sets were rebuilt lane by lane. Each contains two vertices
   from every fixed fibre and two from every graph component, and all fifteen
   pairs have positive target multiplicity.
6. All 74 witnesses replay their 630 pair equations with exact rational
   arithmetic: 46,620 equations in total. Each has total weight 60, every
   coefficient is strictly positive and at most one, and support sizes
   `438..462` equal the frozen reported full-pair F2 ranks on every lane.

The selected-lane support/rank histogram is:

```text
438: 56
442: 1
446: 1
450: 10
454: 1
458: 1
462: 4
```

## Hostile checks

Eight tests passed. The verifier rejects:

- a changed rational numerator;
- a negative denominator;
- an out-of-range candidate index;
- a duplicate candidate index;
- a changed target equation; and
- a missing selected lane.

It also positively replays the first lane and independently audits the MILP
status guard.

## Metadata clarifications

- The discovery field
  `exact_replay.distinct_column_upper_bound_exact: false` records that the
  discovery exactification did not enforce `x_s <= 1`. It is not a statement
  that the saved coefficients violate the bound. Independent replay proves
  every saved coefficient is at most one.
- `attempts/wave63-c3-integer-cone/exact-check-results.json` reports
  `all_witness_pair_equations_checked: 630`. That is the number per witness;
  the exact total across 74 witnesses is 46,620.

Neither clarification changes a mathematical claim.

## MILP and unresolved boundary

Exactly one binary MILP lane was run for about 30 seconds. The sealed record
has solver status 1, a time-limit message, no candidate, and no proof
certificate. Its only valid status is `UNKNOWN`; it is not evidence of
infeasibility.

The verified rational witnesses are not binary incidence matrices. The
74-lane selection does not exhaust all 1,140 triples or 275 safe coordinate
orbits. No compatible `Y` graph or complete strongly regular graph is
constructed. The endpoint, Conway-99, and novelty statuses remain `UNKNOWN`.
