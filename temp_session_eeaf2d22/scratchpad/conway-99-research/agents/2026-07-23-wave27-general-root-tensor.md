# Wave 27 orthogonal root-summand tensor obstruction

```yaml
role: proof_b
date_utc: 2026-07-24T00:24:24Z
git_commit: 2ac11809fafee7ab752965ae49a96e922859b5ee
claim_label: DERIVED
scope: >-
  Exact necessary cubic-tensor obstructions for orthogonal A6 and E6
  summands of the scaled-dual endpoint lattice. Any orthogonal A6 summand
  is incompatible with global cubic trace 60. Any orthogonal E6 summand
  has local cubic floor 24, while its rank-38 complement forces local
  trace at most 22, so it too is incompatible. Conditionally, if the
  entire rank-44 scaled-dual form is an orthogonal ADE root lattice, only
  h=21 and A20 orthogonal_sum E8^3 survives this screen.
inputs:
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
  verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md: 642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de
  verification/wave26-a2-frame-obstruction/2026-07-23T225015Z-audit.md: 5ec6b1924fb9ca2ab9295808178684751b6a90e43315d00cbf232ba8d9fe84a3
  verification/wave26-a2-cubic-obstruction/2026-07-23T231001Z-audit.md: 883f48e70336b87955f5c2a115ac8b137169310c6f5ef91fe4581cb1b6c10465
method: >-
  Orthogonal block compression of the verified Schur cubic tensor,
  frame-forced repeated-index parities, exact symmetric-cubic Gram
  matrices, Fraction-valued LDL sphere enumeration with exact integer
  interval bounds, zero-sum energy divisibility modulo six, a complement
  AM-GM trace budget, and a complete rank-44 ADE decomposition census.
command: |-
  cd attempts/wave27-general-root-tensor
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave27-general-root-tensor/exact_check.py: 107907f610b83ddbb526daddeaa1fe850a0bd73e2dfeeaa386ca578a875bf8d5
  attempts/wave27-general-root-tensor/test_exact_check.py: 3d9197c959b4624755243d21ecdc10dda95012b083717199f055f19a8872123f
  attempts/wave27-general-root-tensor/exact-results.json: 98aba5a30b2f3a83b9f6ce6fd6a20458505b668249d97b0810907de50cae678d
  attempts/wave27-general-root-tensor/input-freeze.sha256: 13c5327b27ad81311e7857460c777db85064141fbdd8b33b5a8906f456647eaa
  attempts/wave27-general-root-tensor/failed-routes.md: e806127f2140212277651ffa47b24087f79d6ba59c91b5aa290f1d73ac51f1d4
limitations:
  - Discovery-agent derivation pending a fresh independent verifier.
  - Every component theorem requires an orthogonal integral summand; a
    nonorthogonal root subsystem is outside scope.
  - The full-ADE conclusion assumes the entire scaled-dual form is an
    orthogonal sum of irreducible ADE root lattices.
  - A20 orthogonal_sum E8^3 survives the conditional screen.
  - No primitive embedding, 231-row frame, Schur certificate, graph,
    endpoint exclusion, formal-kernel proof, or novelty result is supplied.
  - n3=708, Conway-99 existence, and novelty remain UNKNOWN.
```

## Result and status wall

The main exact necessary conditions are

```text
full endpoint projector/Schur origin
  ==> no orthogonal A6 summand in S,
  ==> no orthogonal E6 summand in S.                 (1)
```

The second conclusion is not restricted to a displayed block-diagonal
choice of `Q`.  Arbitrary cross-block entries are allowed.

A complete conditional ADE census then gives

```text
S is an orthogonal rank-44 ADE root lattice
  ==>
h=21 and S is isometric to A20 orthogonal_sum E8^3  (2)
```

as the only type not excluded by the current component tests.  Statement
(2) is conditional on the full root-lattice hypothesis.  It does not exclude
any `h` row among general even lattices and does not construct the surviving
type's required origin.

The scope wall is:

```text
orthogonal A6 summand:                              REFUTED
orthogonal E6 summand:                              REFUTED
full ADE root-lattice types other than A20+E8^3:   REFUTED CONDITIONALLY
A20+E8^3 full projector/Schur origin:               UNKNOWN
all unrestricted h/index rows:                     UNKNOWN
n3=708:                                             UNKNOWN
Conway-99 existence and novelty:                    UNKNOWN
```

## 1. Projector frame and cubic compression

Use the audited endpoint package

```text
X in Z^(231 x 44),
G=X^T X,
S=21 G^-1,
M=X S X^T,
W=M o M,
Q=X^T W X.
```

