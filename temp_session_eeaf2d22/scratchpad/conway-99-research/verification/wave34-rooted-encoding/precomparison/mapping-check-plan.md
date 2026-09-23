# Independent DIMACS and model-map check plan

This plan is deliberately separate from discovery.  It has not yet been
applied to a Wave 34 candidate.

## Formula and map integrity

1. Hash the exact DIMACS, JSONL map, criterion specification, generator, solver
   binary, and any proof bytes before execution.
2. Parse the DIMACS without a SAT library.  Require one header, exactly the
   declared clause count, terminating zero on every clause, no literal zero
   inside a clause, and every variable id in `1..num_vars`.
3. Parse the map as JSONL.  Require one header followed by exactly one record
   for every id in strict order, with no gaps or duplicates.  Check every
   index range and require the first 3,465 records to be precisely all
   `D(i,j)` (`i<j`) and all `B(i,q)` in the frozen labeled order.
4. Reconstruct the fixed Fano data from the seven frozen lines, rather than
   importing serialized matrices.  Compare the three canonical data hashes
   and recheck the fixed `SS` identity.
5. Rebuild every expected product meaning and its three clauses from the map.
   For each mapped `CARD_GE` variable, rebuild the threshold recurrence and its
   simplified clauses.  Compare the resulting normalized clause multiset and
   deterministic clause-stream hash against the DIMACS.  This step must not
   trust family counts supplied by the encoder.
6. Independently enumerate all equation keys and scopes.  Require the exact
   family inventory and target distributions in `count-expectations.json`.
   Reject missing, duplicated, extra, or out-of-range equation records.

## SAT-model validation

1. Parse a model independently and require a total assignment for all declared
   variables with no contradictory duplicate literals.
2. Evaluate every DIMACS clause directly.
3. Decode only the 3,465 primary records.  Build a full symmetric hollow
   `70x70` `D`, a `70x15` `B`, and then the complete `99x99` adjacency

   ```text
   [[U,F,0],[F^T,D,B],[0,B^T,0]].
   ```

4. Recompute every binary, degree, row, column, design, coupling, and nonlinear
   common-neighbor equation directly from `D,B`; also check the complete
   identity `A^2=12I-A+2J` entry by entry.
5. Recompute every product and prefix-threshold auxiliary from the decoded
   primaries.  Require exact equality to the model assignment.  This detects a
   false or shifted variable map even if the primary graph happens to pass.
6. Emit a compact machine-readable result containing input hashes, mismatch
   counts per block, graph degrees, edge count, and the decoded adjacency hash.
   A positive claim is inadmissible without the complete 99-vertex adjacency
   certificate.

## UNSAT-proof validation

A negative claim requires the exact certified DIMACS plus a complete
proof-producing run.  Before such a run, freeze the solver name/version,
command, seed, timeout policy, native proof format, any proof conversion
command, and the independently pinned proof-checker name/version/hash.  Check
the proof against the hashed DIMACS bytes in a fresh process.  A solver exit
code, timeout, heuristic nonhit, partial proof, or a proof for a differently
mapped formula is not evidence of nonexistence.

## Mutation tests required at comparison

The independent checker should reject at least these one-change mutations:

- omit one primary `D` or `B` map record;
- swap two primary ids while leaving the map unchanged;
- map a `D` diagonal or both orientations as separate primaries;
- delete one direction of an AND or threshold equivalence;
- change one `SO`, `SQ`, `OO`, `OQ`, or `QQ` target;
- omit the 21 target-zero duplicate-label `OO` equations;
- accept a model while ignoring auxiliaries;
- accept row/column counts or one abstract design in place of all six blocks.
