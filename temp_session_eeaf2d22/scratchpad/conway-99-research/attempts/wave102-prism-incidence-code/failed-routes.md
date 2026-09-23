# Wave 102 retained boundaries

## Total parity

`sum_v f_v=6P` only proves that the number of odd entries is even. The
triangle-incidence factorization adds a code location for `f mod 2`, but
the even triangle code has at least 44 dimensions and need not exclude
zero.

## Ordinary adjacency polynomials

Every polynomial in the SRG adjacency matrix belongs to `span{I,A,J}` and
has constant diagonal. It cannot recover a nonconstant rooted prism vector.
Tensor or Hadamard information is essential.

## A triangle of prism edges

Three pairwise prism-related triangle blocks would cancel parity, but the
union is the `3 by 3` rook graph and automatically contains three additional
prisms. This excludes total `P=3` parity cancellation, not general
cancellation.

## Four-prism cycle

`C4 box K3` contains exactly four internal prisms and each of its vertices
belongs to two. It passes induced `lambda/mu` cap and spectral-interlacing
controls. It is only a local motif, so neither existence nor
nonextendibility to the full graph has been shown.
