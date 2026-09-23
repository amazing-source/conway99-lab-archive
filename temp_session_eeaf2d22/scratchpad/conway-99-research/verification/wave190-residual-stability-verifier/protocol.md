# Clean-room protocol

1. Freeze the sealed Wave190 source, both proof-agent accounts, and the sealed
   Wave189 verifier on which the pool theorem depends.
2. Do not import or execute discovery code during derivation.
3. Separate raw assignments, residual assignments, and actual circuits.
4. Reconstruct exact-one slack from actual label capacity.
5. Audit all three collision classes: low raw circuits, old exact-three
   orbits, and genuinely new residual circuits.
6. Charge raw and residual uses to labels, not to the two members of an orbit.
7. Verify the master residual inequality as a sum of five nonnegative slacks.
8. Verify `6Q>=8C` coefficientwise and test the sharp arithmetic row.
9. Keep the conditional theorem separate from cover realization, endpoint
   exclusion, and Conway-99.
