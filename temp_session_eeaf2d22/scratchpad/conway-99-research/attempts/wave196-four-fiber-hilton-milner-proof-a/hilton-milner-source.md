# Frozen Hilton--Milner equality statement

Primary sources:

- A. J. W. Hilton and E. C. Milner, "Some Intersection Theorems for
  Systems of Finite Sets," *The Quarterly Journal of Mathematics* 18(1)
  (1967), 369--384, DOI `10.1093/qmath/18.1.369`.
- Glenn Hurlbert and Vikram Kamat, "New injective proofs of the
  Erdos--Ko--Rado and Hilton--Milner theorems," *Discrete Mathematics* 341
  (2018), 1749--1754; preprint <https://arxiv.org/abs/1609.04714>.

The readable preprint states the full equality classification explicitly
as Theorem 11: equality holds exactly for the family `H`, or, when
`r=3`, the exceptional family `K`. Its definitions immediately preceding
Theorem 11 match the two templates frozen below.

Exact specialization used:

```text
For a nontrivial intersecting family of 3-subsets of a 7-set,
|F|<=13.

At equality, up to relabeling, F is one of:

H = {X} union {{s} union E:
               E is a 2-subset of the other six points,
               E intersects X},
    where |X|=3 and s is outside X;

K = {A: |A intersect X|>=2},
    where |X|=3.
```

In `H`, the three pairs `{s,t}`, `t in X`, have degree five. In `K`, the
three pairs contained in `X` have degree five.

Access checked: 2026-07-28.
