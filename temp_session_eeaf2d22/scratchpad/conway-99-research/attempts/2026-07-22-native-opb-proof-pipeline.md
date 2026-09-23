# Native-cardinality OPB proof pipeline

> **Record type:** synthesis note, not a run manifest. Exact commands, pinned
> source identities, and artifact hashes are authoritative only in
> `verification/2026-07-22-veripb-calibration.md`.

Status: `VERIFIED_ENCODING_AND_CALIBRATION`; target result: `UNKNOWN`

The native rooted model can now be emitted directly as a pseudo-Boolean OPB
formula. This keeps all 5,838 target `AtMost` constraints in cardinality form
instead of expanding them into sequential-counter CNF variables.

The translation is exact for signed literals:

```text
clause(l1,...,lm)       -> sum(li) >= 1
AtMost(l1,...,lm,k)     -> sum(not li) >= m-k.
```

An exhaustive small truth-table test is part of `code/test_sat_model.py`. An
independent verifier additionally checked every pair-2 assignment, 142,368
pair-3 local rows, direct/native export, contiguous identifiers, and the
target header counts.

The source-built Exact solver can produce VeriPB 3 certificates from these
formulas. Pair 2 is a positive `srg(9,4,1,2)` control and pair 3 is an
infeasible parameter control. Their raw proofs pass strict VeriPB; elaborated
proofs pass both strict VeriPB and the independently verified CakePB checker.
Canonical formulas and proofs are committed under `formal/opb-calibration/`.

The full target formula parsed successfully. A 10-second proof-producing run
returned `UNKNOWN`, and every checker verified only `NO CONCLUSION`. It is
recorded solely to demonstrate that the exact pipeline operates at target
scale. It does not constrain the truth of the conjecture.

See `verification/2026-07-22-veripb-calibration.md` for exact commands, tool
commits, binary hashes, artifact hashes, and the certificate boundary.
