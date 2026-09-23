# Independent verification protocol

## Frozen claim

Assume the Wave 181 equality regime, hence 2,079 root incidences, and the
Wave 182 conclusions:

1. for each nonedge `uv`, the two common neighbors define its unique
   projective root `rho_uv`;
2. opposite nonedges of a canonical 4-cycle have orthogonal norm-one roots;
3. the complement of the graph induced on a root support `X_r` is
   4-regular;
4. `sum_r m_r (r tensor r)=0` over `F_3`.

Verify the Wave 183 support classification and its global counting
consequences without using discovery code as evidence.

## Method

- Re-derive the common-neighbor bound from the strongly regular parameters,
  exact nonedge-root uniqueness, and canonical-4-cycle orthogonality.
- Count unordered length-two paths only by their middle vertices and prove
  injectivity into unordered endpoint pairs.
- Treat the cubic case by triangle-edge incidence and local degree, not by
  graph enumeration.
- Classify regular graphs of degrees 0, 1, and 2 on 5, 6, and 7 vertices.
- Recompute the incidence interval, defect equation, and frame coefficients
  with exact integer/modular arithmetic.
- Run hostile unit tests at each excluded boundary.

## Acceptance rule

Promote only the stated conditional deductions.  Do not promote the equality
regime, rank 11, or the endpoint itself.
