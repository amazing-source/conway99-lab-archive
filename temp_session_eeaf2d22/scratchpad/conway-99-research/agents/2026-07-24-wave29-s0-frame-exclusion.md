# Wave 29: the Wave 28 rootless control cannot carry the full endpoint frame

```yaml
role: proof_a
date_utc: 2026-07-24T03:13:35Z
git_commit: 74b6f3adcee19ca2b0480258bb7bf51198bd085a
claim_label: DERIVED
scope: >-
  Exact exclusion of the single frozen bare lattice
  S0=K12 orthogonal_sum LAMBDA(F) as the S-form of a full n3=708
  231-row projector/Schur endpoint package. This does not exclude any other
  h=729 lattice, the n3=708 endpoint, or Conway-99.
inputs:
  agents/2026-07-24-wave28-orchestrator-brief.md: 6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e
  agents/2026-07-24-wave28-theta-modular.md: 8783be7e730306637ed863b4d9fbe8f4193ad756e7ec86d697c7407688a5423a
  verification/wave28-theta-modular/audit.md: adc90e404735ca147bc0a5418974d8af0bde71c4ddc2dc62a8c07dee670dbfeb
  verification/wave28-theta-modular/independent-results.json: 24298ae282c7baa252a39ffe96fc37b7c696cb51f14b9ddea2318a59b4335b7f
  verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md: 958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8
  verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md: 642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de
method: >-
  Orthogonal minimum-four support splitting; exact tight-frame block traces;
  Schur-square block inheritance; determinant allocation with the
  even-unimodular rank-12 signature veto; per-row alphabet equations;
  blockwise cubic trace residues; exact integer AM-GM comparisons; and a
  fresh rank-12 application and check of the Wave 24 logarithmic
  characteristic-pseudodeterminant inequality.
command: |-
  cd attempts/wave29-s0-frame-exclusion
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave29-s0-frame-exclusion/exact_check.py: 6a31c4ae0b2c994f4c715ba5118e3b25a052e8b3fc99dea88ea794cb7d9d8dce
  attempts/wave29-s0-frame-exclusion/test_exact_check.py: 26dff5f61d6bc6e3d752f596f5c318baee47358f27552e4a0b7e4c3e8a6a5c4f
  attempts/wave29-s0-frame-exclusion/exact-results.json: 7a85c5321b5e91365c246dff7bae9264cc82494da5c866b1b351511099f6638c
  attempts/wave29-s0-frame-exclusion/input-freeze.sha256: 5ddbd25498cf9f7048705e190f81e203d3d21efcc72d1750de2235e419fda1c4
  attempts/wave29-s0-frame-exclusion/failed-routes.md: bba05cd84c1ac35284c9f8af7d8dd32480f11158ada69195b1bfa61892cad234
limitations:
  - The argument uses the explicit orthogonal K12 plus LAMBDA(F) decomposition and does not classify general h=729 forms.
  - It assumes the full inherited endpoint package only to derive a contradiction; it constructs no X, M, W, Q, B, graph, or endpoint realization.
  - The even-unimodular signature theorem and the already independently checked S0 block data are frozen inputs.
  - Discovery is labeled DERIVED and requires an independent verifier before any promotion.
  - n3=708, Conway-99 existence, and novelty remain UNKNOWN.
```

## Result

The Wave 28 rootless hostile control is hostile only to *bare lattice and
ordinary theta* arguments. It cannot be the `S`-form of the full endpoint
projector/Schur package.

Assume for contradiction that

```text
S0 = K12 orthogonal_sum LAMBDA(F)
```

admits the frozen full endpoint objects. The frame rows split between the two
summands. Exact tight-frame traces force `63` rows in `K12` and `168` in
`LAMBDA(F)`. The matrices `M,W,Q,B` then split into the same two blocks.
The endpoint determinant arithmetic forces

```text
det(Q)=5,
det(Q_K)=5,
det(Q_L)=1,
det(B_K)=729*5=3645,
det(B_L)=1.
```

The row alphabet and the two identities `M 1=0`, `M^2=21M` make each block
trace a positive multiple of six. Blockwise AM-GM then forces

```text
tr(B_K)=24,
tr(B_L)=36.
```

Consequently `C_K=(B_K-I_12)/2` has trace six. Its integral characteristic
pseudodeterminant and the Wave 24 pointwise logarithmic inequality give

```text
det(B_K)<=3^6=729,
```

contradicting `det(B_K)=3645`.

The exact status is:

```text
S0 as a full n3=708 projector/Schur endpoint S-form:  REFUTED by DERIVATION
all other h=729 forms:                                UNKNOWN
n3=708:                                               UNKNOWN
Conway-99:                                            UNKNOWN
novelty:                                              UNKNOWN
```

No automorphism, restricted search, or failed-search inference is used.

## 1. Frozen inputs and the single-lattice scope

The endpoint package is frozen from the Wave 28 orchestrator brief:

