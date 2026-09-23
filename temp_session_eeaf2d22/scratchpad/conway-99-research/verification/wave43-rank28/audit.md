# Wave 43 rank-28 clean-room audit

Date: 2026-07-27 UTC

Verdict: **PASS**

## Frozen boundary

The verifier was not blind to the proposed counts, so it does not claim
precomparison ignorance. It froze the discovery inputs and then implemented
a structurally separate search without importing either Wave 43 discovery
checker. Independence rests on reconstruction and method separation.

The trusted prior theorem is the independently verified Wave 42 formula

```text
rank(K39) = (25-2e) + 2 rank(F) + rank(D),  rank(F)>=e,
```

where `e` is the number of even parts in the edge-local partition. Exact
integer enumeration gives the only two rank-27 mechanisms

```text
rank(F)=e,   rank(D)=2;
rank(F)=e+1, rank(D)=0.
```

At `n3=4158` there is no induced triangular prism. A part of size one in the
local partition would give such a prism, so the positive partitions of six
left at the endpoint are exactly `222`, `24`, `33`, and `6`.

## Independent reconstruction

`independent_check.py` rebuilds:

- the 27-point local graph and transported matrix over `F_7`;
- all 144 border columns and radical signatures;
- canonical quotient kernels and Schur targets;
- all 10,395 labelled perfect matchings; and
- literal 39-by-39 blocks for sample rank-formula checks.

No Wave 43 discovery function or module is loaded.

For `222` and `24`, direct lexicographic permutation DFS maintains the exact
incremental `F` row space and immediately prunes branches over the target
rank. This differs from discovery's generated-projective-subspace cover. It
finds:

```text
222: 332 derangements, all F-rank 4;
24:  1,352 derangements, all F-rank 3.
```

Thus neither type has a minimum-rank endpoint derangement. All 17,505,180
remaining labelled permutation/matching pairs are tested for a literal zero
residual, with zero hits.

For type `6`, the direct DFS finds exactly 288 minimum-rank derangements.
Every one of their 2,993,760 residuals is processed by batched exact Gaussian
elimination over `F_7`; none has rank at most two. This route is distinct
from discovery's complete `3 x 3`-minor scan.

The higher-`F` type-`6` mechanism is reconstructed from literal kernel
vectors. Its complete counts are:

```text
pivot-image branches: 1,014
pivot-mate branches:  92,274
unary-surviving:         488
backtrack nodes:       1,058
complete leaves:           0
```

For type `33`, all 144 border signatures independently vanish. Every
symmetric rank-two residual has an invertible principal `2 x 2` minor:
writing `D=X^T H X`, two independent columns of `X` give determinant
`det(X_P)^2 det(H)`, which is nonzero. Exhausting all pivots, deranged pivot
images, and pivot-mate cases gives:

```text
branches:                  666,666
invertible pivots:         491,220
unary-surviving branches:   60,306
backtrack nodes:           122,922
complete leaves:                 0
```

## Nonvacuity and hostile controls

- Batched elimination accepts exact ranks zero, one, and two and rejects
  ranks three and four, including a rank-four matrix whose principal
  `3 x 3` minors all vanish.
- A planted matching form is accepted, while a one-entry target perturbation
  is rejected.
- The type-`6` CSP accepts a planted zero residual with the intended
  derangement and perfect matching after eleven nodes.
- The type-`33` CSP accepts a planted symmetric rank-two residual with the
  intended derangement and perfect matching after eleven nodes.
- A repeated matching vertex is rejected.
- Mutating the fixed-rank constant changes the enumerated equality mechanisms
  and is detected.
- Sample literal 39-by-39 ranks equal the Schur rank formula in every endpoint
  type.

## Comparison and replay

Mechanical comparison checks 36 invariant fields. All match, including both
complete bounded-rank derangement streams, their SHA-256 hashes, all explicit
pair counts, both CSP branch censuses, and every zero-survivor count.

```text
discrepancies: 0
discovery even-package manifest: 11/11 entries
verifier tests: 16 passed
discovery tests inspected: 15 passed
full independent deterministic replay: PASS
```

The full replay ran as one foreground Python process. The checker samples
physical memory and fails below 15%; external pre/post snapshots retained
more than 63% free memory. No background verifier worker remains.

## Logical combination

All four endpoint edge types have local rank at least 28. A local `K39` is a
principal block of the transported global matrix, so its rank is a lower
bound for the global rank. The verified transport identifies that global
rank with `rank_F7(M)`. Therefore

```text
n3=4158  ==>  rank_F7(M)>=28.
```

Equivalently,

```text
rank_F7(M)=27  ==>  the graph contains an induced triangular prism.
```

## Scope wall

The theorem is conditional on `n3=4158`. Rank `28` is compatible with the
global endpoint ceiling `44`; therefore this result does not exclude the
endpoint. It does not improve `n3<=4158`, construct a graph, resolve
Conway-99, or establish novelty or priority.

