# Wave 177: universal short relations by code averaging

Status: `DERIVED_PENDING_VERIFICATION`.

Wave 176 proves that every pair of labelled vertex-stars has a genuine
cross-star relation, but leaves only the loose support range `4..13` in two
adjacent cycle types and `4..14` on nonedges.  A full-support ternary-code
average removes that gap without enumerating any candidate.

```text
every edge:    a true cross-star relation of weight 4..8,
every nonedge: a true cross-star relation of weight 4..9.
```

For an edge, the relation can avoid the shared triangle block.  Its
coefficient sum is then zero, so it holds for both centered and uncentered
factor columns.

The type `4+2` weight-four relation has a precise geometric meaning: after
switching its four columns by their nonzero coefficients, they are exactly
the four singular points of a plane conic `Q(2,3)`.  The other nine points
of `PG(2,3)` cancel the conic's outer-product contribution exactly.  Thus
local projective 3-divisibility and the zero-frame identity do not forbid
the conic.

No graph, code, SAT, or isomorphism search is used.  The global overlap of
the edge-indexed short relations, rank 11, and the endpoint remain
`UNKNOWN`.