```text
X in Z^(231 x 44), full column rank
G=X^T X
S=21G^(-1)
M=XSX^T
W=M o M
Q=X^T W X
B=SQ=I+2C

S,Q,G even integral positive definite
B integral, G-self-adjoint, and G-positive
tr(B)=60
det(B)<=6525
det(B)=det(S)det(Q)
det(Q)>=5 and det(Q)=1 mod 4

M 1=0
diag(M)=4
offdiag(M) in {0,1,-1,-2}.
```

The independently audited Wave 28 object has

| block | rank | determinant | minimum | norm-four vectors |
|---|---:|---:|---:|---:|
| `K12` | 12 | 729 | 4 | 756 |
| `LAMBDA(F)` | 32 | 1 | 4 | 146880 |
| `S0` | 44 | 729 | 4 | 147636 |

Both blocks are even, integral, and positive definite. Those exact facts and
all six frozen file hashes are checked before the companion emits a result.

## 2. Every norm-four row lies in one block

Write a row of `X` as

```text
x_i=(u_i,v_i)
```

in the displayed orthogonal decomposition. Since both summands are even,
positive definite, and have minimum four, every nonzero component has norm at
least four. But the endpoint diagonal says

```text
x_i^T S0 x_i=4.
```

Therefore exactly one of `u_i,v_i` is zero. Every row is supported wholly in
`K12` or wholly in `LAMBDA(F)`. This is a pointwise norm argument, not an
automorphism reduction.

Let the corresponding row sets be `I_K,I_L`. From

```text
G=X^T X=21S0^(-1)
```

and the block support,

```text
X_K^T X_K=21S_K^(-1),
X_L^T X_L=21S_L^(-1).
```

Taking the trace after multiplying by the relevant `S` block gives

```text
4|I_J|
 =sum_(i in I_J) x_i^T S_J x_i
 =tr(S_J X_J^T X_J)
 =21 rank(S_J).
```

Hence

```text
|I_K|=21*12/4=63,
|I_L|=21*32/4=168.
```

These add to `231`, as required.

## 3. The full Schur package splits

After permuting rows so `I_K` comes first,

```text
X = [X_K  0
     0    X_L].
```

Orthogonal row support now gives, directly from the definitions,

```text
M=XSX^T
 =M_K orthogonal_sum M_L,

W=M o M
 =W_K orthogonal_sum W_L,

Q=X^T W X
 =Q_K orthogonal_sum Q_L,

B=SQ
 =B_K orthogonal_sum B_L.                       (1)
```

The principal blocks `Q_K,Q_L` inherit even integrality and positive
definiteness. The blocks of `B` inherit positive-form self-adjointness and
positive eigenvalues.

For this row `det(S0)=729`. The endpoint bound and congruence give

```text
729 det(Q)=det(B)<=6525,
det(Q)>=5,
det(Q)=1 mod 4.
```

Thus `det(Q)<=8`, and the only possible integer is

```text
det(Q)=5.                                       (2)
```

## 4. The rank-12 even-unimodular veto fixes the allocation

By (1), the positive integer block determinants multiply to five. Before
using evenness there are two allocations:

```text
(det(Q_K),det(Q_L))=(1,5) or (5,1).
```

The first would make `Q_K` an even positive-definite unimodular lattice of
rank and signature 12. The even-unimodular signature theorem requires the
signature to be divisible by eight, whereas

```text
12=4 mod 8.
```

Therefore

```text
det(Q_K)=5,
det(Q_L)=1.                                     (3)
```

Using `det(S_K)=729` and `det(S_L)=1`,

```text
det(B_K)=det(S_K)det(Q_K)=3645,
det(B_L)=det(S_L)det(Q_L)=1.                    (4)
```

This veto is active. Without it, the alternative would give
`det(B_K)=729`, exactly the logarithmic cap below rather than a contradiction.

## 5. The row alphabet makes each block trace a multiple of six

The identity `S G=21I` gives

```text
M^2
 =X S X^T X S X^T
 =X S G S X^T
 =21M.                                         (5)
```

For row `i`, let `a_i,b_i,c_i,z_i` count off-diagonal entries equal to
`1,-1,-2,0`, respectively. The row-sum equation and the diagonal part of
(5) are

```text
4+a_i-b_i-2c_i=0,
16+a_i+b_i+4c_i=84.
```

Solving together with `a_i+b_i+c_i+z_i=230` gives

```text
a_i=32-c_i,
b_i=36-3c_i,
z_i=162+3c_i,
0<=c_i<=12.                                    (6)
```

In particular,

```text
sum_j M_ij^3
 =64+a_i-b_i-8c_i
 =60-6c_i.                                     (7)
```

Because (1) splits `M` and `W`, cyclicity of trace gives for either block
`J=K,L`

```text
tr(B_J)
 =tr(S_J X_J^T W_J X_J)
 =tr(M_J W_J)
 =sum_(i,j in I_J) M_ij^3
 =sum_(i in I_J)(60-6c_i).                     (8)
```

Thus both block traces are multiples of six. They are positive multiples
because the eigenvalues of each `B_J` are positive.

## 6. Exact blockwise AM-GM forces traces 24 and 36

Apply AM-GM to the 32 positive eigenvalues of `B_L`. From (4),

```text
tr(B_L)>=32 det(B_L)^(1/32)=32.
```

Together with the multiple-of-six residue,