After an integral congruence, suppose the scaled-dual form has an orthogonal
integral summand

```text
S=R orthogonal_sum C,
rank(R)=r.
```

Write each row as `x_i=(z_i,y_i)`.  The frame identity and `M 1=0` give

```text
sum_i z_i z_i^T = 21 R^-1,                        (3)
sum_i z_i = 0.                                    (4)
```

Let

```text
T=sum_i (S^(1/2)x_i)^(tensor 3)
```

and let `K=S^(1/2) Q S^(1/2)` be the orthogonal Schur endomorphism from the
verified tensor factorization.  Then

```text
K is positive definite,
tr(K)=||T||^2=60.                                 (5)
```

Compression to the Euclidean space belonging to `R` yields

```text
tau_R := tr(R Q_RR)
       >= ||P_R||^2_(R tensor R tensor R),         (6)

P_R := sum_i z_i^(tensor 3).
```

This is simply orthogonal projection of the full tensor norm.  Mixed tensor
blocks are squared nonnegative terms; cross-block entries of `Q` cannot
lower (6).

## 2. A general complement upper bound

The complementary compression is

```text
K_C=S_C^(1/2) Q_CC S_C^(1/2).
```

Because `S_C` and the positive-definite principal block `Q_CC` are integral,

```text
det(K_C)=det(S_C) det(Q_CC)
```

is a positive integer.  AM-GM on its `44-r` positive eigenvalues gives

```text
tr(K_C) >= 44-r.
```

Together with (5),

```text
tau_R <= 60-(44-r)=r+16.                          (7)
```

For any rank-six orthogonal summand,

```text
tau_R <= 22.                                      (8)
```

This argument uses only the principal complement block.  It does not assume
that `Q` is block diagonal.

## 3. Frame parity of the symmetric cubic

Fix an integral basis of `R` and put

```text
N=21 R^-1,
P_abc=sum_i z_ia z_ib z_ic.
```

For every pair of coordinates,

```text
P_aab
 =sum_i z_ia^2 z_ib
 =sum_i z_ia z_ib        (mod 2)
 =N_ab                   (mod 2).                 (9)
```

The same identity includes `a=b`.  It is unaffected by norm-four
projections and needs no classification of the row projections.

Index `P` by the 56 triples

```text
0 <= a <= b <= c < 6.
```

Expanding each symmetric coordinate into all distinct ordered permutations
gives an exact integral 56-by-56 Gram matrix `Gamma_R` satisfying

```text
||P_R||^2=P^T Gamma_R P.                          (10)
```

Thus (9) puts every possible projected cubic in an explicit affine sublattice
of `Z^56`.

## 4. Exact complete sphere enumeration

For both `R=E6` and `R=A6`, the checker forms

```text
Gamma_R=L D L^T
```

with `fractions.Fraction`.  The symmetric triples are in lexicographic
`combinations_with_replacement` order.  Recursion assigns coordinates from
index 55 down to zero.  Once later coordinates are fixed,

```text
P^T Gamma_R P
 =sum_i D_i (P_i + sum_(j>i) L_ji P_j)^2.         (11)
```

At each node the remaining rational inequality is multiplied by the exact
denominator of its center.  `isqrt` then gives the complete integer interval;
intersecting it with the residue progression from (9) enumerates every and
only admissible coordinate.  There is no floating-point bound or heuristic
pruning.

The checker reconstructs `Gamma_R` byte-for-byte from `L,D` before searching.
The exact results are:

| component | dimension | forced odd repeated coordinates | closed cap | accepted partial nodes | complete leaves |
|---|---:|---:|---:|---:|---:|
| `E6` | 56 | 10 | 18 | 10,011 | 0 |
| `A6` | 56 | 12 | 60 | 105,185 | 0 |

The empty leaf count proves

```text
E6: no frame-parity cubic has squared norm <=18,  (12)
A6: no frame-parity cubic has squared norm <=60.  (13)
```

The result JSON records exact hashes of both Gram matrices and both LDL
decompositions.

## 5. Zero sum makes the energy divisible by six

For every integer `k`,

```text
k^3=k (mod 6).
```

Using (4),

```text
||P_R||^2
 =sum_(i,j) <z_i,z_j>_R^3
 =sum_(i,j) <z_i,z_j>_R                 (mod 6)
 =||sum_i z_i||_R^2
 =0                                    (mod 6).    (14)
```

Combining (12)--(14) gives the safe exact floors

```text
R=E6: ||P_R||^2 >=24,
R=A6: ||P_R||^2 >=66.                            (15)
```

