# Wave 31 surviving `20+24` endpoint: statement and literature protocol freeze

```yaml
role: literature
date_utc: 2026-07-24T06:16:55Z
git_commit: 5652578111999645a9d5427d0716053de79e0902
claim_label: UNKNOWN
scope: >-
  Pre-search freeze of the exact matrix-level realization problem left by
  the verified Wave 30 decomposable rootless h=729 reduction, followed by a
  bounded primary/authoritative-source audit for that exact signature.
```

This file was frozen before the Wave 31 searches. It does not assert that a
realization exists or does not exist.

## 1. Frozen inputs

```text
fd1f11a2ab5c5dfd2732a4ba1fb8d063dea1ae0e96d417aaf9d45eade4f2281a  agents/2026-07-24-wave30-general-h729.md
523a84e2a490f3626a791fb16f43b77b7631b3f26f2de8dcecc83f5e03f4d2cc  verification/wave30-general-h729/reverification-audit.md
479ed105825ea2b2a0802c34fcc332b8dc1420b27966bec41053702f3212451f  agents/2026-07-24-wave30-h729-construction.md
abba8583533a3ccafe774d7a5b5760a0f76eb23c6427642476a3496c1662fb5c  verification/wave30-h729-construction/audit.md
7b852d5be4ee283e2280d7ebc7e5144ec25666c194fe91cbaaf43a745f1de30c  verification/wave30-literature-audit/audit.md
6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e  agents/2026-07-24-wave28-orchestrator-brief.md
6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3  verification/2026-07-23-wave20-global-schur-audit.md
45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md
958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8  verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md
642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de  verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md
883f48e70336b87955f5c2a115ac8b137169310c6f5ef91fe4581cb1b6c10465  verification/wave26-a2-cubic-obstruction/2026-07-23T231001Z-audit.md
dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d  verification/wave29-s0-frame-exclusion/audit.md
7b4693420eae7e6f13ce0d66c786424c18863a1b1c350da83097f8e982ebe324  agents/2026-07-22-wave7-triangle-side-incidence.md
9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787  verification/2026-07-22-n3-side-incidence-audit.md
31511fd902d2887823174374c8a058c22452bb81950f49a25834e69efcc460ed  agents/2026-07-22-wave8-status-search.md
```

## 2. Exact surviving realization question

Does there exist an even positive-definite integral form

```text
S = A orthogonal_sum U
rank(A)=20,  det(A)=729,  min(A)>=4,
rank(U)=24,  det(U)=1,    min(U)>=4,
```

together with the integral frame and Schur data below?

The symbol `A` is a local name. It is **not** the ADE root lattice `A_20`.
The quantifier ranges over every such `A` and `U`, with every integral
marking. In particular, this freeze does not assume

```text
A = T20
U = a particular displayed Leech Gram matrix.
```

The verified Wave 30 `T20 orthogonal_sum LAMBDA24` construction is a useful
restricted bare candidate only. It does not supply any of the missing
`Q,B,X,M,W` or tensor data, and failure or success for that one candidate
would not by itself classify the exact problem above.

## 3. Required integral frame and projector identities

There must be a full-column-rank matrix

```text
X in Z^(231 x 44)
```

such that

```text
G = X^T X = 21 S^(-1),
S G = 21 I_44,
M = X S X^T.
```

The inherited endpoint conditions are

```text
G even integral positive definite,
M symmetric positive semidefinite,
rank(M)=44,
M^2=21M,
M 1=0,
diag(M)=4,
M_ij in {0,1,-1,-2} for i!=j.
```

Thus the 231 rows have `S`-norm four and form a scale-21 tight frame. The
binary-rank consequence `rank_F2(M)=44` and the congruence
`M o M = M (mod 2)` are inherited consequences, not extra assumptions.

Rootlessness forces each row of `X` to be supported in exactly one summand.
After a row permutation,

```text
X = X_A orthogonal_row_sum X_U,
X_A in Z^(105 x 20),
X_U in Z^(126 x 24),
X_A^T X_A = 21 A^(-1),
X_U^T X_U = 21 U^(-1).
```

