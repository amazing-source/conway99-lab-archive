# Wave 94 clean-room verification protocol

1. Freeze every discovery path, size, and SHA-256 before reading the
   derivation or executing its code.
2. Import no discovery module. Reconstruct the rooted
   `K14 - 7K2` scaffold, four-point seeds, transition multiplicities, local
   matching cap, and all arithmetic independently.
3. Define `P` as the number of induced triangular prisms and `n3` as the
   number of two-triangle configurations with exactly two matching cross
   edges. Rebuild `n3+3P=4158` by the induced-`C4` double count.
4. Derive the norm-14 complementary-Fano seed injection from the SRG
   equations and attack its saturation and transition-free steps.
5. Check the prism-to-root multiplicity at all six vertices, both signs in
   `N14`, every compatible `(n3,P)` row, floor residues, and endpoint values.
6. Run hostile controls against cap three, five prism roots, sign-pair
   counting, malformed local matchings, and incompatible `n3`.
7. Compare discovery fields only after the independent reconstruction exists.
8. Preserve `UNKNOWN` for `N16`, `N18`, a strict `n3` upper bound,
   Conway-99, and literature novelty.
