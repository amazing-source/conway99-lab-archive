# Wave 26 A2 cubic-tensor obstruction to the explicit abstract survivor

```yaml
role: proof_b
date_utc: 2026-07-23T22:42:45Z
git_commit: 1f22323a2805e3e24f7848d53f2f4813e236fae9
claim_label: DERIVED
scope: >-
  The explicit Wave 24 E8^5 direct-sum A2^2 coordinate-lattice survivor
  cannot also arise from the omitted 231-column projector Gram matrix and
  W=M o M Schur-square origin.
inputs:
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
  verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md: 958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8
  verification/wave24-n3-708-index/survivor-certificate.json: a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2
method: >-
  Convert any hypothetical primitive 231-column realization into a
  norm-four tight frame and its symmetric cubic tensor.  On either
  orthogonal A2 summand, exact root enumeration and the odd scale 21 force
  a pure-cubic squared norm of at least 18.  The Schur-square factorization
  makes this a lower bound for the corresponding compression trace of
  S^(1/2) Q S^(1/2), whereas the explicit Q_AA=A2 block has trace 10.
command: |
  cd attempts/wave26-a2-cubic-obstruction
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave26-a2-cubic-obstruction/exact_check.py: e266fd1189f5f1960093e2991d88b66c220bbbd7bcdc390c04e2d8a8218f3523
  attempts/wave26-a2-cubic-obstruction/test_exact_check.py: aa9d2a653133b981851faa4cc39528a4572703d7ba2d8db040d7068ccc07cd71
  attempts/wave26-a2-cubic-obstruction/exact-results.json: acc3ce7298c164bdee1fe32766bf18437fe79770ee69090b759d3dc774640f33
  attempts/wave26-a2-cubic-obstruction/input-freeze.sha256: c6651c004c5c93a4cefe3183c3c49e4982d1b3d386cf61a02ba0ef9bf1f866e1
  attempts/wave26-a2-cubic-obstruction/failed-routes.md: 3ec793e89df22b36bbdd7808a2c5099b472e7a6a41f5f3c9352051bde931671c
  attempts/wave26-a2-cubic-obstruction/run-report.yaml: 008a154f928d64c5c3fbc672ce0aabc1115a84984e9d6d231757016bdb2b2003
limitations:
  - The result rejects only the full projector/Schur origin of the explicit
    E8^5 direct-sum A2^2 hostile-control package.  Its abstract lattice
    identities remain valid.
  - It does not exclude every h=9 package, any of the other seven necessary
    index values, or n3=708.
  - It supplies no primitive embedding, projector, graph, target resolution,
    formal-kernel proof, or novelty result.
```

## Result

The explicit Wave 24 coordinate-lattice survivor cannot possess the stronger
structure it deliberately omitted:

```text
primitive 231-column projector realization
              plus
          W = M o M
              plus
the published S,Q,G blocks of that survivor.
```

Either one of its two `A2` blocks already gives the exact contradiction

```text
10 = tr(K restricted to A2) >= 18.
```

Here `K` is the orthogonal representative of the Schur endomorphism.  This is
a refutation of a possible extension of one hostile control, not a refutation
of the control in its published abstract scope.  It does not exclude the
index `h=9`, the endpoint `n3=708`, or Conway-99.

## 1. Frozen setup and the 231-column tensor bridge

Suppose, only for contradiction, that the explicit survivor came from an
integral basis matrix

```text
X in Z^(231 x 44),
G = X^T X,
S = 21 G^(-1),
M = X S X^T.
```

Write `x_i` for row `i` of `X` and put

```text
u_i = S^(1/2) x_i.
```

The verified projector conditions give

```text
<u_i,u_j> = M_ij,
||u_i||^2 = 4,
sum_i u_i u_i^T = 21 I_44.
```

The graph-derived endpoint has the exact ordered Gram histogram

| Gram entry | Ordered count |
|---:|---:|
| `4` | 231 |
| `1` | 5,092 |
| `0` | 44,322 |
| `-1` | 1,416 |
| `-2` | 2,300 |

Thus the first four entrywise moments are

```text
sum M_ij   = 0,
sum M_ij^2 = 19,404,
sum M_ij^3 = 60,
sum M_ij^4 = 102,444.
```

Now define the fully symmetric cubic tensor and its flattening

```text
T = sum_i u_i tensor u_i tensor u_i,
Phi(v) = contraction_v(T)
       = sum_i <v,u_i> u_i tensor u_i.
```

For `W=M o M` and `Q=X^T W X`, exact expansion gives

