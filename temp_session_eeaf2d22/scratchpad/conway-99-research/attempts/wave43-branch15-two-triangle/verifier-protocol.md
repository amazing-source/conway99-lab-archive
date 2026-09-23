# Independent verifier protocol

The verifier must not import either Wave 43 discovery implementation. It
should work from the frozen Wave 37 OPB, the published Wave 42 inputs, the
rooted labelling convention, and this statement.

## Frozen inputs

1. Bind the Wave 37 branch-15 compressed OPB to gzip SHA-256
   `7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e`
   and decompressed SHA-256
   `4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5`.
2. Bind the Wave 42 seventh-triangle delta to gzip SHA-256
   `0840524515920a59fd3d0f0666b496f9e639476dd887d0d90df5bb58a9e8904e`
   and decompressed SHA-256
   `348dc5f4bc9ee99511286a8078d0e4ef79786b57ba39ae572c032e42747be77e`.
3. Independently replay or validate the Wave 42 closure at SHA-256
   `ab05feb596c25d0fbb872a0d92978355638218350bdf7606c248ca98ae2469ce`;
   do not trust its assignment list merely because it parses.

## Clean-room derivation

1. Reconstruct the 84 labels `(a,b)` with `0 <= a < b < 14` and
   `floor(a/2) != floor(b/2)`.
2. Reconstruct the 3,486 primary residual-edge IDs in lexicographic order.
3. Enumerate the 924 coordinate-anchored potential triangles.
4. Classify their controller variables under the independently replayed
   closure and obtain exactly 7 true, 157 false, and 760 unfixed triangles.
5. Visit all 288,420 unordered pairs of unfixed triangles; retain exactly
   259,499 vertex-disjoint pairs.
6. Visit all 1,556,994 perfect matchings. Independently prove and check that
   the only 40,800 compatible visits have mate coordinate anchors matched to
   each other, arising from 20,400 mate-anchor triangle pairs.
7. Convert every compatible visit to its sorted positive-variable catalogue
   for an all-negative clause. Confirm 40,800 distinct width-four clauses.
8. Scan the base OPB and Wave 42 delta and confirm zero exact raw-row overlap.
9. Compare the canonical raw catalogue hash
   `cafd0eddbc8371d59f7fb184b51f6a6facdeee9d1a50bbea7b30b95e2fa2b462`.
10. Compare the deterministic raw-delta gzip SHA-256
    `82a13e78e514cf35f27190da665bdedaf4fed28c7a6fa2856e22badf63f32797`
    and decompressed SHA-256
    `23fc3b22b4b235cc631bfd0b53ed2806394273aa1b4c691c883ebe343788d3f1`.

## Closure and probe replay

1. Simplify all 40,800 rows under the independently reconstructed closure.
   Confirm 6,460 satisfied rows, zero empty rows, and 34,340 distinct new
   active width-four rows.
2. Compare the active catalogue hash
   `8c8afac5833ce5a2739fa6043d255adae5e3eb52b6bc75799fcd2ce86d297bf8`
   and active-delta gzip SHA-256
   `858f2a5c66d251497e4c13fb4d633c18fe65afe657937b84444cde55b1a4a631`.
3. Check every active row has slack three. Combined generalized-unit closure
   must therefore remain exactly 830 assignments, including 174 primary
   assignments, with no contradiction.
4. Independently reconstruct the active-cut incidence ordering and the 32
   selected controller variables. Replay all 64 polarities against all three
   formula components, validating every cited source row and derivation.
5. Confirm zero failed polarities, zero candidate implications, and zero
   Wave 43-delta-sourced derivations.

## Required status wall

The verifier must reject promotion to `SAT`, `UNSAT`, endpoint exclusion,
strict upper bound, or Conway-99 solution. Even a later checked `UNSAT` result
for branch 15 would close only one of the 33 endpoint cases.