Every row in both blocks has squared norm four. Consequently

```text
M = M_A orthogonal_sum M_U,
M_A = X_A A X_A^T,
M_U = X_U U X_U^T,
M_A^2=21M_A,  rank(M_A)=20,  M_A 1=0,
M_U^2=21M_U,  rank(M_U)=24,  M_U 1=0.
```

Both diagonal blocks have diagonal four and the same off-diagonal alphabet.
Every cross-block entry of `M` is zero.

## 4. Required Schur-square, `Q`, and `B` identities

Define, without substituting an independently chosen matrix,

```text
W = M o M,
Q = X^T W X,
B = S Q = I_44 + 2C.
```

The required global properties are

```text
W symmetric positive semidefinite,
Q even integral positive definite,
B integral, G-self-adjoint, and G-positive,
G B = 21 Q,
tr(B)=60,
tr(C)=8,
tr(C^2)>=10,
det(S)=729,
det(Q)=5,
det(B)=3645.
```

The Schur definition is active: an arbitrary even determinant-five `Q` is
not a solution.

Block support makes every displayed object split:

```text
W = W_A orthogonal_sum W_U,
Q = Q_A orthogonal_sum Q_U,
B = B_A orthogonal_sum B_U,
C = C_A orthogonal_sum C_U,
```

where

```text
W_A=M_A o M_A,             W_U=M_U o M_U,
Q_A=X_A^T W_A X_A,         Q_U=X_U^T W_U X_U,
B_A=A Q_A,                 B_U=U Q_U,
det(Q_A)=5,                det(Q_U)=1,
det(B_A)=3645,             det(B_U)=1,
tr(B_A)=36,                tr(B_U)=24,
C_A=(B_A-I_20)/2,          C_U=0,
tr(C_A)=8,                 B_U=I_24,
tr(C_A^2)>=10,             Q_U=U^(-1).
```

Neither the scalar hostile spectrum
`spec(C_A)={2^1,1^6,0^13}` nor equality `tr(C_A^2)=10` is required. That
spectrum is only a non-lattice control retained by Wave 30.

## 5. Exact row and pair arithmetic

For a row `i`, let `a_i,b_i,c_i,z_i` count full-matrix off-diagonal entries
`+1,-1,-2,0`. Then

```text
a_i=32-c_i,
b_i=36-3c_i,
z_i=162+3c_i,
0<=c_i<=12,
sum_j M_ij^3=60-6c_i.
```

The independently verified harmonic-projector consequences further give

```text
c_i>=1 for every row,
at most one row has c_i=1.
```

Equivalently, in the actual-graph notation `q_i=12-c_i`, the projector
package gives `q_i<=11` and at most one `q_i=11`. It does **not** exclude
`q_i=1`, or equivalently `c_i=11`.

The block traces force

```text
sum_(i in A)c_i=1044,
sum_(i in U)c_i=1256.
```

Hence the directed internal alphabets are forced to be

| block | `+1` | `-1` | `-2` | `0` |
|---|---:|---:|---:|---:|
| `A`, 105 rows | 2316 | 648 | 1044 | 6912 |
| `U`, 126 rows | 2776 | 768 | 1256 | 10950 |

In particular the `-1` pairs split as `324+384=708`. This is a consequence
of the endpoint identities, not a graph construction.

## 6. Required tensor/Schur factorization

Put `u_i=S^(1/2)x_i` and

```text
T=sum_i u_i tensor u_i tensor u_i,
Phi(v)=sum_i <v,u_i> (u_i tensor u_i),
K=Phi^*Phi=S^(1/2) Q S^(1/2).
```

The frame has

```text
sum_i u_i u_i^T=21I_44,
sum_i u_i=0,
```

so `T` is harmonic. Block support gives pure tensors

```text
T=T_A+T_U,
Phi=Phi_A orthogonal_sum Phi_U,
Phi_A^*Phi_A=A^(1/2)Q_A A^(1/2),
Phi_U^*Phi_U=I_24.
```

Equivalently, with

```text
P_abc=sum_i X_ia X_ib X_ic in Z,
```

all mixed `A/U` entries of `P` vanish and

