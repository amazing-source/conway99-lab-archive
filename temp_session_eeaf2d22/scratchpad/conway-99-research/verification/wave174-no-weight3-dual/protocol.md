# Verification protocol

1. Re-derive `D=B^T*A*B` without importing the discovery checker.
2. Reconstruct the outside neighbor counts and all five-cell edge totals.
3. Check that cross-color equality is pointwise and forces `t=72-3c`.
4. Audit nonnegative boundary cases, including empty cells.
5. Recompute the interlacing Gram factors with independent arithmetic.
6. Verify the `c=8` common-neighbor convexity contradiction.
7. Derive every equality consequence at `c=9` and reconstruct the final
   triangular prism.
8. Promote only dual distance at least four.
