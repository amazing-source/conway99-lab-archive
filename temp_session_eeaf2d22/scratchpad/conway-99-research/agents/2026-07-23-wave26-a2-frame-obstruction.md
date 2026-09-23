# Wave 26 `A2` projector-frame obstruction

```yaml
role: proof_a
date_utc: 2026-07-23T22:40:02Z
git_commit: 1f22323a2805e3e24f7848d53f2f4813e236fae9
claim_label: DERIVED
scope: >-
  An exact necessary obstruction for the required 231-row projector origin:
  the scaled-dual form cannot have an orthogonal A2 summand. In particular,
  the frozen Wave 24 E8^5 orthogonal_sum A2^2 survivor cannot have that
  origin. This does not exclude arbitrary primitive embeddings, all h=9
  lattices, or n3=708.
inputs:
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md: 958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8
  verification/wave24-n3-708-index/survivor-certificate.json: a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2
  verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md: 642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de
method: >-
  Basis-covariant projector-frame identities, exact A2 representation
  arithmetic, the A2 block trace of the tight-frame identity, a
  positive-semidefinite same-root fiber bound, and two explicit hostile
  controls.
command: |-
  cd attempts/wave26-a2-frame-obstruction
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave26-a2-frame-obstruction/exact_check.py: 77c4657696ae214196a1abdc30c2baf6c67263fc7c4ed53cc036e58f33b32aa8
  attempts/wave26-a2-frame-obstruction/test_exact_check.py: 62c3dfeabae4d877ddb556b905869bc6786ab617b604789e39e75ef01c24cb66
  attempts/wave26-a2-frame-obstruction/exact-results.json: bb2b2ffe33d0ca6a0a1f18be8b36c48060d40aef2fc6e0857fd1d23c18e84bb9
  attempts/wave26-a2-frame-obstruction/input-freeze.sha256: 653e294646dc5ee74f3da00ddd9458eb04f5a0660a044bb9dcceef3482a160a5
  attempts/wave26-a2-frame-obstruction/failed-routes.md: 6bfb1ef3e733606006d5986e5adeb8c1da15a1fe6cccbb7cff3e3c500b5a8ad3
limitations:
  - Discovery-agent derivation pending a fresh independent verifier.
  - The obstruction uses the exact projector diagonal, off-diagonal entry
    set, and tight-frame second moment; primitive embedding alone is open.
  - No classification of all even rank-44 determinant-nine forms is proved.
  - The h=9 arithmetic row and n3=708 remain possible under other forms.
  - Target existence and literature novelty remain UNKNOWN.
```

## Result and status wall

Let `S=21G^-1` be the scaled-dual form of the rank-44 projector lattice.
The new necessary condition is:

```text
actual 231-row projector origin
  ==>
S has no orthogonal A2 summand.                     (1)
```

The frozen Wave 24 abstract survivor has

```text
S = E8^5 orthogonal_sum A2^2.
```

It therefore cannot realize the required projector origin. This closes the
specific structural gap left open for that exact matrix certificate.

The conclusion is deliberately narrower than a lattice or endpoint
exclusion:

```text
Wave 24 survivor as abstract coordinate package:       still exact
Wave 24 survivor with required 231-row origin:          REFUTED
Wave 24 survivor under arbitrary primitive embedding:  UNKNOWN
all h=9 scaled-dual forms:                              NOT EXCLUDED
h=9 arithmetic index row:                              NOT EXCLUDED
n3=708:                                                 NOT EXCLUDED
Conway-99 existence and novelty:                        UNKNOWN
```

## 1. Basis-invariant projector-frame package

Let the columns of

```text
Y in Z^(231 x 44)
```

be an integral basis of the actual primitive lattice `L`, and write

```text
H = Y^T Y,
T = 21 H^-1.
```

The orthogonal projector onto the column space of `Y` is

```text
E = Y H^-1 Y^T.
```

Consequently the audited integral projector matrix obeys

```text
M = 21E = Y T Y^T,                              (2)
Y^T Y = H = 21 T^-1.                            (3)
```

These identities are invariant under an integral lattice-basis change.
Suppose `P in GL_44(Z)` gives the desired representative

```text
P^T T P = S.
```

Set

```text
A = P^-T,
Y' = YA,
T' = A^-1 T A^-T = S.
```

Then

```text
Y'T'Y'^T = YTY^T = M,
Y'^T Y' = 21(T')^-1.
```

Thus one may work in the displayed block basis of `S` without changing
`M`. The checker certifies the contragredient transformation with an exact
integral two-dimensional model, including both identities.

Let `x_i` be the rows of `Y'`. Equations (2)--(3), the diagonal of `M`,
and the audited off-diagonal entry set give

```text
<x_i,x_i>_S = 4,
<x_i,x_j>_S in {0,1,-1,-2} for i != j,
sum_i x_i x_i^T = 21 S^-1.                    (4)
```

No automorphism or graph construction is assumed.

## 2. Exact arithmetic of `A2`

Use

```text
A2 = [[2,-1],[-1,2]].
```

For a vector `(a,b)`,

