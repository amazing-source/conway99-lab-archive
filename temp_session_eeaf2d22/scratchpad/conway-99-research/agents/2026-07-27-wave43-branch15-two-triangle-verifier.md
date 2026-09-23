# Wave 43 branch-15 two-triangle verifier

Role: verifier  
Claim label: `VERIFIED_SCOPED`  
Frozen commit: `e28f90464d00b98d37672b0b2b23dba15399a6f2`

The independent streamed implementation reproduced the complete restricted
family exactly: 924 coordinate triangles, closure split `7/157/760`,
288,420 eligible pairs, 259,499 vertex-disjoint pairs, 20,400 mate-anchor
pairs, 1,556,994 matching visits, and 40,800 distinct compatible cuts.

All accepted visits were checked to use mate anchors and to match the two
anchors to each other. The raw and closure-active catalogues match the
discovery package exactly, including deterministic decompressed and gzip
bytes. The active catalogue contains 34,340 width-four rows after 6,460 raw
rows are satisfied, and every active row has slack three.

The independently replayed 64 probes match every discovery pass and
derivation record. There are zero failed polarities, implications,
contradictions, or Wave 43-sourced derivations.

Publication recommendation: publish as `VERIFIED_SCOPED`, with the explicit
wall that only pairs of closure-unfixed coordinate-anchored triangles are
complete. Do not claim branch closure, endpoint exclusion, a strict upper
bound, or a Conway-99 solution. No completed-graph automorphism is assumed.
