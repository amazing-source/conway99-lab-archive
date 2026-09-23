# Independent verifier request

Please verify this package without importing `exact_check.py`.

1. Rebuild the Wave 105 incidence multiset and `Q=[one P]`.
2. Recompute `G=Q^TQ`, its determinant, and its local Smith profiles at
   `2,3,5,7`.
3. Derive `BQ=QC` from the linear block equations and check
   `GC=C^TG`.
4. Check independently that `(C^T)^2-7C^T` has every column in `GZ^13`.
5. Recompute the Smith profiles of `[G|C^T]` and `[G|7I-C^T]` using a
   separate algorithm or implementation.
6. Audit the identification of those two cokernels with the `K` and `U`
   primary discriminant components.
7. Independently derive the characteristic-vector correction
   `q=(y_0-x^TGx)/2`, enumerate the six finite primary Gauss sums, and
   certify their phases without floating-point recognition.
8. Check the seven-primary anti-isometry, equal determinant valuations,
   and exponent-seven conclusion.
9. Check the Milgram deduction that both seven-primary forms have phase
   `-1` and type `O^-(k,7)`.
10. Attack the norm-two exclusion, including signs and the coordinate chosen.
11. Preserve `UNKNOWN` for every rank exclusion, motif extension,
   Conway-99, and novelty claim.
