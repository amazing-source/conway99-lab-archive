# Independent verification protocol

1. Freeze the complete Wave 188 source manifest and the five direct verified
   prior manifests.
2. Validate every file named by those six manifests.
3. Do not import or execute any discovery checker.
4. Re-enumerate the exact selected-circuit coefficient domain: both base-star
   supports proper, base weight `4..9`, and all nine affine words of weight at
   least four.
5. Check projective distinctness in an abstract basis `c,s_x,s_y`; do not
   infer distinct words merely from distinct coefficient pairs.
6. Extend the two-transversal capacity argument at support level only:
   both sides at least two gives capacity at most two, and weight above four
   gives exact-singleton support.
7. Reconstruct the one-block projector residue and the anticomplete local
   relation plane independently.
8. Reconstruct the type-two `6+2` and type-three `3+6` words
   coefficientwise over `F_3`.
9. Check every possible collision between the four added word families.
   Use exact realization multiplicity or private-label uniqueness, never
   presumed support uniqueness.
10. Recompute the private-label and word-count coefficient rows exactly.
11. Count actual dual words, not extracted circuits, and keep endpoint
   existence, rank-11 exclusion, external novelty, and Conway 99 `UNKNOWN`.