```text
sum_(b,c) S_bc P_abc=0,
Q_ab=sum_(c,d,e,f) P_ace S_cd S_ef P_bdf.
```

On the `U` rows, the isometry condition forces

```text
c_i in {9,10,11},
n_9=n_11+4,
n_10=122-2n_11,
0<=n_11<=61.
```

These are 62 aggregate profiles. They are necessary counts, not a
construction of `M_U`.

## 7. Projector-only layer versus actual-graph layer

The verified global graph theorem

```text
q_i=0 or q_i>=2
```

is part of the scope of any actual `srg(99,14,1,2)`. It was independently
verified in Wave 7 and is also prior art in Lou--Murin (2014). Its proof uses
the graph-local perfect matchings and the triangle-free auxiliary graph
`H_i`: if `q_i=1`, the nonisolated 2-regular graph `H_i` would have three
edges and hence be a forbidden triangle.

That proof uses graph structure not encoded by the narrower matrix list
`X,M,W,Q,B`. Therefore:

```text
projector/Schur realization only: c_i=11 remains permitted;
actual-graph endpoint:             c_i=11 is forbidden.
```

Combining the actual-graph gap with the `U`-block tensor profile makes that
block's row distribution unique:

```text
U block:
  4 rows with c=9,  equivalently q=3;
  122 rows with c=10, equivalently q=2;
  0 rows with c=11, equivalently q=1.
```

The corresponding actual-graph `A` block has

```text
sum_(i in A) q_i=216,
q_i in {0,2,3,...,11},
at most one q_i=11.
```

This sharpening is required for a graph lift but cannot be imposed when
searching the narrower projector/Schur matrix problem alone.

## 8. Scope wall

The primary exact frozen question is the matrix-level decomposable rootless
`h=729`, `n3=708` projector/Schur realization above. A second, explicitly
stronger layer asks whether such a realization can satisfy the verified
actual-graph `q`-gap and admit the remaining incidence/adjacency lift.

- It is not restricted to `T20 orthogonal_sum LAMBDA24`.
- It does not assume an automorphism or a row orbit.
- It does not assume the hostile scalar spectrum for `C_A`.
- It does not range over rooted or integrally indecomposable `h=729` forms.
- A matrix-level realization would still require a separate triangle
  incidence and 99-vertex graph lift before it became a Conway graph.
- A finite search no-hit cannot exclude the realization.

The surviving matrix problem, `n3=708`, Conway-99, and novelty are all
`UNKNOWN`.

## 9. Pre-frozen literature search plan

The audit will search primary papers, current preprints, publisher or DOI
records, institutional repositories, and author-maintained mathematical
catalogues. Search snippets are discovery aids only.

The exact lanes are:

1. `231 x 44`, rank `44`, eigenvalue `21`, alphabet
   `{4;0,1,-1,-2}`, row sum zero, and the `105+126` split.
2. A 126-vector norm-four scale-21 tight frame in a rootless even
   unimodular rank-24 lattice, especially the cubic-isometry condition
   `Phi_U^*Phi_U=I_24`.
3. A 105-vector norm-four scale-21 integral frame in rank 20,
   determinant 729, coupled to an even determinant-five `Q_A` and
   `det(B_A)=3645`, `tr(B_A)=36`.
4. Integral eutactic stars, lattice designs, cubature, harmonic cubic
   tensors, Schur/Hadamard-square Gram identities, and frame subsets of the
   Leech lattice under alternate terminology.
5. Strongly regular graph Euclidean representations and Conway-99 records
   containing any exact or equivalent matrix signature, including the
   graph-only `q!=1` sharpening and the forced `U` profile
   `q=3^4,2^122`.
6. The rank-24 rootless even-unimodular classification, used only to identify
   standard prior art and not to add a coordinate ansatz.

Every query string, service, result-window limit, source disposition, and
access failure will be retained. No PDF, raw HTML, XML feed, or raw API
payload will be retained.

The strongest permitted negative conclusion is:

> No exact prior result was found in the sources searched as of 2026-07-24.

That statement cannot establish novelty, priority, global openness, or
nonexistence.
