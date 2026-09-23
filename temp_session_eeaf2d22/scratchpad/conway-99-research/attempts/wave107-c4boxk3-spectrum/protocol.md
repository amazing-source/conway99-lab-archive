# Wave 107 protocol: spectrum of the Wave 105 principal complement

Claim label: `DERIVED`; independent verification is required.

Freeze the Wave 105 package manifest before calculation. Assume only that a
hypothetical `srg(99,14,1,2)` contains the exact induced 12-vertex
`C4` Cartesian `K3` motif used there. Let `D` be the adjacency matrix on
the remaining 87 vertices.

The lane must:

1. derive the restricted resolvent of the 99-vertex adjacency matrix;
2. apply Jacobi's complementary-minor identity exactly;
3. determine the characteristic polynomial of `D`;
4. test the proposed residual factor `x^2-9x-38` against the forced degree
   sum;
5. record all exact spectral, closed-walk, rank, and Perron consequences;
6. run a dependency-free checker using only integer and rational arithmetic.

No spectral consistency check may be promoted to a motif exclusion, a full
extension, or a Conway-99 result. Literature novelty remains `UNKNOWN`.
