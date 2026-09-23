# Wave 31: a target-incidence commutator excludes every rootless integral split

```yaml
role: proof_a
date_utc: 2026-07-24T06:38:48Z
git_commit: 5652578111999645a9d5427d0716053de79e0902
claim_label: DERIVED
scope: >-
  Conditional exclusion, under the actual vertex-triangle incidence
  semantics of a putative srg(99,14,1,2), of every nontrivial rootless
  integral orthogonal decomposition of the rank-44 scaled-dual endpoint
  S-form. This eliminates the Wave 30 rank-20 determinant-729 plus rank-24
  unimodular decomposable boundary. Rooted and integrally indecomposable
  endpoint forms, n3=708, Conway-99, and novelty remain UNKNOWN.
inputs:
  agents/2026-07-23-wave20-global-schur.md: 64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/2026-07-22-n3-side-incidence-audit.md: 9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787
  agents/2026-07-24-wave30-general-h729.md: fd1f11a2ab5c5dfd2732a4ba1fb8d063dea1ae0e96d417aaf9d45eade4f2281a
  verification/wave30-general-h729/reverification-audit.md: 523a84e2a490f3626a791fb16f43b77b7631b3f26f2de8dcecc83f5e03f4d2cc
method: >-
  Turn a coordinate projector block into a diagonal sign involution;
  transport it through the vertex-triangle incidence map to the adjacency
  minus-four eigenspace; commute the resulting symmetric operator with the
  exact spectral projector; use unique edge-triangle incidence to force
  constant signed triangle degree; then contradict the norm-four block
  trace identity by exact divisibility.
command: |-
  cd attempts/wave31-survivor-proof
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave31-survivor-proof/exact_check.py: 7613ecc5680bbb1539690e1308775014a2e32957e51036cf9de68ce2ae699956
  attempts/wave31-survivor-proof/test_exact_check.py: 24e81f7136bcfa188d5cea93fce36600ba198cbdbf0561ae4c0f4090b92d313b
  attempts/wave31-survivor-proof/exact-results.json: e5155e67a59168767639273ee70fc6d63e81b104e9b415e228ca09a0f9317587
  attempts/wave31-survivor-proof/input-freeze.sha256: 28f3b2890db2629686dae23484443582fc883914aeb85e2edc87e0149d479174
  attempts/wave31-survivor-proof/failed-routes.md: beaec0f3f988c2ed961e628d5d1c6ca73f1439b40f6e9b67536415f63d942c4f
limitations:
  - This is a discovery-agent derivation requiring a fresh independent verifier.
  - The vertex-triangle incidence transport uses actual target-graph semantics, not only a free-standing abstract X,M,S,Q,B package.
  - Minimum at least four and an integral orthogonal decomposition are essential.
  - Rooted and integrally indecomposable S-forms remain untreated.
  - No graph, frame, Schur package, or endpoint object is constructed.
  - n3=708, Conway-99 existence, and novelty remain UNKNOWN.
```

## Result

Let `S` be the rank-44 scaled-dual form attached to the projector lattice of
a putative target graph.  If

```text
min(S)>=4
```

and `S` has a nontrivial integral orthogonal decomposition, then the
norm-four frame rows split into coordinate blocks.  The corresponding
zero-eigenspace projector of the triangle-intersection graph is therefore
coordinate-block diagonal.

The target vertex-triangle incidence map turns any such coordinate block
into a signed operator on the 99 graph vertices.  Exact commutation with the
adjacency `-4` projector forces the block to contain a multiple of 33 of the
231 graph triangles.  On the other hand, a rank-`r` rootless integral block
contains exactly

```text
21r/4
```

frame rows.  Thus `r=4k` and its row count is `21k`.  For a proper block,
`1<=k<=10`; divisibility by 33 would force `11|k`, which is impossible.

Consequently:

```text
nontrivial rootless integral orthogonal endpoint split: DERIVED IMPOSSIBLE
Wave 30 rank-20 plus rank-24 decomposable boundary:     DERIVED IMPOSSIBLE
rooted endpoint forms:                                  UNKNOWN
rootless indecomposable endpoint forms:                 UNKNOWN
n3=708:                                                  UNKNOWN
Conway-99 and novelty:                                   UNKNOWN
```

