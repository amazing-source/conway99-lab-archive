# Wave 37 finite-polar and code strengthening

```yaml
role: proof_a
date_utc: 2026-07-27T00:03:38Z
git_commit: efbf74e3edf4d11d853d0129634507b01ff7b577
claim_label: CANDIDATE
scope: >
  Conditional n3=4158 ternary code/design consequences, exact forced
  degenerate-triple counts, and characteristic-seven rank-eleven
  projective orthogonality test.
inputs:
  agents/2026-07-26-wave36-ternary-polar-bound.md: 062e8b5478b93195dae4d9a571677688cefcd7397cda75246dbd03503f7c9b85
  attempts/wave36-ternary-polar-bound/exact-results.json: 7d7c15ad99952ee3ca70582a887e771331156b8ef8e50524d296f1dc15f425a1
  verification/wave36-ternary-polar-bound/independent-results.json: 38ec002886c2a9b38f8d11824dc79e07147b16386dcc3449064633efb630beeb
  attempts/wave35-n3-upper-spectral/exact-results.json: ca1df07bede11642fb1639a2ae554c1a31ce9a58424d5b3e5031c90ad550a194
method: >
  Finite-field Gram factorization; projective self-orthogonal code
  consequences; exact Krawtchouk transforms; ternary and characteristic-seven
  association-scheme intersection algebras; divisibility-refined
  regular-subgraph moments; and signed-triangle geometry.
command: |
  .\.venv\Scripts\python.exe -B -m unittest -v attempts/wave37-polar-strengthen/test_exact_check.py
  .\.venv\Scripts\python.exe -B attempts/wave37-polar-strengthen/exact_check.py --output attempts/wave37-polar-strengthen/exact-results.json
  .\.venv\Scripts\python.exe -B attempts/wave37-polar-strengthen/exact_check.py --verify attempts/wave37-polar-strengthen/exact-results.json
outputs:
  attempts/wave37-polar-strengthen/exact_check.py: fb8baf5260931d5ac9eaf6e9fc288c1a1e4f29d7170ae3c4259ee59a8be934f7
  attempts/wave37-polar-strengthen/test_exact_check.py: 2a3af23ded4deaf506ca741b92c89fdc4d2c999c59f68487978b53f573abdc2d
  attempts/wave37-polar-strengthen/exact-results.json: 0d5daafca72b43d159db5e799689e8818fa61f25de2f2d06225a4619817cdff9
  attempts/wave37-polar-strengthen/input-freeze.sha256: 585f56f356ca7bf5d1c8f7328df6216e273165d5d98261ba1a79269fc4d42564
  attempts/wave37-polar-strengthen/failed-routes.md: 53407cccd3dfdcf6155ab300d7c70c9bc1b6ff7f443a0e644c5ee30dcf5f3e38
limitations:
  - Discovery-side candidates require independent adversarial verification.
  - No endpoint reflection, finite-field configuration, or Conway graph is constructed.
  - The square ternary rank-twelve case survives every tested exact relaxation.
  - Both characteristic-seven rank-eleven determinant classes survive.
  - No rank floor, determinant exclusion, or general n3 upper bound is improved.
  - The endpoint, Conway-99, and novelty remain UNKNOWN.
```

## Verdict

The square `r3=12` case survives, and the characteristic-seven polar route
does not raise `r7>=11`.  This lane nevertheless derives two stronger
conditional structural packages:

1. a projective self-orthogonal ternary code with unusually rigid complete
   weights and Schur-square rank; and
2. at least 31,416 independent balanced triples spanning at least 437
   distinct degenerate ternary three-spaces.

Neither package excludes the endpoint.  The rigorous graph-theoretic bound
remains

```text
n3 <= 4158,
```

and Conway-99 remains `UNKNOWN`.

## 1. A ternary projective self-orthogonal code

Reduce the endpoint reflection

```text
C=2S-13I,  C^2=441I,  C1=-21*1
```

modulo three.  For

```text
r3=rank_F3(C),
```

the symmetric rank factorization is

```text
C=V H V^T,
```

