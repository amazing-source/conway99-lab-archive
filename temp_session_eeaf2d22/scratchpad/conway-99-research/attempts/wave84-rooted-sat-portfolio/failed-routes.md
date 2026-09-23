# Wave 84 failed routes

## Solver portfolio

The default, SAT-targeted, and UNSAT-targeted CaDiCaL lanes all reached
their alarm limits.  Kissat independently returned `s UNKNOWN` at its time
limit.  None emitted a result file usable as a graph witness, and none emitted
an UNSAT proof.

The substantial internal reductions and conflict counts do not estimate the
remaining mathematical distance to a result.  Restarting the same
configuration is not a completeness argument.

## Raw transcripts

The exact local transcript hashes are retained in `exact-results.json`.
Publishing path-redacted copies as if they were raw evidence would weaken the
evidence contract, so no such substitution is made.  These are null-run
diagnostics, not proof artifacts.

## Continuation

Longer CaDiCaL and Kissat runs may be useful scouts.  Any terminal SAT result
must pass direct clause evaluation, model decoding, and the independent graph
checker.  Any terminal UNSAT result must be reproduced with a pre-frozen proof
format and checked against the exact CNF.