The proof uses neither `h=729` nor the Schur determinant census.  It
therefore supersedes the whole Wave 30 rootless decomposable boundary, not
only its last `20+24` type.  It does not exclude an endpoint form outside
that boundary.

## 1. Frozen target incidence and projector

Let `A` be the `99 x 99` adjacency matrix, `N` the `99 x 231`
vertex-triangle incidence matrix, and `Gamma` the triangle-intersection
adjacency matrix.  The audited target identities are

```text
N N^T=7I_99+A,
N^T N=3I_231+Gamma.
```

The target spectra are

```text
spec(A)={14^1,3^54,(-4)^44},
spec(Gamma)={18^1,7^54,0^44,(-3)^132}.
```

Let `E` be the zero-eigenspace projector of `Gamma`.  The integral endpoint
projector is

```text
M=21E.
```

If `u` lies in `im(E)`, then

```text
||Nu||^2
 =u^T N^T N u
 =u^T(3I+Gamma)u
 =3||u||^2.                                      (1)
```

Thus `N` is injective on `im(E)`.  Moreover,

```text
(7I+A)Nu
 =N N^T N u
 =N(3I+Gamma)u
 =3Nu,
```

so

```text
A(Nu)=-4Nu.                                     (2)
```

Both spaces in (2) have dimension 44.  Hence `N` maps `im(E)` onto the
adjacency `-4` eigenspace

```text
V=ker(A+4I).
```

The exact orthogonal projector onto `V` is

```text
P_-4=(27I-9A+J)/63.                              (3)
```

Indeed, (3) has eigenvalues zero, zero, and one on the adjacency
eigenspaces `14`, `3`, and `-4`, respectively.

## 2. A rootless integral split gives a commuting sign involution

Suppose, after a unimodular integral change of lattice basis,

```text
S=S_1 orthogonal_sum ... orthogonal_sum S_m,
qquad m>=2.
```

Every row `x_i` of the integral frame satisfies

```text
x_i^T S x_i=4.
```

Each nonzero block component has even norm at least four.  Therefore every
row is supported on exactly one lattice block.  After permuting the 231
triangle rows, `X` and

```text
M=XSX^T=21E
```

are coordinate-block diagonal.

Choose one nonempty proper row block `I`.  Define the diagonal sign matrix

```text
D_ii=+1 for i in I,
D_ii=-1 for i outside I.
```

Coordinate block diagonality gives

```text
DE=ED.                                           (4)
```

Thus `D` preserves `im(E)`.

## 3. Incidence transport and exact commutation

Put

```text
K=N D N^T.                                       (5)
```

The matrix `K` is symmetric.  For `u in im(E)`, equations (4) and
`N^T N=3I+Gamma` give

```text
K(Nu)
 =N D N^T N u
 =N D(3I+Gamma)u
 =3N(Du)
 in V.                                           (6)
```

So `K` preserves `V`.  Symmetry makes `V^perp` invariant as well; hence
`K` commutes with the orthogonal projector (3):

```text
K P_-4=P_-4 K.
```

Canceling the identity term in (3) yields

```text
9(KA-AK)=KJ-JK.                                  (7)
```

Let `s in {+1,-1}^231` be the diagonal of `D`, and define the signed
triangle degree

```text
d=Ns,
d_x=sum_(T containing x) s_T.                    (8)
```

Every graph triangle contains three vertices, so `N^T 1=3 1`.  From (5),

```text
K1=3d.
```

Because `K` is symmetric,

```text
KJ-JK=3(d 1^T-1 d^T).
```

Equation (7) therefore becomes

```text
3(KA-AK)=d 1^T-1 d^T.                            (9)
```

Every factor and coefficient in (9) is exact.

## 4. The unique graph triangle on an edge forces `d` constant

The entries of `K` have a direct graph interpretation.  On the diagonal,

```text
K_xx=d_x.
```

If `x` and `y` are adjacent, their edge lies in its unique graph triangle
`T`, and

```text
K_xy=s_T.
```

For a nonedge the off-diagonal entry is zero.  Write

```text
K=diag(d)+Z,
```

where `Z` is this signed adjacency matrix.

Fix adjacent vertices `x,y`.  Because the target has `lambda=1`, their
unique common neighbor `z` completes the same graph triangle `T=xyz`.
Consequently,

```text
(ZA-AZ)_xy
 =Z_xz-Z_zy
 =s_T-s_T
 =0.                                             (10)
```