```text
K := Phi^* Phi = S^(1/2) Q S^(1/2),
tr(K)=||T||^2=sum M_ij^3=60.
```

Moreover `M1=0` implies `sum_i u_i=0`, so contracting two tensor indices
gives `4 sum_i u_i=0`; the cubic is harmonic.  None of these identities is
present in an arbitrary coordinate-lattice package.

In integer coordinates, a complete tensor certificate would include

```text
P_abc = sum_i X_ia X_ib X_ic in Z,
sum_(b,c) S_bc P_abc = 0,
Q_ab = sum_(c,e,d,f) P_ace S_cd S_ef P_bdf.
```

## 2. Exact `A2` component count

Focus on one orthogonal `A2` summand, with Gram matrix

```text
A2 = [[ 2,-1],
      [-1, 2]].
```

The complement is even and every full row has norm four.  The `A2` component
therefore has norm zero, two, or four.  But

```text
||(a,b)||^2 = 2(a^2-ab+b^2),
```

and `a^2-ab+b^2` is only zero or one modulo three.  Hence `A2` represents no
vector of norm four.  Its six norm-two roots lie on the three unoriented
lines

```text
alpha=(1,0), beta=(0,1), gamma=(1,1).
```

The tight-frame second moment on this block is

```text
sum_i z_i z_i^T
  = 21 A2^(-1)
  = [[14,7],
     [ 7,14]].
```

If `n_alpha,n_beta,n_gamma` count the three root lines, comparison of the
three matrix entries gives, without a search,

```text
n_alpha=n_beta=n_gamma=7.
```

Let `d_alpha,d_beta,d_gamma` be positive-minus-negative counts on those
lines.  Every `d` is odd.

## 3. The pure cubic has squared norm at least 18

Under the tensor inner product,

```text
<r tensor r tensor r, s tensor s tensor s> = <r,s>^3.
```

The cubic Gram matrix of `alpha,beta,gamma` is exactly

```text
H = [[ 8,-1, 1],
     [-1, 8, 1],
     [ 1, 1, 8]].
```

For `d=(d_alpha,d_beta,d_gamma)`,

```text
d^T H d
 = 6(d_alpha^2+d_beta^2+d_gamma^2)
   +(d_alpha-d_beta)^2
   +(d_alpha+d_gamma)^2
   +(d_beta+d_gamma)^2.
```

All three coordinates are odd, so the right side is at least 18.  This
already proves the needed floor.  The inherited zero-sum identity gives the
sharper form

```text
d=(t,t,-t),  t odd,
||T_A2||^2=18 t^2.
```

The equality cases have `t=+1` or `t=-1`.

## 4. Schur origin turns the floor into a block-trace inequality

Let `A` be the Euclidean two-space belonging to the chosen `A2` summand.
For an orthonormal basis `e_1,e_2` of `A`,

```text
tr(K compressed to A)
 = sum_a ||Phi(e_a)||^2
 >= sum_a ||proj_(A tensor A) Phi(e_a)||^2
 = ||proj_(A tensor A tensor A) T||^2
 >= 18.
```

Equivalently, for any full Schur realization with an orthogonal `A2`
summand of `S`, the corresponding principal block of `Q` must satisfy

```text
tr(A2 Q_AA) >= 18.                         (A2 floor)
```

This statement does not require `Q` itself to split orthogonally.

In the explicit survivor, however,

```text
S_AA=Q_AA=A2,
K_AA is orthogonally similar to A2^2,
tr(K_AA)=tr(A2^2)=1^2+3^2=10.
```

Therefore

```text
10 >= 18,
```

an exact contradiction.  Both displayed `A2` blocks fail separately.

## 5. Hostile controls and boundary

The checker confirms:

- a hypothetical scale 18 gives six occurrences per root line and permits
  balanced signs with pure-cubic norm zero;
- changing `Q_AA` to `2A2` raises the compression trace to 20 and removes
  this particular trace contradiction;
- replacing `A2` by `2I` introduces norm-four component vectors and invalidates
  the three-root-line classification; and
- a two-entry mutation of the endpoint Gram histogram is detected.

The exact standard-library replay is:

```text
cd attempts/wave26-a2-cubic-obstruction
python -B -m unittest -v test_exact_check.py
python -B exact_check.py --output exact-results.json
```

The next obstruction is to apply the integral cubic certificate and block
compression bounds to all lattice packages compatible with the eight
remaining index values.  In particular, the two `A2` floors total only 36,
below the global tensor trace 60, so this argument alone does not exclude a
different `Q` or the endpoint.
