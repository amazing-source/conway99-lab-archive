# Wave 27: an A2-free `h=9` coupled lattice survivor

```yaml
role: proof_a
date_utc: 2026-07-24T00:00:14Z
git_commit: 2ac11809fafee7ab752965ae49a96e922859b5ee
claim_label: DERIVED
scope: >-
  Exact A2-free survivor of the n3=708 h=9 coordinate-lattice and coupled
  S,Q,G,B endomorphism identities. No primitive Z^231 embedding, projector
  Gram, Schur-square origin, graph, endpoint exclusion, or classification of
  every h=9 form is claimed.
inputs:
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md: 958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8
  verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md: 642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de
  verification/wave26-a2-frame-obstruction/2026-07-23T225015Z-audit.md: 5ec6b1924fb9ca2ab9295808178684751b6a90e43315d00cbf232ba8d9fe84a3
  verification/wave26-a2-cubic-obstruction/2026-07-23T231001Z-audit.md: 883f48e70336b87955f5c2a115ac8b137169310c6f5ef91fe4581cb1b6c10465
method: >-
  Construct E8^4 orthogonal-sum E6^2, solve the unrestricted local E6
  trace/parity problem exactly, couple two trace-14 E6 blocks to four
  unimodular E8 blocks, and verify all matrices with exact Fraction
  arithmetic. Compare root components and discriminant quadratic modules
  with the old E8^5 orthogonal-sum A2^2 hostile control.
command: |-
  cd attempts/wave27-h9-classification
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
limitations:
  - Positive-definite rank-44 determinant-nine lattices are not classified.
  - Genus masses and class representatives are not enumerated.
  - The 231-row projector and Schur-square tensor constraints are absent.
  - The target and novelty remain UNKNOWN.
```

## Result

The determinant-nine, scaled-dual, and coupled endomorphism premises do
**not** force an orthogonal `A2` summand.  There is an exact alternative
package

```text
S = E8^4 orthogonal_sum E6^2
Q = (E8^(-1))^4 orthogonal_sum Q6^2
G = 21 S^(-1)
B = S Q
C = (B-I)/2
```

with

```text
rank(S)=44,
det(S)=det(Q)=9,
det(B)=81,
tr(B)=60,
tr(C)=8,
tr(C^2)=32,
rank(C)=2,
S G=21I,
S Q=B,
G B=21Q,
B=I mod 2.
```

The forms `S`, `Q`, and `G` are even, integral, and positive definite.
Their relevant minima are

```text
min(S)=2,
min(E8^(-1))=2,
min(E6^(-1))=4/3,
min(G)=21*(4/3)=28.
```

Thus this package passes the same abstract coordinate-lattice gates as the
old `E8^5 orthogonal_sum A2^2` package while containing no orthogonal `A2`
summand.  It remains only an arithmetic hostile control: no matrix `X` with
231 rows, projector Gram `M`, Schur square `W=M o M`, or graph is supplied.

## 1. Frozen inherited premises

The cited Wave 21, 24, and 25 audits supply the conditional endpoint
coordinate identities

```text
S=21G^(-1) even integral positive definite,
Q=G B/21 even integral positive definite,
B=S Q=I+2C,
tr(B)=60,
det(S)=h,
det(B)=h det(Q).
```

For `h=9`, the inherited modular bookkeeping is the necessary row
`rank_F3(M)=42`, `rank_F7(M)=44`.  The present construction verifies
`rank_F3(S)=42`; it does not construct `M` and therefore does not promote
the modular rank bookkeeping to a realized projector.

The cited Wave 26 audits exclude a full projector/Schur realization when
`S` has an orthogonal `A2` summand.  They do not say that every `h=9` form
has such a summand.  The construction below shows that the latter assertion
would be false at the arithmetic level.

## 2. Determinant-nine lattice without an `A2` component

Use the standard simply-laced Cartan forms

```text
E8  (rank 8, determinant 1),
E6  (rank 6, determinant 3).
```

Exact elimination gives

```text
rank(E8^4 + E6^2)=4*8+2*6=44,
det(E8^4 + E6^2)=1^4*3^2=9.
```