```text
q_A2(a,b)=2(a^2-ab+b^2).                      (5)
```

Its norm-two vectors are exactly the six oriented roots

```text
(-1,-1), (-1,0), (0,-1), (0,1), (1,0), (1,1).
```

It has no norm-four vector. Indeed, norm four would require

```text
a^2-ab+b^2=2.
```

Modulo three the left side equals `(a+b)^2`, which can only be zero or one.
The exhaustive checker is finite without a hidden coordinate cutoff because

```text
q_A2(a,b)-(a^2+b^2)=(a-b)^2.
```

Hence `q_A2<=4` implies `|a|,|b|<=2`; the exact box enumeration is complete.

## 3. The frame identity forces 21 `A2` incidences

Assume that

```text
S = A2 orthogonal_sum R
```

and split each row as `x_i=(a_i,u_i)`. Restricting (4) to the `A2` block
gives

```text
sum_i a_i a_i^T = 21 A2^-1.
```

Multiplication by `A2` followed by trace yields

```text
sum_i q_A2(a_i)
 =21 tr(A2 A2^-1)
 =21*2
 =42.                                           (6)
```

Every full row has norm four. Positivity, the `A2` minimum two, and the
absence of norm-four `A2` vectors imply

```text
q_A2(a_i) in {0,2}.
```

Equation (6) therefore forces exactly

```text
42/2=21
```

rows with a nonzero `A2` root component.

Rows meeting both `A2` blocks are covered. Relative to either selected
summand, the root in the other `A2` block is simply a norm-two vector in
`R`. Such a row contributes two to each block's separate energy equation
and is counted once in each.

## 4. Each oriented-root fiber has size at most three

Fix one oriented root `r` in the selected `A2` block. Every row in its fiber
has the form

```text
x_i = r+u_i,
<u_i,u_i>_R=2.                                (7)
```

For distinct rows in this fiber,

```text
<x_i,x_j>_S=2+<u_i,u_j>_R.
```

The permitted off-diagonal values in (4), together with Cauchy's exact
lower bound `<u_i,u_j>_R>=-2`, force

```text
<u_i,u_j>_R in {-2,-1}.                       (8)
```

If the fiber contained `m` rows, positive definiteness and (8) would give

```text
0 <= ||sum_i u_i||^2
   = 2m+2 sum_(i<j)<u_i,u_j>
   <= 2m-m(m-1)
   = m(3-m).                                  (9)
```

Thus `m<=3`. Six oriented roots support at most

```text
6*3=18
```

incident rows, contradicting the 21 forced by (6). This proves (1).

## 5. Application to the frozen survivor

The checker reads the complete independently verified Wave 24 matrix
certificate. It confirms that its rank-44 `S` matrix contains exact
orthogonal `A2` blocks at zero-based coordinate starts 40 and 42.

Only one such summand is needed for the contradiction. Therefore the exact

```text
E8^5 orthogonal_sum A2^2
```

survivor cannot satisfy the actual 231-row projector package, irrespective
of the second `A2` block.

This does not show that its Gram form lacks an arbitrary primitive embedding
in `Z^231`: the proof uses the diagonal four, the restricted off-diagonal
entries, and the exact second moment in (4).

## 6. Hostile controls

### 6.1 Allowing `+2`

Inside the frozen survivor, fix one oriented root in an `A2` block and pair
it with four norm-two simple roots in four different orthogonal `E8` blocks.
The resulting four rows have exact Gram matrix

```text
[[4,2,2,2],
 [2,4,2,2],
 [2,2,4,2],
 [2,2,2,4]].
```

This is a valid size-four fiber if `+2` is admitted. It fails precisely the
actual off-diagonal entry set. Hence the absence of `+2` is active.

### 6.2 Omitting the frame identity

The checker also constructs 18 norm-four rows satisfying every local entry
condition. For each oriented root in one `A2` block, it selects a distinct
orthogonal complement block and pairs that root with a three-root
zero-sum `A2` triple. Within a fiber the total inner product is one; between
fibers it is one, minus one, or minus two.

Their central second moment is

```text
[[12,6],
 [ 6,12]],
```

whereas the required frame block is

```text
21 A2^-1
 =[[14,7],
   [ 7,14]].
```

Thus the local norm and entry restrictions do not replace the tight-frame
identity. This is a local hostile configuration, not a complete projector.

## 7. Exact replay and boundary

The standard-library-only suite passed:

```text
Ran 15 tests
OK
```

It checks all four frozen hashes, the public base commit, both orthogonal
`A2` blocks, the exact root and norm-four enumeration, basis covariance,
the energy count `42 -> 21`, the fiber cap `3`, total capacity `18`, a row
meeting both `A2` blocks, both hostile controls, all scope walls, and
deterministic LF-only JSON.

The exact next obstruction is no longer whether the displayed Wave 24
survivor has the projector origin: it does not. The remaining task is to
classify or obstruct the other scaled-dual forms in the eight arithmetic
index rows, or construct a complete projector certificate. Until then,
`n3=708`, Conway-99 existence, and novelty remain `UNKNOWN`.
