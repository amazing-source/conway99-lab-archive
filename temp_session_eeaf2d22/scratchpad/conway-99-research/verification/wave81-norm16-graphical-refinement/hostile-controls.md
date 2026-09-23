# Hostile controls

The test suite attacks the refinement with controls independent of the
50-row target census.

## Exhaustive simple-graph oracle

For each `n=1,...,6`, the test enumerates all `2^(n choose 2)` labelled
simple graphs and records their sorted degree sequences. It then
enumerates every nonincreasing length-`n` sequence with entries in
`0,...,n-1`. Both Erdos-Gallai and Havel-Hakimi must agree with the
brute-force membership oracle on every sequence.

This includes odd-sum sequences, impossible maximum degrees, and
inequality failures at different values of `k`.

## Exhaustive bipartite oracle

The test enumerates all `2^9` labelled `3 x 3` bipartite graphs and all
pairs of nonincreasing three-entry sequences in `0,...,3`. Gale-Ryser and
bipartite Havel-Hakimi must each agree with the brute-force oracle on every
left/right pair.

An explicit unequal-marginal control `[2,2]` versus `[1,1]` is rejected.

## Domain and indexing controls

The verifier rejects:

- any change to the three frozen source hashes;
- a source lane other than `t=0` or `t=1`;
- a lane count other than 43 or seven;
- duplicate histogram triples;
- malformed, negative, wrong-width, or wrong-population histograms;
- disagreement between the two exact criteria;
- failure to check any of the six type pairs for all 50 rows.

The three rejected rows retain both zero-based source indices and
one-based stable row IDs in the result artifact.
