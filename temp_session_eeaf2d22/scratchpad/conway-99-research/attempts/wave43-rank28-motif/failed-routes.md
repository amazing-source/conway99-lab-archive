# Retained failed and corrected routes

## Random derangement sampling

Ten thousand random endpoint derangements found no rank-four `F` for type
`222` and no rank-three `F` for type `24`. That diagnostic was misleading:
the complete subspace cover found 332 and 1,352 such labelled permutations.
Random absence was discarded and is not evidence in the theorem.

## Minimum-border equality alone

Repeating the Wave 42 minimum-border search would miss the second rank-27
mechanism:

```text
rank(F)=e+1, rank(D)=0.
```

The generated-subspace streams plus exact zero-residual checks, and the
type-`6` pivot/mate CSP, were added specifically to close this gap.

## Principal `3 x 3` minors only

Vanishing principal `3 x 3` minors does not prove rank at most two. The direct
sum of two hyperbolic planes is a rank-four symmetric counterexample with all
principal `3 x 3` minors zero. The final checker tests every general
`3 x 3` minor; the hostile control is retained in the tests.

## Dense type-`6` rank-two enumeration

The type-`6` rank-two branch contains an enormous labelled permutation
universe. Dense `12! * 10,395` materialization is unnecessary. The exact
canonical first-independent-pivot and pivot-mate CSP covers the same
residual-zero target with 92,274 mate branches and 1,058 backtracking nodes.

## Universal rank 28

This package covers only the even endpoint types and is conditional on
`n3=4158`. It does not prove universal rank 28 away from the endpoint. The
separate type-`33` lane is required even for the conditional endpoint
combination, and discovery cannot verify that combination itself.

## General upper bound

Even a verified conditional endpoint rank floor 28 is compatible with the
known rank ceiling 44. It neither excludes `n3=4158` nor improves the general
upper bound `n3<=4158`.
