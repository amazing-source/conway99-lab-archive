# Wave 105 independent verification protocol

## Frozen scope

The discovery input is the sealed manifest
`b0fd40eda5a3677d4a835788cea20dfcb9bb3c5764719fc04536893f1b5da4a1`.
The claim is conditional on a hypothetical `srg(99,14,1,2)` containing the
induced 12-vertex `C4 box K3` motif. No claim that every target contains this
motif is in scope.

## Independence and gates

1. Reconstruct the motif and its residual pair capacities without importing
   discovery code.
2. Prove that the positive residual-pair support is triangle-free before
   accepting the incidence multiset as forced.
3. Re-derive all three block equations, all type-edge formulas, every aggregate
   moment row, and all six graphicality filters.
4. Decode the archived linear witness from scratch; check binary symmetry,
   degrees, all 1,044 entries of `DP=2J-P-PH`, and its upper-triangle hash.
5. Check the nonlinear outside-pair equation on that witness rather than
   trusting its label.
6. Audit the discovery SAT source against the independently derived equations,
   truth-table the conjunction clauses, and prove that the four `X0` branches
   cover all eight labelled three-vertex graphs up to row permutation.
7. Accept raw bounded logs only by SHA-256 and exact field comparison.
8. Keep every timeout `UNKNOWN`; accept SAT only after direct SRG replay and
   UNSAT only after an independently replayable proof.

The verifier may clarify or veto a claim but does not modify the discovery
package.
