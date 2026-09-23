# Wave 35 independent verifier audit

**Verdict:** `VERIFIED_SCOPED_WITH_WORDING_QUALIFIER`

The verifier independently reconstructed the submitted endpoint calculations
from the strongly regular graph parameters, without importing discovery-side
Python or JSON. The following conditional claims check exactly:

- \(n_3=4158\) forces \(q(T)=12\) for all 231 triangles and the profile
  \((a_0,a_1,a_2,a_3)=(32,144,36,0)\).
- The signed matrix satisfies
  \(S^2=13S+68I\), has spectrum \(17^{44},(-4)^{187}\), and has Smith form
  \(\operatorname{diag}(1^{44},4^{143},68^{44})\).
- \(C=2S-13I\) satisfies \(C^2=441I\), has spectrum
  \(21^{44},(-21)^{187}\), row sum \(-21\), and row squared norm 441.
- All 40 primitive-projector Schur triples were reconstructed from exact entry
  classes: none is negative, 15 are zero, and the smallest positive value is
  \(1/231\). The Schur-power, compression-trace, and Frobenius scalar
  calculations agree.
- Every actual adjacent local 12-by-12 cycle type is positive definite. The
  submitted nonadjacent 7-by-7 object is only a relaxed margin/cell witness.
- Rank 44 implies every 45-by-45 principal submatrix of \(M\) is singular.
  A set with support degree
  \(\max_i\sum_{j\in X}|S_{ij}|\leq 3\) would contradict this by Gershgorin.

The wording qualifier is material but non-refuting: “absolute signed degree”
must mean the support degree \(\sum_j|S_{ij}|\), not the absolute algebraic row
sum \(|\sum_j S_{ij}|\). A switched negative \(K_5\) has support degree 4,
absolute algebraic row sums at most 2, and eigenvalue \(-4\); it also shows that
the threshold 4 is insufficient.

The verifier found no endpoint matrix, no 45-set meeting the sufficient
condition, and no contradiction below 4158. Mixed-Schur nonnegativity, scalar
feasibility, and the relaxed nonadjacent witness are failures of proposed
obstructions, not existence evidence. Thus the endpoint remains unexcluded,
the bound is not improved, and the Conway-99 target remains `UNKNOWN`.

Reproduction completed with 10 independent verifier tests passing and all 14
submitted discovery tests replaying successfully. The submitted frozen JSON
and the independently generated JSON both passed their exact self-verification
commands.
