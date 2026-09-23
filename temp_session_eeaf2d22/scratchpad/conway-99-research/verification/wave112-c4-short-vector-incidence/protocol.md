# Wave 112 independent verification protocol

## Frozen input

Before reading or executing the discovery package, freeze the SHA-256 of its
sealed manifest and every entry named by it.  Reject any later byte drift.

## Conditional inputs

Accept only the already verified statements that:

1. the target is an `srg(99,14,1,2)`;
2. the short-vector theta coefficients `N14,N16,N18` count oriented nonzero
   vectors and negation pairs them;
3. their live support types are `7+7`, `8+8`, and `9+9`, with cross degrees
   four in the homogeneous lanes and cross degrees `5,5,4^7` in the norm-18
   `h=1` lane;
4. the rank-28 row has `N14+N16+N18 >= 5868`.

## Independent gates

1. Double-count target nonedges and prove the resulting `K2,2` subgraphs are
   induced.
2. Exhaust all aggregate same-side codegree histograms rather than reuse the
   discovery formula.
3. Keep the adjacent same-sign pair out of the alternating-cycle count in the
   norm-18 `h=1` lane.
4. Compute the raw pigeonhole ceiling before applying antipodal evenness.
5. Reconstruct the rooted-cycle outside partition from anchor degrees and
   `lambda,mu`, including distinctness of the four external edge witnesses.
6. Verify discovery only after the independent result exists.
7. Keep the universal cap, rank-28 exclusion, Conway-99, and novelty unproved.
