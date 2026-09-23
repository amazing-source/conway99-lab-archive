# Rank-26 equality reduction

## Frozen premise

Wave 41 independently verified the following decomposition for each labelled
39-point edge-local block. Let `e` be the number of even parts in the
alternating partition of six determined by the first two fibre matchings.
Then, over `F_7`,

```text
rank(K39) = (25 - 2e) + 2 rank(F) + rank(B),
rank(F) >= e,
```

where `B` is a symmetric Schur residual on the canonical right kernel of
`F`. Consequently,

```text
rank(K39)=26
iff
rank(F)=e and rank(B)=1.                         (1)
```

The Wave 41 minimum-`F` enumeration is complete and labelled. It uses no
automorphism of a completed graph.

## Even-part types

For each of the seven types containing an even part, the checker enumerates
every minimum-`F` permutation. For each permutation it enumerates all
`11!!=10,395` labelled perfect matchings `R` on the third fibre and computes

```text
B = Z^T W_R Z - T
```

exactly over `F_7`.

The diagonal filter is lossless for the target rank. A nonzero symmetric
rank-one matrix has the form

```text
B = lambda v v^T.
```

It therefore has a nonzero diagonal coordinate, and every nonzero diagonal
entry lies in the same quadratic-character class. Over `F_7` these two
classes are

```text
{1,2,4}, {3,5,6}.
```

Only residuals satisfying that necessary condition proceed to exact Gaussian
elimination. Thus a filtered residual cannot have rank one, and every retained
residual is decided exactly.

## All-odd types

For an all-odd type, `e=0`, every labelled border permutation has `F=0`, and
the canonical right kernel is the full 12-dimensional space. Directly
materializing

```text
12! * 10,395 = 4,979,221,632,000
```

pairs per type is unnecessary.

Fix a labelled third-fibre matching `R` and suppose

```text
B = W_R - T
```

has rank one. Since `B` is symmetric and nonzero, it has a unique first
position `p` with `B_pp != 0`. The search enumerates `p` and the image of `p`
under the border permutation. For every pair of coordinates,

```text
B_ik B_pp = B_ip B_pk.                           (2)
```

Once the pivot assignment is fixed, equation (2) gives:

1. a unary compatibility condition for every remaining assignment;
2. a pairwise compatibility condition between any two assignments; and
3. the ordinary all-different condition for a labelled permutation.

The backtracker exhausts every assignment satisfying those conditions. This
is complete because every rank-one residual has exactly one chosen first
nonzero diagonal pivot, and equation (2) is both necessary and sufficient
when `B_pp` is invertible. Every emitted leaf is rechecked by dense exact
rank and by the full 39-by-39 block rank.

No graph automorphism is imposed. All 10,395 labelled `R` matchings are
visited, and the permutation search is an exact implicit enumeration of all
`12!` labelled border permutations.

## Candidate consequence

If all eleven atomic outputs report zero rank-one residuals, (1) gives

```text
rank_F7(K39) >= 27
```

for every edge-local block. Since the block is principal in the transported
global matrix and Wave 41 verified exact rank transport, the candidate global
consequence is

```text
rank_F7(M) >= 27.
```

This is a discovery claim until an independent verifier reconstructs the
finite searches and the all-odd CSP completeness argument.

