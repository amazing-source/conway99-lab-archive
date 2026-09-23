# Hostile and positive controls

Claim label: `DERIVED`.

- Both row and column codegrees are checked. The first implementation caught
  an invalid one-sided candidate and was corrected before sealing.
- Duplicate weight-four rows are rejected by the pair-codegree guard.
- Canonical keys are tested after a nontrivial row and column relabelling.
- The anchored enumeration is quotiented only after a complete coverage
  normalization; no target automorphism is assumed.
- Deficiency multisets are checked to contain exactly eight pairs and to be
  2-regular on all eight vertices.
- A positive bounded-contingency instance and a one-cell-deleted negative
  instance test the integral flow routine.
- Every exact outside spectrum must have traces `0,1002,906` through degree
  three and a nonnegative integral four-cycle count.
- The SRG eigenvalue multiplicities are recomputed as 54 for eigenvalue 3
  and 44 for eigenvalue -4. Reversing them fails `trace(D)=0`.
- A surviving coupling or histogram is never promoted to a graph
  construction.
