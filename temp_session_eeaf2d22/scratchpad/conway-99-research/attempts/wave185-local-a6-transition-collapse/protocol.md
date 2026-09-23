# Wave 185 protocol

1. Freeze only independently verified Wave 181, 183, 184, and rooted Wave 64
   inputs.
2. Prove the cell-edge restriction directly from an induced triangular
   prism; do not enumerate cell graphs or target graphs.
3. Recompute the transition table from rooted degree and endpoint-profile
   equations.
4. Prove the incident-cell capacity with the `mu=2` common-neighbor bound.
5. Keep local companion occurrences separate until nonedge-root uniqueness
   proves they are globally distinct.
6. Check the remaining scalar arithmetic independently with exact integers.
7. Retain equality, endpoint, and Conway-99 status as `UNKNOWN`.
