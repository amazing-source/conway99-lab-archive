# Clean-room verifier protocol

Do not import `degree2_windows.py` as the source of the mathematical rules.

1. Check the four frozen input hashes in `input-freeze.sha256`.
2. Independently parse the OPB syntax, literal polarities, and Wave 42 closure.
3. Reconstruct the seven mate-coordinate windows from the 84 residual labels.
   Confirm 24 vertices, 276 primary variables, and exactly 48 complete
   coordinate-incidence blocks per window.
4. For each simplified exact-count block, independently enumerate its Hamming
   slice and compute the degree-at-most-two vanishing space over `F2`.
5. Translate only active clauses of residual width at most two by their
   falsifying-assignment polynomials.
6. Independently saturate the squarefree degree-two row space under
   multiplication of every derived linear row by every free window variable.
7. Compare every axiom-catalog, echelon, final-linear-RREF, and relation hash
   in `degree2-window-result.json`.
8. Confirm the new-linear ranks `2,1,2,2,2,2,2`, all 13 explicit equations,
   zero contradiction, and zero assignment.
9. Repeat with exact-count blocks only and confirm equality of the final
   linear spaces in all seven windows.
10. Independently confirm that the windows partition all 34,340 active Wave
    43 rows and that every row remains an all-negative width-four monomial.

Any discrepancy keeps the relations `CANDIDATE` or makes them `REFUTED`.
Even complete agreement verifies only this scoped algebraic calculation, not
branch UNSAT, endpoint exclusion, a strict upper bound, or Conway-99.
