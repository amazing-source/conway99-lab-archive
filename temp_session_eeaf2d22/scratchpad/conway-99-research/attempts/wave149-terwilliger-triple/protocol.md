# Protocol

## Scope

This package studies only the triangle-root Terwilliger/triple-intersection
projection for a hypothetical `srg(99,14,1,2)` at `n3=4158`.

## Certification boundary

- Standard-library exact arithmetic reconstructs the complete Gram witness.
- PSD is certified by integer character determinants, not floating-point
  eigenvalues.
- The explicit witness certifies feasibility only of the stated projection.
- A Gram matrix is not promoted to a binary incidence factor.
- Solver timeout or `unknown` status is not negative evidence.
- No automorphism of a putative graph is assumed. The displayed permutation
  system is an abstract local witness used to refute the strength of the
  relaxation.

## Promotion rule

A stronger result requires one of:

1. an exact contradiction valid for every prism-free permutation system; or
2. an exact binary factor `C`, followed by exact replay of all `D` equations.

Neither has been obtained here.
