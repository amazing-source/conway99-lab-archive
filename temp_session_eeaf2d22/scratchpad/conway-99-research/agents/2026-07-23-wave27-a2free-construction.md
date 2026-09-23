# Wave 27 A2-summand-free coupled hostile control

```yaml
role: construction
date_utc: 2026-07-24T00:04:30Z
git_commit: 2ac11809fafee7ab752965ae49a96e922859b5ee
claim_label: CANDIDATE
scope: >-
  An explicit even positive-definite rank-44 determinant-nine form with no
  orthogonal A2 direct summand, extended to complete S,Q,G,B,C matrices
  satisfying the h=9 n3=708 arithmetic/lattice relaxation. No primitive
  embedding, 231-row projector, Schur-square origin, graph, or endpoint
  realization is asserted.
inputs:
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md: 958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8
  verification/wave24-n3-708-index/survivor-certificate.json: a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2
  verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md: 642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de
  verification/wave26-a2-frame-obstruction/2026-07-23T225015Z-audit.md: 5ec6b1924fb9ca2ab9295808178684751b6a90e43315d00cbf232ba8d9fe84a3
  verification/wave26-a2-cubic-obstruction/2026-07-23T231001Z-audit.md: 883f48e70336b87955f5c2a115ac8b137169310c6f5ef91fe4581cb1b6c10465
method: >-
  A direct sum E8^4 orthogonal_sum E6^2, complete exact LDL
  branch-and-bound root enumeration, a root-component obstruction to a
  hidden orthogonal A2 summand, and a rank-one E6-dual projector producing
  integral even Q blocks with the exact endpoint trace.
command: |-
  cd attempts/wave27-a2free-construction
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave27-a2free-construction/exact_check.py: 1bd20f820a5d4467f29860a03a93c4ef3192bb9df4b1c87901080ffa8b793f1e
  attempts/wave27-a2free-construction/test_exact_check.py: 7693d905bd142c34e8552f93c87b253621dfc6e6f94e1beec65e8b688eb8568d
  attempts/wave27-a2free-construction/exact-results.json: 3b1d30b6110d937f1bd4bb9ff570419625063afc5c0915382baa2466d349946d
  attempts/wave27-a2free-construction/input-freeze.sha256: 19beda0a2cfd430bde00d39c9371b9f76df36b7e3ee9ee612b73db21bae43f93
  attempts/wave27-a2free-construction/failed-routes.md: 724e2daf4604cd7fb779b686acc9bdf5b6a1398ed020846bcbebc0968482e120
  attempts/wave27-a2free-construction/run-report.yaml: 249078954019aad3256456470a2a677e4b85f3b7c734bad80c0f29a4effa05d7
limitations:
  - Construction-agent candidate pending a fresh independent verifier.
  - A2-free means no orthogonal A2 direct summand; embedded A2 root
    subsystems do occur.
  - The bounded seed scan is complete only in its named box and rank-one,
    block-diagonal ansatz; it is not a classification.
  - No cross-block Q, primitive embedding, 231-row projector frame,
    Schur-square tensor, or graph was constructed.
  - A separate cubic-tensor scout can impose stronger projector-origin
    restrictions; no such claim is imported here.
  - n3=708, Conway-99 existence, and novelty remain UNKNOWN.
```

## Result and status wall

The Wave 26 obstruction to an orthogonal `A2` summand does not eliminate
the entire `h=9` arithmetic/lattice row.  There is an exact replacement
hostile control:

```text
S = E8^4 orthogonal_sum E6^2,
det(S)=9,
rank(S)=44,
S has no orthogonal A2 direct summand.
```

More strongly, the certificate supplies complete integer matrices
`S,Q,G,B,C` satisfying

```text
G = 21 S^-1,
B = S Q,
G B = 21 Q,
C = (B-I)/2,

det(S)=9,
det(Q)=9,
det(B)=81,
tr(B)=60,
B=I mod 2,
tr(C)=8,
tr(C^2)=32.
```

Thus the abstract coupled arithmetic/lattice relaxation still has an
`h=9` survivor after the specific `E8^5 orthogonal_sum A2^2` survivor loses
its projector origin.

