# Protocol

- The Wave149 package manifest and exact result are hash-frozen inputs.
- Heuristics may discover permutations but cannot certify them.
- Every positive construction is accepted only by direct binary matrix
  multiplication and exact row/column checks.
- A solver timeout, `unknown`, or bare `unsat` status without a replayable
  proof is not a negative certificate.
- A fixed-Q1 refutation is never generalized to all first-stage factors.
- The `D` layer is entered only after all three groups of `C` are certified.
- No automorphism of a putative graph is assumed beyond the explicit local
  matching witness frozen in Wave149.