The diagonal part gives

```text
(diag(d)A-A diag(d))_xy=d_x-d_y.
```

Taking the `(x,y)` entry of (9) and using (10),

```text
3(d_x-d_y)=d_x-d_y,
```

so

```text
d_x=d_y                                          (11)
```

on every graph edge.  The target graph is connected: adjacent vertices are
joined directly, and every nonadjacent pair has `mu=2` common neighbors.
Thus (11) makes `d` constant on all 99 vertices.

## 5. Divisibility contradiction

Let `b=|I|`.  Double-counting signed vertex-triangle incidences gives

```text
99d
 =sum_x sum_(T containing x) s_T
 =3 sum_T s_T
 =3(2b-231).
```

Therefore

```text
33d=2b-231.                                      (12)
```

Since `231=7*33` and `2` is invertible modulo 33,

```text
33 divides b.                                    (13)
```

Equivalently, the only possible sizes from the seven signed triangles at
each vertex are

```text
b in {0,33,66,99,132,165,198,231}.
```

Now let the selected integral lattice block have rank `r`.  Its frame rows
still satisfy

```text
X_I^T X_I=21S_I^(-1).
```

Multiplying by `S_I` and taking the trace gives

```text
4b=21r.                                         (14)
```

Thus `r=4k` and `b=21k`.  For a nonempty proper block of a rank-44
decomposition,

```text
1<=k<=10.
```

But (13) and (14) give

```text
33 divides 21k,
11 divides k,
```

which is impossible in that range.  This proves the claimed exclusion.

For the exact Wave 30 boundary,

```text
rank 20 block: 105 rows = 6 mod 33,
rank 24 block: 126 rows =27 mod 33.
```

Both sides fail independently.

## 6. Superseded rank-24 tensor refinement

The initial Wave 31 route sharpened, but did not exclude, the Wave 30
rank-24 block.  With

```text
W_U=M_U o M_U,
B_U=I_24,
```

the Euclidean Schur operator is `K_U=I_24`, hence

```text
A4_U=M_U W_U M_U=M_U.                            (15)
```

Every `A4_U` diagonal is four.  If `q_i=12-c_i`, the cubic row identity and
tensor Cauchy give

```text
[6(q_i-2)]^2<=4*16,
q_i in {1,2,3}.
```

The separately verified graph-local theorem excludes `q_i=1`.  Finally,

```text
tr(B_U)=sum_(i in U) 6(q_i-2)=24
```

forces

```text
122 rows with q=2 (c=10),
  4 rows with q=3 (c=9),
  0 rows with q=1 (c=11).
```

This reduces the 62 Wave 30 aggregate complement profiles to one.  It is
retained as a correct necessary condition and hostile regression, not as
the exclusion proof.

## 7. Exact replay and hostile controls

The standard-library-only companion passed:

```text
Ran 15 tests
OK
```

It freezes all six inputs, checks the `-4` projector on every adjacency
eigenspace, audits the incidence scale and commutator coefficients,
enumerates all eight signed block sizes and all ten proper rootless block
ranks, checks both Wave 30 row residues, retains the superseded unique
rank-24 row profile, deletes every named essential premise fail-closed, and
regenerates LF-only JSON byte-identically.

The local sign mutation is active.  Replacing the two signs on the edges
`xz,yz` of one graph triangle by `+1,-1` gives

```text
(ZA-AZ)_xy=2.
```

Then the adjacent equation permits `d_x-d_y=-3`; it no longer forces
constancy.  This confirms that the proof uses shared graph-triangle signs,
not only an arbitrary signed adjacency matrix.

The complete non-improvement and scope ledger is
`attempts/wave31-survivor-proof/failed-routes.md`.

## 8. Boundary

This derivation changes the decomposable boundary but not the endpoint
status:

```text
rootless decomposable endpoint S-forms:  DERIVED IMPOSSIBLE
rootless indecomposable endpoint S-form: UNKNOWN
rooted endpoint S-form:                  UNKNOWN
n3=708:                                  UNKNOWN
Conway-99 existence/nonexistence:        UNKNOWN
novelty:                                 UNKNOWN
```

No automorphism, lattice catalog, numerical solver, restricted search, or
failure-to-find inference is used.  A fresh verifier must reconstruct the
incidence transport and local commutator before any promotion to
`VERIFIED`.