The status boundary is strict:

```text
explicit A2-summand-free coupled lattice package:  CANDIDATE
all h=9 forms classified:                           NO
231-row projector or Schur origin:                  NOT ESTABLISHED
n3=708 excluded:                                    NO
Conway-99 existence and novelty:                    UNKNOWN
```

## 1. Frozen coordinate forms

The certificate freezes the same simple-root `E8` Gram matrix used by the
Wave 24 checker.  For `E6`, it uses diagonal two and the five edges

```text
(0,1), (1,2), (2,3), (3,4), (2,5).
```

Exact LDL pivots are positive.  The determinants and parities are

```text
det(E8)=1,  E8 even positive definite;
det(E6)=3,  E6 even positive definite.
```

Consequently

```text
S=E8^4 orthogonal_sum E6^2
```

is even positive definite of rank 44 and determinant nine.  Its
discriminant group is certified by determinant and rank modulo three:

```text
rank_F3(S)=42,
disc(S) = (Z/3Z)^2.
```

No target automorphism is assumed.  Choosing this direct-sum form is a
construction ansatz, not a necessary decomposition for a target.

## 2. Complete root enumeration and the hidden-summand test

The checker performs exact reverse-`LDL` branch-and-bound enumeration.
For a positive-definite Gram matrix `A=L D L^T`, it uses

```text
x^T A x
 = sum_i D_i (x_i + sum_(j>i) L[j,i] x_j)^2.
```

Once the higher coordinates are fixed, exact rational comparison gives a
finite complete interval for the next integer coordinate.  No
floating-point cutoff or assumed coordinate box is used.

The unique blocks give:

| block | exact minimum | norm-two vectors | nonorthogonality components |
|---|---:|---:|---:|
| `E8` | 2 | 240 | one of size 240 |
| `E6` | 2 | 72 | one of size 72 |

Since the full form is an orthogonal sum of even blocks, every norm-two
vector lies in exactly one block.  Therefore the complete root system of
`S` has

```text
4*240 + 2*72 = 1104
```

roots and component sizes

```text
240,240,240,240,72,72.                         (1)
```

Now suppose, for contradiction, that

```text
S is integrally isometric to A2 orthogonal_sum R.
```

The complement `R` is even because it is a sublattice of the even lattice
`S`.  A norm-two vector decomposes into nonnegative even norms in the two
summands, so it lies wholly in `A2` or wholly in `R`.  The six roots of the
`A2` summand must therefore form a complete connected component of the
root nonorthogonality graph.  Equation (1) has no component of size six.
This proves that no orthogonal `A2` direct summand is hidden by a basis
change.

This does **not** say that `S` contains no `A2` root subsystem.  The first
two simple roots in the displayed `E6` block have Gram matrix

```text
[[ 2,-1],
 [-1, 2]].
```

The certificate retains this positive hostile control so “embedded
subsystem” cannot be silently confused with “orthogonal direct summand.”

## 3. The rank-one `E6` extension

Let

```text
R = E6,
H = R^-1,
v = (1,0,-1,0,0,1)^T.
```

Exact arithmetic gives

```text
d = v^T H v = 4/3.
```

Define the `H`-orthogonal rank-one projector and its endpoint endomorphism

```text
P = v(v^T H)/d,
B6 = I+8P.
```

Then `P^2=P`, so

```text
spec(B6)=9,1,1,1,1,1,
tr(B6)=14,
det(B6)=9.
```

Set

```text
Q6 = H B6
   = H + 8(Hv)(Hv)^T/d.
```

The symmetry is built into the second expression.  Exact cancellation
makes both `B6` and `Q6` integral:

```text
B6 =
[[ 3,-2,-6,-4,-2, 0],
 [ 0, 1, 0, 0, 0, 0],
 [-2, 2, 7, 4, 2, 0],
 [ 0, 0, 0, 1, 0, 0],
 [ 0, 0, 0, 0, 1, 0],
 [ 2,-2,-6,-4,-2, 1]],

Q6 =
[[2,1, 0,0,0,1],
 [1,4, 6,4,2,2],
 [0,6,12,8,4,3],
 [0,4, 8,6,3,2],
 [0,2, 4,3,2,1],
 [1,2, 3,2,1,2]].
```