```text
tr(B_L)>=36.
```

Since the endpoint trace is 60,

```text
tr(B_K)<=24.                                    (9)
```

The positive multiple-of-six possibilities at or below 24 are
`6,12,18,24`. If `tr(B_K)<=18`, AM-GM in rank 12 would imply

```text
det(B_K)
 <=(18/12)^12
 =(3/2)^12
 <3645.
```

The final comparison is exact:

```text
3^12 < 3645*2^12.
```

This contradicts (4), so (9) is sharp:

```text
tr(B_K)=24,
tr(B_L)=36.                                    (10)
```

As a consistency consequence of (7)--(8),

```text
sum_(i in I_K)c_i=626,
sum_(i in I_L)c_i=1674,
sum_i c_i=2300.
```

No contradiction is claimed from those sums themselves.

## 7. The exact statement about `C_K`

Restrict

```text
B=I+2C
```

to the `K12` coordinate block. Then

```text
C_K=(B_K-I_12)/2
```

is integral and `G_K`-self-adjoint. From (10),

```text
tr(C_K)=(24-12)/2=6.                            (11)
```

The needed positivity statement is about `B_K`, not `C_K`:

```text
B_K is G_K-positive,
so every B_K eigenvalue is positive,
so every C_K eigenvalue mu is real and mu>-1/2.
```

`C_K` is **not** asserted positive semidefinite. Negative eigenvalues in
`(-1/2,0)` are explicitly allowed.

Let `r=rank(C_K)`. Integral characteristic coefficients and real
diagonalizability give

```text
char_(C_K)(t)=t^(12-r)p(t),
```

where `p` is monic in `Z[t]` and `p(0)` is a nonzero integer. For the
nonzero eigenvalues `mu_1,...,mu_r`,

```text
|product_i mu_i|=|p(0)|>=1.                    (12)
```

This characteristic pseudodeterminant, not a numerical approximation, is the
integrality input to the final bound.

## 8. Fresh logarithmic proof on the rank-12 block

Put

```text
L=log(3),
c=L-2/3.
```

The exact expansion

```text
log(3)=2 atanh(1/2)
      =2 sum_(k>=0) (1/2)^(2k+1)/(2k+1)
```

with a rational partial sum and geometric tail proves

```text
2/3<L<2,
c>0.                                           (13)
```

For every real `x>-1/2`, `x!=0`,

```text
log(1+2x)<=xL-c log|x|.                         (14)
```

For completeness, on `x>0` subtract the left side from the right and call
the result `F(x)`. Exact formal differentiation gives

```text
x(1+2x)F'(x)=(x-1)(2Lx+c).
```

The second factor is positive, so `F` decreases to `x=1`, increases after
it, and has `F(1)=0`.

On `-1/2<x<0`, put

```text
g(x)=xL-log(1+2x).
```

By (13),

```text
g'(x)=L-2/(1+2x)<L-2<0.
```

Since `g(0)=0`, this gives `g(x)>0` on the negative interval. Also
`-c log|x|>0`, so (14) is strict there. This explicitly covers every allowed
negative eigenvalue of `C_K`.

Apply (14) to the nonzero eigenvalues of `C_K`; zero eigenvalues contribute
the factor one. Equations (11)--(12) give

```text
log det(B_K)
 =sum_i log(1+2mu_i)
 <=6L-c log|product_i mu_i|
 <=6L.
```

Therefore

```text
det(B_K)<=3^6=729.                              (15)
```

But (4) gives `det(B_K)=3645`, and

```text
3645>729.
```

This is the contradiction.

## 9. Exact checker and hostile controls

The companion uses only the Python standard library. Its 18 tests cover:

- all six frozen input hashes and the independently checked `S0` block facts;
- the norm-four support split and exact row counts `63/168`;
- the `M,W,Q,B` block inheritance;
- the unique value `det(Q)=5` and determinant allocation;
- all 13 nonnegative row-alphabet solutions;
- exact integer AM-GM comparisons and the unique trace pair `24/36`;
- the corrected `C_K` spectral statement;
- the integral characteristic pseudodeterminant;
- exact rational bounds on `log(3)` and formal derivative factorization;
- the contradiction `3645>729`;
- fail-closed deletion of every named essential premise;
- explicit controls for nonintegral `C_K`, the missing rank-12 veto, and the
  missing multiple-of-six trace residue; and
- byte-identical deterministic JSON regeneration.

The failed routes and the `C_K` wording correction are retained in
`attempts/wave29-s0-frame-exclusion/failed-routes.md`.

## 10. Scope wall and next boundary

The proof excludes one exact orthogonal decomposition because its norm-four
vectors cannot mix the two summands. It does not extend automatically to:

- a nonorthogonal glue of `K12` and a rank-32 complement;
- another rootless determinant-729 lattice;
- a lattice whose norm-four vectors have nonzero projections into multiple
  subspaces; or
- the full class of general even rank-44 endpoint forms.

Accordingly, this wave removes the strongest Wave 28 bare-lattice hostile
control from full endpoint consideration without changing the global bound.
The general `h=729` row, `n3=708`, Conway-99, and novelty remain `UNKNOWN`.
