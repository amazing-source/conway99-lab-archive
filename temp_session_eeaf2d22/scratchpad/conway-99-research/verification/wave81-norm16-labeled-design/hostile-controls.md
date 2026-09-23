# Wave 81 hostile controls

- The discovery package was inventoried and SHA-256 frozen before any file
  was inspected. Its manifest hash recomputes to
  `6c05ff8ef0f97b1c9af0a1fbe1106ec07f826e819869660262fe92b9478033bd`,
  with zero member mismatches.
- The verifier never imports `attempts/.../exact_check.py`.
- Support enumeration checks row and column degrees and row and column
  codegrees. Orbit classification exhausts all `8!` column relabellings;
  it assumes no target automorphism.
- A nontrivial row and column relabelling remains in the generated
  `S8 x S8` orbit.
- Every deficiency multiset has exactly eight occurrences and degree two
  at every support vertex.
- Coupling recursion treats repeated deficiency occurrences as
  indistinguishable but retains every distinct `(P-pair,N-pair)` multiset.
- The local marginal checker is an independent exact dynamic program, not
  the discovery max-flow routine. All 4,985 positive rows pass.
- A null control removes every capacity from a positively demanded row and
  is rejected.
- The histogram checker reproduces the exact discovery row sets, not merely
  the totals `43+7`.
- Havel-Hakimi and Gale-Ryser are separately applied to all type-subgraph
  degree sequences. The three new deletions are isolated as `DERIVED`.
- The full SRG multiplicities are recomputed as `3^54` and `(-4)^44`.
  Their Jacobi exponents are `38` and `28`; swapping them yields
  `trace(D)=-70`, while the corrected factors yield zero.
- Exact residual polynomial coefficients, determinants, traces through
  degree four, and four-cycle counts match the frozen discovery artifact.
- A surviving row is never called a graph construction. Conway-99 and
  novelty remain `UNKNOWN`.
