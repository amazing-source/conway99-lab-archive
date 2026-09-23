# Wave 53 failed and deferred routes

## Confusing branch coverage with proof coverage

The 33 cases are exhaustive only as a conditional normalized cover. No
complete case has a checked terminal proof. The verified
`branch15 AND x187=1` contradiction is a proper subcase and therefore leaves
complete-case coverage at `0/33`.

## Three-second branch-15 remainder solve

Exact returned `UNKNOWN`. The retained raw proof, elaborated kernel proof,
strict VeriPB replays, and CakePB replay all certify `NO CONCLUSION`.
Parsing and presolve consumed 3.345 of 3.448 CPU seconds, leaving only 0.103
seconds of reported solve time. This run has zero mathematical evidentiary
value.

## Static all-prism materialization

The already audited complete schema has over 24 billion residual-only prism
clauses before simplification. It remains resource-inappropriate. A terminal
UNSAT proof for the smaller necessary-condition formula is sufficient to
exclude a case; a SAT assignment is not sufficient without complete
solve--cut--decode--oracle handling.

## Solving all 33 cases at once

Deferred. One case at a time gives case-owned raw proofs, bounded resource
use, atomic status records, and an unambiguous coverage numerator. Parallel
unbounded proof production would make the 20% memory reserve harder to
enforce and would not repair the missing certificate gate.
