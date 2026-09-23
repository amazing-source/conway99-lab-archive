# Wave 22 full-seven-deck route ledger

## Full deletion-deck equations

Status: `DERIVED_INCONCLUSIVE`, awaiting independent verifier review.

The 62-by-208 deletion matrix, the 62 right-hand sides at `n3=705`, and a
nonnegative integer count vector were checked exactly.  The system is feasible,
so this necessary-condition route does not improve the conditional bound
`n3>=705`.

## Published Hamiltonian variables

Status: `DERIVED_INCONCLUSIVE`, awaiting independent verifier review.

The pinned figure was transcribed panel by panel using a clockwise perimeter
`C7`.  Canonicalization gives 19 distinct masks and exactly covers an
independently enumerated census of all locally admissible Hamiltonian
seven-vertex classes.  At the admissible choice `h11=2820`, all 19 published
formula values were fixed in the integer deck witness.  The combined system is
still feasible.

The transcription is auditable human source interpretation tied to the pinned
figure hash.  Its exact graph canonicalization, coverage, counts, and deck
compatibility are machine checked.

## Floating feasibility

Status: superseded.

Floating LP feasibility at `n3=0,705,4158` was useful for scouting but is not a
certificate.  The frozen `n3=705` integer witness and exact checker supersede
that observation at the incumbent boundary.

## HNF/SNF and congruence search

Status: incomplete and not needed for the positive witness.

Two HNF attempts did not finish.  Finite-field ranks for `p=2,3,5,7` did not
restrict `t=n3/3`.  Rank 62 over `F_11` establishes full real row rank, but does
not by itself characterize the integer image of the deletion matrix.

## Scope wall

The variables are aggregate counts of isomorphism types.  They do not specify
which seven-subsets receive which types, do not enforce overlap consistency
between distinct seven-subsets, and do not encode a 99-by-99 adjacency matrix.
Consequently the witness is neither a construction nor evidence of existence.
