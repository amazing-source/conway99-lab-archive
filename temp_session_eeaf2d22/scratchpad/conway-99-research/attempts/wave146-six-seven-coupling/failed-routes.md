# Failed and bounded routes

## Reusing the selected Wave 144 profiles

The first selected local profile used a rooted type that is not locally
admissible on seven vertices.  Replacing every selected profile by a
seven-extendable profile repairs that local defect, but the fixed collection
then violates `R_(38,8)=2R_(37,12)` by `3,076,026,288`.

This refutes one certificate, not the endpoint.

## Unscaled HiGHS feasibility

The unscaled full LP reported infeasibility.  A first row normalization made
some legitimate deck coefficients smaller than HiGHS's matrix cutoff and
even produced a spurious one-row IIS.  Both records are numerical failures,
not mathematical evidence.

Column-aware scaling based on exact combinatorial variable bounds instead
returned a feasible point.  Reconstruction with denominator at most four
then produced the stored exact witness.

## One-root coupling

The exact witness shows that retaining only one outside vertex at a time is
insufficient.  The remaining gap is compatibility between two roots, or
equivalently between rooted seven-set views on an eight-vertex union.