with `V` of size `231 x r3`, full column rank, and `H` nondegenerate.
Since `C^2=0`,

```text
0=V H (V^T V) H V^T
```

and left/right inverses give

```text
V^T V=0.                                           (1)
```

Likewise `C1=0` and injectivity of `VH` give

```text
V^T 1=0.                                           (2)
```

Let

```text
U=col(V) <= F_3^231.
```

Then (1) says `U` is self-orthogonal, and (2) says the all-one vector is in
`U^perp`.  The 231 columns of `V^T` are nonzero and pairwise
nonproportional by the independently verified Wave 36 distinctness lemma.
Thus `U` is a projective ternary `[231,r3]` code and

```text
d(U^perp) >= 3.                                    (3)
```

For a codeword `x`, write `n1(x),n2(x)` for the numbers of coordinates equal
to one and two.  Self-orthogonality and (2) give

```text
n1+n2  = x.x = 0 mod 3,
n1+2n2 = x.1 = 0 mod 3.
```

Therefore

```text
n1(x)=n2(x)=0 mod 3 for every x in U.              (4)
```

The 231 rows of `C mod 3` are projectively distinct words in `U`.  Each has

```text
weight 69,
(n1,n2)=(36,33),
```

and their negatives have the swapped composition.  Consequently the
ordinary weight enumerator obeys the exact necessary condition

```text
A_69 >= 462.                                       (5)
```

### Schur-square rank

Let `B=S^(o2)` be the unsigned 68-regular support graph.  Over `F_3`,

```text
C^(o2)=I+B.
```

This is the Gram matrix of the quadratic Veronese vectors
`v_i^(o2)`, so

```text
rank_F3(I+B) <= binom(r3+1,2).                     (6)
```

The selected orthogonality matrix is `J-I-B`, hence

```text
rank_F3(J-I-B) <= 1+binom(r3+1,2).                 (7)
```

At the surviving boundary `r3=12`, (6)--(7) become

```text
rank_F3(I+B) <= 78,
rank_F3(J-I-B) <= 79.                              (8)
```

Equations (3)--(8) are stronger endpoint restrictions.  They do not prove
that such a code or support graph exists, and they do not contradict it.

## 2. Exact rank-twelve hostile controls

### MacWilliams/Delsarte relaxation

The checker gives the exact real distribution

```text
A_0   = 1,
A_69  = 462,
A_141 = 76965,
A_153 = 288015,
A_162 = 165998.
```

It sums to `3^12`, uses only weights divisible by three, has `B1=B2=0`,
and its full real Krawtchouk transform is nonnegative with `B_j>=A_j`.
However, transformed coefficients `B3` through `B231` are nonintegral.
This is deliberately **not** a formal weight enumerator and not a code.  It
only demonstrates that the basic real Delsarte inequalities, including the
relaxation of `U<=U^perp`, do not exclude the boundary.

### Full oriented association scheme

The checker independently reconstructs the five-class scheme on oriented
norm-two vectors in the square twelve-space.  In the relation order

```text
equal, antipodal, inner 0, inner 1 independent, inner 2 independent,
```

the valencies are

```text
1, 1, 58806, 59048, 59048.
```

The endpoint inner distribution is

```text
1, 0, 162, 36, 32.
```

Its transforms in all five primitive eigenspaces are

```text
231, 249/121, 123/121, 4767/7381, 60/61,
```

all positive.  Thus remembering the signed `36/32` split does not yield a
Delsarte contradiction.

### Divisibility-refined Evans polynomial

For every ambient vector `a`, (1)--(2) imply that the counts of selected
vectors with inner products one and two are separately divisible by three.
The selected orthogonality count is therefore also divisible by three.

For the square rank-twelve orthogonality graph, the outside degrees `b_z`
have

```text
number of outside vertices = 88221,
sum b_z                  = 6754671,
sum b_z^2                = 523215693.
```

The ordinary consecutive-integer polynomial is minimized at `76,77` and
gives `6020322`.  Using the consecutive allowed multiples `75,78` sharpens
this to

```text
sum_z (b_z-75)(b_z-78) = 5843880 > 0.              (9)
```