The checker closes the simple-root orbits under exact simple reflections
and obtains

```text
|Roots(A2)|=6, |Roots(E6)|=72, |Roots(E8)|=240.
```

Each displayed Dynkin diagram is connected and its simple roots span the
corresponding block.  In an orthogonal splitting of an even lattice, a
norm-two vector lies in exactly one summand: two nonzero components would
already contribute norm at least four.  Hence an orthogonal splitting
partitions the root components.  The root components of this `S` are

```text
E8, E8, E8, E8, E6, E6,
```

so none is `A2`.  Therefore `S` has no orthogonal `A2` summand.

This argument does not assert that `S` has no `A2` root subsystem.  It
asserts the stronger relevant structural distinction that `A2` is not an
orthogonal direct summand.

## 3. The discriminant form does not recover `A2`

Exact Smith-rank data give

```text
A_S = S*/S = (Z/3Z)^2.
```

For a generator of the `E6` discriminant group the norm is `4/3`; for a
generator of the `A2` discriminant group it is `2/3`, modulo `2Z`.
Nevertheless the two doubled discriminant forms are isometric.  Indeed

```text
P = [[1, 1],
     [1,-1]]
```

has determinant one modulo three and satisfies, before reduction,

```text
(2/3) ||P x||^2 = (4/3) ||x||^2.
```

Consequently `E6^2` and `A2^2` have isometric order-nine discriminant
quadratic modules.  Determinant, exponent, signature, and this discriminant
module therefore cannot distinguish the two hostile controls or force an
`A2` component.

Their root counts are different:

```text
E8^4 + E6^2:  4*240+2*72 = 1104,
E8^5 + A2^2:  5*240+2*6  = 1212.
```

Thus their theta series already differ in the norm-two coefficient.
Discriminant-form data alone do not fix the needed theta coefficient.

## 4. Exact scaled-dual minimum

`E8` is even unimodular.  Its displayed inverse Gram matrix is integral,
even, positive definite, and has a diagonal entry two, so its minimum is
exactly two.

Put `H=E6^(-1)`.  Exact inversion gives `3H` integral and even.  The checker
also proves `4I-E6` positive definite.  Hence every vector with

```text
x^T H x < 4/3
```

would have Euclidean square below `16/3`, so it lies in the finite set of
integer vectors with Euclidean square at most five.  Exhausting that set
gives minimum `4/3`, attained by a displayed basis vector.  Therefore

```text
21H integral and even,
min(21H)=28.
```

The full `G=21S^(-1)` is consequently even integral positive definite with
minimum 28, well above the inherited minimum-four lattice gate.

## 5. Complete unrestricted local `E6` trace problem

Let `S6=E6`.  Among all even integral positive-definite symmetric `Q6`
satisfying

```text
B6=S6 Q6=I mod 2,
```

the exact minimum is

```text
min tr(S6 Q6)=14.                           (E6 trace floor)
```

This is not a root-basis-restricted statement.

### 5.1 Lower bound

Write `T=tr(B6)` and `B6=I+2C6`.  Since `det(S6)=3`, while an even
rank-six odd-determinant form has determinant `3 mod 4`, one has

```text
det(B6)=3 det(Q6)=1 mod 4.
```

The determinant expansion of `I+2C6` modulo four makes `tr(C6)` even.
Therefore

```text
T=6+2tr(C6)=2 mod 4.
```

Moreover `det(Q6)>=3`, so `det(B6)>=9`.  AM-GM on the six positive
eigenvalues gives

```text
T<=8
  ==> det(B6)<=(8/6)^6=4096/729<9,
```

which is impossible.  The first remaining congruence value is `T=10`.

Suppose `T=10`.  Then `tr(C6)=2`.  The integral characteristic
pseudodeterminant and Cauchy/AM-GM argument give `tr(C6^2)>=2`.  Equality
forces exactly two nonzero eigenvalues, both one, so `C6` is an integral
self-adjoint idempotent of rank two.  Its integral image/kernel split makes
the rank-four kernel blocks of `S6` and `Q6` mutual even integral inverses.
That would be an even positive-definite unimodular form of rank four,
contradicting the inherited even-unimodular signature theorem.  Hence