The checker proves

```text
Q6 even positive definite,
det(Q6)=3,
B6=I mod 2.
```

Notice that `B6` is not symmetric in these integral coordinates.  The
required property is self-adjointness for the `G` form, not accidental
Euclidean symmetry.

## 4. Complete coupled matrices

Let

```text
Q = (E8^-1)^4 orthogonal_sum Q6^2,
G = 21 S^-1,
B = S Q,
C = (B-I)/2.
```

All five complete `44 x 44` integer matrices appear in
`exact-results.json`; the certificate also records a canonical JSON hash
for each matrix.

The four `E8` blocks contribute `I_32` to `B`.  Each `E6` block contributes
one eigenvalue nine and five eigenvalues one.  Hence

```text
spec(B)=9^2,1^42,
det(B)=81,
tr(B)=60,
tr(B^2)=204.
```

Moreover,

```text
C^2=4C,
rank(C)=2,
tr(C)=8,
tr(C^2)=32.
```

The exact global matrix identities are

```text
S G = 21 I,
B = S Q,
G B = 21 Q,
B^T G = G B.
```

The last identity is the correct self-adjointness statement.

## 5. Minimum, roots, and discriminant data

The same complete block enumerator gives

| full form | determinant | minimum | roots | discriminant group |
|---|---:|---:|---:|---|
| `S` | `9` | 2 | 1104 | `(Z/3Z)^2` |
| `Q` | `9` | 2 | 1104 | `(Z/3Z)^2` |
| `G` | `21^44/9` | 28 | 0 | `(Z/7Z)^2 + (Z/21Z)^42` |

For `G`, the unique blocks have exact minima

```text
min(21 E8^-1)=42,
min(21 E6^-1)=28.
```

Thus `G` is even positive definite with minimum well above the inherited
minimum-four floor.

The Smith data are recovered without a black-box normal-form solver.  For
`S` and `Q`, determinant valuation two at three and rank 42 modulo three
force exactly two invariant factors equal to three.  For `G`,

```text
v3(det G)=42, rank_F3(G)=2,
v7(det G)=44, rank_F7(G)=0.
```

Every relevant prime occurs to the first power in exactly the indicated
number of invariant factors, and Smith divisibility ordering gives two
factors `7` followed by 42 factors `21`.

## 6. Search restrictions and hostile controls

The positive construction arose from a finite exact seed scan, but only
inside the following ansatz:

```text
v in {-1,0,1}^6 modulo v ~ -v,
P=v(v^T E6^-1)/(v^T E6^-1 v),
B6=I+8P,
Q6=E6^-1 B6.
```

There are exactly 27 sign-canonical successful seeds in this box, all
listed in the JSON certificate.  This count is complete only within that
box and formula.  It says nothing about seeds outside the box, cross-block
`Q`, or other determinant-nine forms.

Two active hostile controls are retained:

- using `Q=S` gives `tr(S^2)=252`, not 60; and
- reusing the chosen vector in the wrong `E6` coordinate convention gives
  dual norm `10/3`, not `4/3`, and loses the displayed integral package.

No cross-block `Q` was needed or searched.  No absence conclusion follows
from that restriction.

## 7. Exact replay and boundary

The standard-library suite passed:

```text
Ran 15 tests
OK
```

It checks all frozen hashes; complete matrix dimensions and canonical
hashes; the `E6` convention; projection identities; all coupled identities;
determinants, parity, and exact LDL definiteness; endpoint traces; complete
minimum and root enumerations; the hidden-`A2` direct-summand lemma;
discriminant groups; bounded-search restrictions; hostile mutations; scope
walls; and deterministic LF-only JSON.

The result is adversarial evidence against the naive inference

```text
every h=9 form has an orthogonal A2 summand.
```

It is not evidence that the new package has the omitted projector or
Schur-square structure.  A separate cubic-tensor analysis may obstruct
that extension without changing this abstract hostile control.  Until a
fresh verifier checks this package and a genuine structural bridge is
supplied, `n3=708` and Conway-99 remain `UNKNOWN`.
