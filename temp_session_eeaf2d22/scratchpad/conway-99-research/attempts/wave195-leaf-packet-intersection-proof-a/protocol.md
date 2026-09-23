# Wave 195 proof-A protocol

1. Freeze the independently verified Wave194 bookkeeping and pool
   separation.
2. Include both selected and raw exact-three companion-pair flags.
3. Use only the canonical Wave180 `A_x(T)` relation; do not assume a
   canonical support for any exact-one circuit.
4. Prove `T -> A_x(T)` injective by the forbidden weight-two difference.
5. Prove the local `A_x(T)` family intersecting by the forbidden
   weight-three sum with the full star relation.
6. Define `j_x` using distinct oriented center-to-leaf labels, not
   multiplicity.
7. Separate the nontrivial Hilton--Milner case from the common-star case.
8. In the common-star case, use both simplicity (`c_x<=15`) and the two
   `lambda=1` neighbor caps to derive `j_x<=12+12+c_x<=39`.
9. Derive the uniform global union bound `J<=99*39=3861`.
10. Audit the lower bound `J>=C-n1-2*n2+a3+b3` orientation by orientation,
    including the two opposite raw orientations of one type-two private
    nonedge.
11. Expand the final rational certificate after the four raw identities.
12. Preserve the fractional null row as arithmetic only.
13. Preserve the failed mixed-orientation leaf-support elimination; do not
    use it in the theorem.
14. Run no graph, code, cover, SAT, LP, configuration, enumeration, or
    isomorphism search.
15. Keep `Q>=6980` labeled `DERIVED` pending an independent verifier.