The refinement is exact but leaves large positive slack.

## 3. The signed triangles force degenerate three-spaces

For every support edge `ij`, multiply the off-diagonal identity

```text
(S^2)_ij=13 S_ij
```

by `S_ij`.  Every common support neighbor contributes the sign product of
the corresponding triangle.  Therefore

```text
balanced common neighbors - unbalanced common neighbors = 13
```

on every one of the `231*68/2=7854` support edges.  Equivalently,

```text
balanced triangles - unbalanced triangles
  = tr(S^3)/6
  = (44*17^3+187*(-4)^3)/6
  = 34034.                                         (10)
```

A balanced support triangle has a ternary Gram matrix of rank one.  This
does **not** imply collinearity: three independent vectors may span a
degenerate three-space with a two-dimensional radical.

Every nonorthogonal projective pair lies on a unique projective line, so it
belongs to at most one selected collinear triple.  Each collinear triple
uses three support edges.  Hence there are at most

```text
7854/3=2618
```

collinear selected triples.  Since the number of balanced triangles is at
least 34,034, at least

```text
34034-2618=31416                                  (11)
```

balanced triples are linearly independent.

Their spans are three-dimensional restricted spaces of Gram rank one and
radical dimension two.  Such a space contains at most nine norm-two
projective points.  Those nine points form an affine plane of order three:
among its `binom(9,3)=84` triples, 12 are affine lines, leaving at most 72
independent triples.  Thus (11) forces at least

```text
ceil(31416/72)=437                                (12)
```

distinct degenerate three-spaces.

This is a higher-order exact restriction, not an endpoint exclusion.

## 4. Characteristic seven polar geometry

Over `F_7`, the factorization has

```text
C=V H V^T,
(v_i,v_i)=1.
```

The independently verified identity

```text
C^(o3)=4(I+C)
```

is nonsingular because `C^2=0`.  Therefore the 231 pure cubes
`v_i^(o3)` are independent.  In particular, the `v_i` are nonzero and
pairwise projectively distinct.  They give 231 distinct norm-one
projective points, each orthogonal to 162 selected companions.

At the cube boundary `r7=11`, the norm-one projective orthogonality graph
has more than two nontrivial pair orbits.  It is not strongly regular, so
Evans's SRG polynomial cannot be applied.  The checker reconstructs its
five-class association algebra exactly.  For two normalized norm-one
representatives, the projective pair type is determined by

```text
equal, or inner-product-square in {0,1,2,4}.
```

The value one is the distinct degenerate-pair orbit; the other nonzero
values give the two nondegenerate nonorthogonal orbits.  Witt extension
reduces every pair to the corresponding canonical representative used by
the recurrence, so the resulting intersection numbers cover every pair.

For square determinant:

```text
v = 141229221,
k_orth = 20178004,
largest nonprincipal orthogonality eigenvalue
  = 2401(1+sqrt(2)).
```

For nonsquare determinant:

```text
v = 141246028,
k_orth = 20175603,
largest nonprincipal orthogonality eigenvalue
  = 4802.
```

The spectral mixing right side is

```text
theta+(k-theta)*231/v > theta >= 4802 > 162
```

in both cases.  Thus both characteristic-seven determinant classes survive
at rank eleven.

Combining only the already verified Wave 36 bounds and parity leaves 561
rank pairs.  The boundary can be stated explicitly:

```text
r3=12  => ternary class square and r7>=12 even,
r7=11  => r3>=13 odd.
```

The characteristic-seven polar calculation adds no further exclusion.

## Reproduction and boundary

The standard-library checker regenerates both finite association schemes,
their exact intersection algebras, the characteristic-seven characteristic
polynomials, all 232 ternary Krawtchouk transforms, the Evans moment
refinement, and the signed-triangle counts.  Its 13-test suite passes.

These are discovery-side candidates until independent verification.  Even
if verified, they imply neither an endpoint matrix nor its nonexistence.
No new rank floor or determinant exclusion is claimed, `n3=4158` survives,
the upper bound remains `4158`, and novelty is `UNKNOWN`.
