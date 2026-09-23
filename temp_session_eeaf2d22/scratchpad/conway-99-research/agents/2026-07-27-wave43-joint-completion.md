# Wave 43 construction agent: canonical joint completion

## Assignment

Attack the exact mask-`51739` Wave 42 joint-incidence instance without an
automorphism assumption, under a four-GiB working-set ceiling and a
fifteen-percent host-free-memory floor.

## Exact reduction

The `45,032` legal six-set variables project to three pairwise perfect
matchings with candidate edge counts

```text
2,881 / 2,881 / 2,694.
```

The first two matchings determine the triple associated with every fibre-0
pair. `96,408` binary clauses reject illegal triples; `45,032` ternary
clauses force the corresponding edge of the third matching for every legal
triple. Since the induced sixty third-matching edges are distinct, they
exhaust the independently perfect third matching. Thus the compact model is
equivalent to the original three-way matching and is not a relaxation or
symmetry restriction.

Exact Gram-cell capacities are sufficient: every cross-fibre matching
contributes 240 point-pair incidences and its target capacities sum to 240.

The canonical sequential-counter encoding has

```text
8,456 semantic variables
82,532 variables including auxiliaries
338,528 clauses.
```

## Search result

No full `B` and no terminal proof emerged. Bounded CaDiCaL, Glucose, and
Minicard runs all remained unresolved. The largest retained diagnostic
bound was `969,623` Minicard conflicts; all runs stayed below `1.01 GiB`, and
the compact runs stayed below `309 MiB`. At least `61.84%` host memory
remained free during every retained compact run. No Wave 43 worker remains.

Claim label: **DERIVED compact reduction; UNKNOWN existence status**.

## Boundary

An `UNSAT` status will not be promoted without a frozen CNF, proof trace, and
independently replayed proof checker. A future `SAT` certificate must be
checked from its sixty blocks, without discovery internals.

There is no compatible `H`, endpoint exclusion, general upper-bound
improvement, Conway-99 solution, or novelty claim.

