# Wave196 clean-room protocol

This protocol was frozen before opening any Wave196 discovery package.

1. Use only the sealed Wave180, Wave194, and Wave195 verifier packages,
   together with the defining parameters of `srg(99,14,1,2)`.
2. For a fixed graph vertex `x`, derive the seven local triangle blocks from
   `lambda=1`.  Classify every nonneighbor `y` by the two blocks containing
   its two common neighbors with `x`, and prove analytically that each of the
   21 pair-types has exactly four vertices.
3. Reconstruct an exact-three flag as `(x,T)` and prove that a flag with
   `A_x(T)={i,j,k}` has one leaf of each type `ij`, `ik`, and `jk`.
4. Apply the verified fixed-center simplicity and pairwise-intersection
   theorem.  For a nontrivial family, use Hilton--Milner to obtain `c_x<=13`.
   If `c_x<=12`, conclude `j_x<=36`.
5. At equality `c_x=13`, state the complete `k=3` Hilton--Milner equality
   classification.  Independently instantiate and check both templates,
   their nonisomorphism, and the three pair-fibres of degree five.  Use the
   four-vertices-per-type theorem to force at least three repeated leaf
   occurrences, so `j_x<=36`.
6. In the common-block family, label the block `{x,p,q}`.  Prove that the
   `p`-neighbor leaf determines first the `q`-neighbor by `mu=2`, and then
   the third leaf by `lambda=1`.  Hence `c_x<=deg(p)-2=12` and `j_x<=36`.
7. Audit that selected, old-`h`, and new-`g` exact-three flags form one
   simple family.  Retain the already verified oriented-label lower-bound
   directions and derive `S36>=0` from `J<=99*36`.
8. Reconstruct the exact rational certificate for `Q>=7029`; check the
   addition of 693 edge-isolated projective circuits and the scalar-word
   conversion.
9. Supply an independent integral arithmetic null for the linear
   certificate.  Label it as accounting only, never as an object.
10. Quarantine unrelated candidate capacity rows and preserve every
    `UNKNOWN` boundary.
11. Freeze the independent mathematical result before obtaining or opening
    any Wave196 source seal.
12. Only after a source manifest is sealed may the verifier compare the
    discovery package and add source-dependent checks.

No graph, code, cover, SAT, LP, family search, construction search,
configuration enumeration, or isomorphism search is permitted in the
clean-room derivation.  The 13 explicitly classified triples in each
Hilton--Milner equality template may be evaluated directly; this is formula
verification, not a search over set families.
