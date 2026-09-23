# Failed routes and integrity boundaries

## `t_xy>=7` from local projectivity is refuted

The marked profiles force `t_xy>=6`, not seven.  The explicit `t6_h1`
control has:

```text
rank(F)=11,
det(F quotient)=2,
true relation minimum weight=6.
```

It also has a complete locally SRG-consistent 28-vertex adjacency lift.
Thus neither projectivity nor local dual distance upgrades the lower bound
to seven.

The global average `t=7` only forces compensation as in equation (8) of the
derivation.  It does not make every nonedge equal to the average.

## Exact average `t_xy=7` does not determine `h_xy`

The three rank-11 `t=7` controls realize `h=0,1,2`.  All have pair trace
two, intersection dimension one, quotient determinant two, and true
relation minimum weight at least four.  Hence no function of only these
listed pair data can recover the fourth trace.

## A Gram-kernel collision is not automatically a column collision

Many normalized census rows have a weight-two Gram-kernel word.  Below full
ambient rank this can map to a nonzero vector in the radical of the actual
two-star span.  It is not a true vector relation without an additional
argument.

The package uses Gram-kernel minimum weight as true relation distance only
for its rank-11 controls, where the actual span is forced to be the full
nondegenerate ambient space.  Lower-rank census rows are not promoted or
excluded by their Gram-kernel weights.

## Rank 12 rows are ambient-impossible, not controls

The raw normalized census includes formal profile matrices whose full
two-star Gram has rank 12.  They cannot occur in the fixed 11-dimensional
ambient space and are retained only in the complete histogram.  They are
never counted as admissible modules.

## Normalized counts are not isomorphism counts

The four boundary normalizations cover every matrix up to independent
ordinary row and column relabeling.  Residual permutations can make the
same orbit appear repeatedly.  The counts `646` and `7,886` are exact
normalized labelled enumeration sizes, not numbers of isomorphism classes.

## Local completion is not global completion

The 28-vertex controls enforce every common-neighbor upper bound visible
inside the two-center union.  Unsaturated pairs still require outside
vertices.  No simultaneous assignment of those outside common neighbors,
99-vertex degree completion, 231-block incidence, global code, or graph is
provided.

## Status wall

```text
nonedge profile theorem and t>=6:       DERIVED
complete normalized t=6,7 census:       DERIVED
pair-local determination of h:          REFUTED
actual nonedge h classification:         UNKNOWN
rank-11 endpoint:                        UNKNOWN
Conway-99:                               UNKNOWN
```

