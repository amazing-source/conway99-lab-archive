# Wave 56 independent percolation-closure verification protocol

Frozen before inspecting `attempts/wave56-percolation-closure/`.

## Scope

Independently check, for a hypothetical strongly regular graph with parameters
`(v,k,lambda,mu)=(99,14,1,2)`, only the following claims:

1. the scoped use of Ibrahim--LaFayette--McCall, Lemma 4.9, about the closure
   of a nonedge under 2-neighbor bootstrap percolation;
2. all target-parameter arithmetic used in the discovery package;
3. the definitions and claimed identities/inequalities involving `n3`, `P`,
   `H`, `R`, and `S`, with special attacks on `R=18H`, `6H<=P`, `R<=3P`,
   and `S>=n3`;
4. the exhaustive census of all 64 labeled simple graphs on six tips;
5. endpoint masks/profiles, formal `D4` label-orbits, the synchronous
   wave-size histogram, and `x2+3*x3+6*x4=16`;
6. whether any claim assumes an automorphism of the hypothetical target
   graph or inflates a locally admissible profile into a globally completable
   graph.

This verification does not search for, construct, or exclude a full
`srg(99,14,1,2)`. It does not certify a strict upper bound on `n3` unless a
fully checked deduction supplies one.

## Independence and clean-room rules

- The checker is written from the frozen scope and the primary source, not by
  copying discovery code.
- Discovery files are opened only after this protocol and
  `input-freeze.sha256` exist.
- The checker reconstructs every finite object from definitions and compares
  its result with the discovery artifact only after its own result is fixed.
- No vertex-transitivity, edge-transitivity, nonedge-transitivity, or other
  target-graph automorphism is assumed. `D4` acts only as formal relabelings
  of a fixed four-cycle when orbit counting is explicitly requested.
- The 64-tip census is exhaustive only for the six formally defined optional
  tip-tip edges. Passing a local census is not evidence of completion to a
  target graph.
- Every identity is checked both algebraically and, where feasible, by
  exhaustive incidence-table tests designed to break incorrect multiplicity
  factors.

## Hostile tests

1. Enumerate all 64 masks without importing discovery code; check uniqueness,
   complement coverage, orbit partitions, and orbit-stabilizer totals.
2. Recompute bootstrap waves directly from adjacency and compare synchronous
   versus asynchronous conventions.
3. Generate malformed incidence tables to ensure each double-count identity
   fails when one multiplicity or endpoint condition is altered.
4. Separate local necessary conditions from existence/completability claims.
5. Recompute the exact target arithmetic from `A^2=(lambda-mu)A+
   (k-mu)I+mu*J`.
6. Hash all inputs and outputs and rerun the checker from a clean process.

## Status rule

Use `VERIFIED` only for exact claims independently reproduced in this scope.
Use `REFUTED` for an explicit countercalculation. Use `UNKNOWN` when the
artifacts or hypotheses do not suffice. A mixed package is reported
`REFUTED_IN_PART` in prose but uses the schema-compatible run-report label
`REFUTED`.