```text
tr(C6^2)>=4,
tr(B6^2)=6+4tr(C6)+4tr(C6^2)>=30.
```

For completeness, maximize the product of six positive variables with
sum ten and square sum at least 30.  A positive maximum lies on square sum
30; otherwise stationarity under the sum alone would give the infeasible
equal point.  Lagrange stationarity gives at most two coordinate values.
If the larger value has multiplicity `k`, positivity leaves `k=1,2,3`.
The exact three products are

```text
k=1: 5,
k=2: (4625-1000 sqrt(10))/729 < 5,
k=3: 125/729 < 5.
```

Thus `det(B6)<=5`, contradicting `det(B6)>=9`.  Trace ten is impossible,
and the congruence proves `T>=14`.

### 5.2 Equality witness

In the displayed `E6` basis take

```text
v=(-1,0,1,0,0,-1),
H=E6^(-1),
v^T H v=4/3,
P=v(v^T H)/(v^T H v),
B6=I+8P,
Q6=H B6.
```

Exact arithmetic gives

```text
B6 =
[[ 3,-2,-6,-4,-2, 0],
 [ 0, 1, 0, 0, 0, 0],
 [-2, 2, 7, 4, 2, 0],
 [ 0, 0, 0, 1, 0, 0],
 [ 0, 0, 0, 0, 1, 0],
 [ 2,-2,-6,-4,-2, 1]]

Q6 =
[[2,1, 0,0,0,1],
 [1,4, 6,4,2,2],
 [0,6,12,8,4,3],
 [0,4, 8,6,3,2],
 [0,2, 4,3,2,1],
 [1,2, 3,2,1,2]].
```

The matrix `P` is an `H`-self-adjoint rank-one idempotent.  Therefore
`B6` has spectrum `9,1,1,1,1,1`, and `Q6=HB6` is symmetric positive
definite.  Entrywise verification gives

```text
Q6 even integral,
B6 integral and B6=I mod 2,
det(Q6)=3,
det(B6)=9,
tr(B6)=14.
```

This attains the unrestricted floor.

## 6. Coupling to rank 44

On each `E8` block take `Q8=E8^(-1)`, so `E8 Q8=I8` and the trace
contribution is eight.  On each `E6` block use the equality witness above.
Then

```text
tr(B)=4*8+2*14=60,
det(Q)=1^4*3^2=9,
det(B)=1^4*9^2=81.
```

Each local `C6=(B6-I)/2=4P` has trace four, square trace 16, and rank one.
Two copies yield the full endpoint values

```text
tr(C)=8,
tr(C^2)=32,
rank(C)=2.
```

All block matrices and identities are regenerated from the Cartan matrices;
the JSON records canonical hashes for the six full 44-by-44 matrices.

## 7. What is and is not classified

The exact result is a counterexample to two possible reductions:

```text
det(S)=9 plus scaled-dual conditions  does not force A2;
adding the abstract coupled S,Q,G,B identities still does not force A2.
```

It is not a classification of all determinant-nine forms.  In particular,
no genus mass, neighbor graph, or complete representative list was
computed.  The sharp finite next problem is:

1. enumerate, up to integral isometry, every even positive-definite
   rank-44 `S` with determinant nine and `21S^(-1)` even integral;
2. for each `S`, enumerate the finite set of even positive-definite
   integral `Q` in the trace slice
   `SQ=I mod 2`, `tr(SQ)=60`, `det(SQ)<=6525`; and
3. impose the missing 231-row second- and third-moment/projector
   certificates on those arithmetic pairs.

The new `E6` pair evades the Wave 26 orthogonal-`A2` obstruction but does
not evade or satisfy the full tensor constraints, which remain a separate
open verification problem.

Final scoped status:

```text
A2 forced by determinant/minimum/scaled dual: REFUTED
A2 forced by abstract S,Q,G,B identities: REFUTED
unrestricted local E6 trace minimum: DERIVED as 14
all h=9 forms classified: NO
projector/Schur/graph origin: NOT CONSTRUCTED
n3=708: NOT EXCLUDED
Conway-99 existence: UNKNOWN
novelty: UNKNOWN
```
