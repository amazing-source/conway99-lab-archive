# Wave 2 algebra, codes, and design track

```yaml
role: proof_b
date_utc: 2026-07-22T20:39:30Z
git_commit: 08ebf70d728b0d14a86d63005ced704eda7b3b50
claim_label: VERIFIED
scope: parameter-forced consequences conditional on existence
automorphism_assumption: none
verification: verification/2026-07-22-wave2-audit.md
limitations: no existence or nonexistence result; novelty unknown
```

All statements below are necessary consequences of the frozen matrix identity

```text
A^2 = 12 I - A + 2 J.
```

They are not evidence that a graph exists.

## Full adjacency matrix

The exact modular data are

```text
over F_2: rank(A)=54, JCF 0^45 + 1^54;
over F_3: rank(A)=45, JCF 0^54 + J_2(2) + 2^43;
over F_7: rank(A)=98.
```

The length-two block over `F_3` is essential. It follows from
`A(A+I)=-J`: the zero-primary part is semisimple, while `A+I` has rank one and
square zero on the eigenvalue-two primary part.

Direct multiplication gives

```text
A^(-1) = (A+I)/12 - J/84 = (7A+7I-J)/84.
```

Thus every Smith invariant divides 84. Combining this bound with the three
modular ranks and

```text
|det A| = 14 * 3^54 * 4^44
```

forces the complete Smith normal form

```text
SNF(A) = diag(1^45, 3^9, 6, 12^43, 84).
```

## Residual modular Jordan forms

Let `B` be the 84-by-84 residual adjacency matrix, `C` the fixed 14-by-84
endpoint-incidence matrix, and `M=7K_2`. Independent exact row reduction gives

```text
rank_2(C)=13,
rank_2(C^T C)=12,
rank_2(C^T (I+M) C)=6,

rank_3(C)=14,
rank_3(C^T C)=14,
rank_3(C^T (I+J) C)=13.
```

Using the rooted block equations and the reduced rational spectrum gives

```text
over F_2:
  B ~ 1^40 + J_3(0)^6 + 0^26,
  rank(B)=52;

over F_3:
  B ~ 1^6 + 2^30 + J_2(0)^7 + 0^34,
  rank(B)=43.
```

For clarity, `C^T(I+J)C = J+C^TC` has total `F_3` rank 13. The number 7 is
only its contribution on the zero-primary space.

## Residual kernel lattice

For the seven root-matched endpoint pairs put

```text
z_i = C^T(e_(2i) - e_(2i+1)).
```

These vectors span the rational kernel of `B` and have raw Gram matrix
`24 I_7`. Their integer span has saturation index two; a saturated basis is

```text
z_1,...,z_6, (z_1+...+z_7)/2.
```

Its Gram determinant is `24^7/4 = 2^19 3^7`. Since the absolute
pseudodeterminant of `B` is `2^68 3^41`, the top nonzero determinantal divisor
is

```text
Delta_77(B) = 2^49 3^34.
```

Consequently the torsion of `coker(B)` has exactly 25 nontrivial 2-primary
cyclic factors with total 2-adic valuation 49, and exactly 34 3-primary factors,
all equal to `Z/3`. It has no other torsion primes.

The individual 2-primary exponents remain `UNKNOWN`. In particular, the
tempting decomposition `(Z/2) + (Z/4)^24` is not established by the rank and
determinantal-divisor data and is quarantined.

## Binary and ternary codes

Over `F_2`, `A` is a symmetric idempotent. Therefore `im(A)` is an even LCD
`[99,54]` code and its dual is the LCD `[99,45]` code `ker(A)`.

For a dual word with support `S`, write `s=|S|`, `e=e(S)`, and
`t_v=|N(v) intersection S|`. Exact double counting gives

```text
sum_v binom(t_v,2) = s(s-1)-e,
sum_v t_v = 14s.
```

Every `t_v` is even, so

```text
0 <= sum_v (binom(t_v,2)-t_v/2) = s(s-8)-e.
```

Hence every nonzero dual word has weight at least eight. At weight eight,
`S` is independent and every vertex meeting `S` has exactly two neighbors in
it. Rows of `I+A` give the upper bound 15.

The row code also has minimum weight at least eight and at most 14. At weight
eight its support induces `4K_2`, and every outside vertex meets it in zero or
two points.

Over `F_3`, the zero-primary and invertible-primary spaces are complementary,
so `im(A)` is an LCD `[99,45]` code.

## Principal-nullity transfer

Jacobi's principal-nullity theorem applied to the displayed inverse gives, for
every vertex subset `S`,

```text
nullity_Q A[V-S] = nullity_Q(7(I+A[S])-J).
```

In particular:

- deleting the endpoints of an edge leaves nullity one;
- deleting a triangle leaves nullity two;
- deleting an independent `s`-set leaves nullity one exactly for `s=7`, and
  leaves nullity zero otherwise.

For an independent seven-set, a complement-kernel vector is
`w(t)=|N(t) intersection S|-1`.

## Conditional maximum-coclique design

If the graph contains an independent set of size 22, equality in Hoffman's
bound forces every outside vertex to meet it in four points. Those 77
neighborhoods form a simple `2-(22,4,2)` design. The 77-vertex outside graph
`D` is 10-regular with spectrum

```text
10^1, (-1)^21, 3^33, (-4)^22.
```

Pairs of blocks intersect in 2, 1, or 0 points respectively

```text
231, 1540, 1155
```

times. The 385 outside edges split into 154 block pairs meeting once and 231
disjoint block pairs. This is a sharply constrained conditional subproblem,
not a contradiction.
