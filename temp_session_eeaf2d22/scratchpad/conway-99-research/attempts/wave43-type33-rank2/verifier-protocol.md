# Independent verification protocol

The verifier should not import `exact_check.py`.

1. Freeze and independently load the Wave 41 secondary verifier source.
2. Reconstruct the type-`3+3` transported core and prove all 144 border
   signatures are zero.
3. Independently derive the `12 x 12` interaction table and matching-matrix
   alphabet.
4. Prove the rank-two principal-pivot lemma over `F_7`.
5. Enumerate all 66 pivot pairs, both pivot-mate cases, and every deranged
   distinct pivot image pair.
6. Reconstruct unary Schur domains and pairwise mate/nonmate requirements
   without calling discovery functions.
7. Compare the complete branch counts and verify zero leaves.
8. Add positive synthetic controls in which a planted rank-two symmetric
   residual is accepted, plus hostile mutations of mate degree, derangement,
   and Schur equations.
9. Preserve the scope wall: this is a one-edge local endpoint theorem, not a
   graph or endpoint exclusion.