The proof does not claim either floor is attained.

## 6. Excluding orthogonal `E6` and `A6`

For `E6`, equations (6), (8), and (15) would require

```text
24 <= tau_E6 <=22,
```

which is impossible.  Thus any orthogonal `E6` summand is excluded, even
when `Q` has arbitrary cross-block entries.

For `A6`, already

```text
tau_A6 >=66>tr(K)=60,
```

so an orthogonal `A6` summand is impossible without using the complement
bound.

These are summand theorems.  A nonorthogonal embedded root subsystem does
not inherit (3), and no conclusion about one is asserted.

## 7. Exact hostile control: algebra alone permits trace 14

A tempting route proposed that an even positive-definite integral `Q` with

```text
E6*Q=I (mod 2)
```

must have `tr(E6*Q)>=18`.  The checker refutes that statement exactly.

With `H=E6^-1` and

```text
v=(-1,0,1,0,0,-1),
P=v(v^T H)/(v^T H v),
B=I+8P,
Q=HB,
```

it verifies

```text
v^T H v=4/3,
P^2=P,
B=E6*Q=I (mod 2),
Q symmetric, integral, even, and positive definite,
spec(B)={9,1^5},
tr(B)=14,
det(Q)=3.
```

This object is a hostile algebraic block, not a projected frame or Schur
certificate.  It is rejected only when the cubic-origin condition is added.
In particular, the new proof does not conceal a false algebraic trace lemma.

## 8. ADE discriminant screen

For an orthogonal irreducible root component `R`, (3) first requires

```text
21 R^-1 integral.                                 (16)
```

The checker constructs every simply-laced irreducible Cartan matrix of rank
at most 44:

```text
A1,...,A44;
D4,...,D44;
E6,E7,E8.
```

Exact inversion leaves only

| component | rank | determinant |
|---|---:|---:|
| `A2` | 2 | 3 |
| `A6` | 6 | 7 |
| `A20` | 20 | 21 |
| `E6` | 6 | 3 |
| `E8` | 8 | 1 |

The earlier independently verified frame theorem excludes any orthogonal
`A2`; Sections 4--6 exclude `A6` and `E6`.

## 9. Complete conditional rank-44 root census

The checker enumerates all nonnegative component multiplicities with

```text
sum ranks=44,
product determinants in
{9,21,49,81,189,441,729,1029}.
```

There are 17 decompositions across the eight index values.  Applying the
component exclusions removes every decomposition containing `A2`, `A6`, or
`E6`.  The only remaining rank equation using `A20` and `E8` is

```text
44=20+3*8,
det(A20 orthogonal_sum E8^3)=21.
```

For completeness, elementary local AM-GM and even-trace bounds give

```text
tau_A20 >=24,
tau_E8 >=8,
```

so this surviving type has only the noncontradictory aggregate floor

```text
24+3*8=48<=60.
```

No `A20` or `E8` cubic minimum is claimed.

## 10. General fibre capacity and why `A2` is special

For any orthogonal even root-lattice summand, let `n2,n4` count rows whose
projection has norm two and four.  Frame energy gives

```text
2 n2+4 n4=21 rank(R).                             (17)
```

Every fixed oriented-root fibre has size at most three under the exact
off-diagonal alphabet `{-2,-1,0,1}`.  If `alpha4(R)` is the largest code of
norm-four vectors with mutual inner products in that alphabet, then the safe
general capacity condition is

```text
21 rank(R)
 <=6 |Phi(R)|+4 alpha4(R).                        (18)
```

For `A2`, `alpha4=0`, so (18) reads `42<=36`, the known contradiction.
For `A3` and larger, norm-four vectors exist; omitting `alpha4` would be an
invalid generalization.  The tensor-parity route avoids this defect.

## 11. Exact replay and boundary

The standard-library-only suite passed:

```text
Ran 17 tests
OK
```

It independently expands the ordered tensor norm, reconstructs both exact
LDL factorizations, checks every binary parity identity, replays both empty
balls and their exact node counts, verifies relaxed even-scale zero-tensor
controls, checks the trace-14 hostile block, reproduces the complete ADE
component and rank-44 censuses, enforces scope walls, and regenerates LF-only
JSON byte-identically.

The most focused next case is the one left by (2):

```text
S=A20 orthogonal_sum E8^3.
```

One must either derive a valid `A20`/`E8` tensor or projector obstruction, or
construct the missing 231-row origin.  Until then, `n3=708`, Conway-99
existence, and novelty remain `UNKNOWN`.
