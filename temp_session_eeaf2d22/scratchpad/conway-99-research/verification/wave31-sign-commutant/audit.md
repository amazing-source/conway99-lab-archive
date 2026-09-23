# Wave 31 sign-commutant adversarial verification

Verdict: **PASS for the scoped conditional claim**

```text
actual target-graph incidence/projector package
+ rootless even integral rank-44 endpoint S-form
+ nontrivial integral orthogonal decomposition

  ==> contradiction.
```

Equivalently, no nontrivial rootless integral orthogonal decomposition of
the scaled-dual endpoint `S`-form can occur under the actual
vertex-triangle incidence semantics of a putative `srg(99,14,1,2)`.  In
particular, the surviving Wave 30 rank-20 plus rank-24 decomposable type is
excluded.

This is not a resolution of Conway-99.  Rooted endpoint forms, rootless
integrally indecomposable endpoint forms, `n3=708`, graph existence or
nonexistence, and novelty all remain `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-24T06:56:26Z
git_commit: a8b0c34040f6857b3c5ebcc44f108e03a4159088
claim_label: VERIFIED
audit_verdict: PASS_SCOPED
scope: >-
  Independent adversarial verification that the actual target
  vertex-triangle incidence and rank-44 zero-projector package excludes
  every nontrivial rootless integral orthogonal decomposition of the
  scaled-dual endpoint S-form. Rooted and indecomposable endpoint forms,
  n3=708, Conway-99, and novelty remain UNKNOWN.
inputs:
  agents/2026-07-24-wave31-survivor-proof.md: 075566744e2622a4dfa402a125d394aef16dfcb3fc53b172176dce88bd951aaa
  attempts/wave31-survivor-proof/exact_check.py: 7613ecc5680bbb1539690e1308775014a2e32957e51036cf9de68ce2ae699956
  attempts/wave31-survivor-proof/test_exact_check.py: 24e81f7136bcfa188d5cea93fce36600ba198cbdbf0561ae4c0f4090b92d313b
  attempts/wave31-survivor-proof/exact-results.json: e5155e67a59168767639273ee70fc6d63e81b104e9b415e228ca09a0f9317587
  attempts/wave31-survivor-proof/input-freeze.sha256: 28f3b2890db2629686dae23484443582fc883914aeb85e2edc87e0149d479174
  attempts/wave31-survivor-proof/failed-routes.md: beaec0f3f988c2ed961e628d5d1c6ca73f1439b40f6e9b67536415f63d942c4f
  attempts/wave31-survivor-proof/run-report.yaml: 3cd2e7fe95e810416185cb1d098586a2ec42fc5539557dd7da4f2c5a4ecee0c6
  attempts/wave31-survivor-proof/artifact-manifest.sha256: c1d3b8d2a2ca25c4dcdb20fbc1d974f1561fa7c110524359443161d79bebd7f6
  agents/2026-07-23-wave20-global-schur.md: 64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/2026-07-22-n3-side-incidence-audit.md: 9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787
  agents/2026-07-24-wave30-general-h729.md: fd1f11a2ab5c5dfd2732a4ba1fb8d063dea1ae0e96d417aaf9d45eade4f2281a
  verification/wave30-general-h729/reverification-audit.md: 523a84e2a490f3626a791fb16f43b77b7631b3f26f2de8dcecc83f5e03f4d2cc
method: >-
  Frozen-commit and hash check; independent exact reconstruction of the
  SRG spectrum, incidence transport, coordinate-block implication,
  spectral-projector commutator, all 99 local summands, connectedness,
  double count, projector/block trace, and rank census; exact hostile
  countermodels; 21 independent tests; then submitted 15-test replay and
  deterministic certificate comparison.
command: |-
  cd verification/wave31-sign-commutant
  python -B independent_check.py --output independent-results.json
  python -B -m unittest -v test_independent_check.py
  cd ../../attempts/wave31-survivor-proof
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output ../../verification/wave31-sign-commutant/submitted-regenerated.json
  git diff --no-index --exit-code -- exact-results.json ../../verification/wave31-sign-commutant/submitted-regenerated.json
outputs:
  verification/wave31-sign-commutant/independent_check.py: 4e7f0979f8da94e34b084a60a95e8ce75a618cc513a19e4eccd75814242d7b22
  verification/wave31-sign-commutant/test_independent_check.py: 65f06e1a8355c28b77b52ceba6d2dbb095f5e9d37ebc7129fb35ae64ed1e3795
  verification/wave31-sign-commutant/independent-results.json: 7143c403172403b21ea2cdc2851851a3a13cb08b0dd14e5d68432aafd25fc5c0
  verification/wave31-sign-commutant/submitted-regenerated.json: e5155e67a59168767639273ee70fc6d63e81b104e9b415e228ca09a0f9317587
  verification/wave31-sign-commutant/input-freeze.sha256: c224fd23fc5eff1abd79cc3dcb19ecf8d97261914dc6f9fd844c19998a7cf6e4
limitations:
  - The result is conditional on a putative target graph and its actual incidence semantics.
  - Rootlessness, integrality, and an integral orthogonal decomposition are essential to induce the coordinate projector block.
  - No graph, frame, projector, lattice, Schur package, or endpoint object is constructed.
  - The verifier does not promote the superseded tensor side route.
  - Rooted and rootless indecomposable endpoint forms remain untreated.
  - n3=708, Conway-99, and novelty remain UNKNOWN.
```

## 1. Freeze and independence

The candidate was frozen at
`a8b0c34040f6857b3c5ebcc44f108e03a4159088`.  All eight candidate files
and all six cited upstream inputs match
`verification/wave31-sign-commutant/input-freeze.sha256`.  The candidate's
seven-entry artifact manifest and six-entry input freeze both validate.
`git diff --quiet` confirms that the candidate paths in the working tree
are byte-identical to the frozen commit even though later unrelated Wave 31
work exists in the shared tree.

The candidate report was read to identify the exact submitted claim and
obligations.  The independent implementation imports no candidate module
and derives its checks from the frozen structural identities.  Candidate
implementation details were then inspected adversarially and executed for
the submitted replay; they were not treated as proof.  Two wrong-directory
`unittest` invocations ran zero substantive tests and were corrected by
running the frozen command from the candidate directory; both harness
failures are retained in `failed-objections.md`.

## 2. Obligation-by-obligation verdict

| Obligation | Verdict | Independent conclusion |
|---|---:|---|
| `N` transports `im(E)` to the graph `-4` space | PASS | The squared norm scale is exactly 3, so the map is injective; both spaces have dimension 44. |
| Rootless integral block support | PASS | A norm-four row cannot have two nonzero lattice-block components when every nonzero component has norm at least four; parity is unnecessary. |
| Coordinate projector block and `DE=ED` | PASS | Cross-block `S`-products vanish, so `M=XSX^T` and `E=M/21` split by row coordinates. |
| Symmetric transport commutes with `P_-4` | PASS | `K=NDN^T` preserves `V`; symmetry also preserves `V^perp`. |
| Exact `-4` projector | PASS | Solving on eigenvalues `14,3,-4` gives `(27I-9A+J)/63`. |
| Full commutator sign and coefficient | PASS | Expansion gives `9(KA-AK)=KJ-JK`; `K1=3d` reduces this to coefficient 3. |
| Adjacent local cancellation | PASS | All 99 summands were partitioned; only the unique common-neighbor term survives on either side, with the same triangle sign. |
| Connectedness | PASS | `mu=2` gives a length-two path for every nonadjacent pair. |
| Signed-incidence double count | PASS | `99d=3(2b-231)`, hence `33|b`. |
| Submitted tight-frame trace | PASS | `4b=21r`; the only proper ranks are `4,8,...,40`, and every corresponding row count is nonzero modulo 33. |
| Shorter projector-trace strengthening | PASS | `E_I` is a projector with trace `4b/21`, so `21|b`; combined with `33|b`, this gives `231|b`. |
| Hypothesis and status boundary | PASS | Only rootless integrally decomposable actual-incidence endpoints are excluded. |
| Submitted tests and JSON replay | PASS | 15/15 tests pass; regenerated JSON is byte-identical, with SHA-256 `e5155e...f9317587`. |

No hidden automorphism, catalog completeness, numerical eigensolver, solver
timeout, or failure-to-find inference enters the proof.

## 3. Incidence transport

The target adjacency eigenvalues follow from

```text
t^2-(lambda-mu)t-(k-mu)=t^2+t-12=0,
```

so they are `3` and `-4`.  The trace and dimension equations give
multiplicities `54` and `44`.

For `u in im(E)=ker(Gamma)`,

```text
||Nu||^2
 =u^T N^T N u
 =u^T(3I+Gamma)u
 =3||u||^2.
```

Thus `N` is injective on `im(E)`.  Also,

```text
(7I+A)Nu
 =NN^TNu
 =N(3I+Gamma)u
 =3Nu,
```

and therefore `A(Nu)=-4Nu`.  The domain and target both have dimension 44,
so this is a bijection onto `V=ker(A+4I)` and a scaled isometry with squared
scale 3.  There is no missing kernel or saturation premise in this real
eigenspace argument.

## 4. From an integral split to a coordinate projector block

Put the integral orthogonal decomposition of `S` into block form by a
unimodular change of basis.  The transformed rows of `X` remain integral,
because the inverse transpose of a unimodular integral matrix is integral.
For a row

```text
x_i=(x_i1,...,x_im),
```

the endpoint diagonal gives

```text
sum_j x_ij^T S_j x_ij=4.
```

Every term is nonnegative, and each nonzero component is a nonzero lattice
vector.  Rootlessness, meaning minimum at least four here, makes every
nonzero term at least four.  Exactly one term is therefore nonzero.  Rows
from different lattice blocks are `S`-orthogonal, so after a row
permutation

```text
M=XSX^T=21E
```

is coordinate-block diagonal.

Choose one nonempty proper coordinate block `I` and put `D=+1` on `I`,
`D=-1` on its complement.  Then `DE=ED`, so `D` preserves `im(E)`.
The rootlessness and integral-split hypotheses are used here; they are not
quietly extended to rooted or rationally decomposable forms.
Evenness of `S` is an inherited endpoint hypothesis but is logically
unnecessary for this one-block support implication.

## 5. Symmetric transport and the commutator

Define

```text
K=NDN^T.
```

For `u in im(E)`,

```text
K(Nu)
 =ND(3I+Gamma)u
 =3N(Du)
 in V.
```

Thus `K` preserves `V`.  It is symmetric, so it also preserves `V^perp`
and commutes with the orthogonal projector onto `V`.

Solving `P=alpha I+beta A+gamma J` on the three adjacency eigenspaces gives

```text
alpha=3/7, beta=-1/7, gamma=1/63,
P_-4=(27I-9A+J)/63.
```

Expanding `KP=PK` with no numerical approximation gives

```text
9(KA-AK)=KJ-JK.                                  (1)
```

Let `s` be the diagonal of `D` and `d=Ns`.  Since every graph triangle has
three vertices,

```text
N^T1=3*1,
K1=NDN^T1=3Ns=3d.
```

Symmetry gives `1^TK=3d^T`, so (1) becomes

```text
3(KA-AK)=d1^T-1d^T.                              (2)
```

The signs and factors `9`, `3`, and `3` all pass an independent exact
generic-matrix expansion.

## 6. All local summands on an edge

For adjacent vertices `x,y`, let `z` be their unique common neighbor.  It
completes their unique graph triangle `T=xyz`.  Write

```text
K=diag(d)+Z,
```

where `Z_xy` on an edge is the sign of its unique graph triangle and is zero
on a nonedge.

The 99 summation indices in `(ZA)_xy` and `(AZ)_xy` partition as follows:

| index class for `w` | count | `Z_xw A_wy` | `A_xw Z_wy` |
|---|---:|---:|---:|
| `w=x` | 1 | 0 | 0 |
| `w=y` | 1 | 0 | 0 |
| unique common neighbor `z` | 1 | `s_T` | `s_T` |
| neighbor only of `x` | 12 | 0 | 0 |
| neighbor only of `y` | 12 | 0 | 0 |
| remaining vertices | 72 | 0 | 0 |
| **total** | **99** | **`s_T`** | **`s_T`** |

Thus

```text
(ZA-AZ)_xy=0.
```

Taking the `(x,y)` entry of (2) gives

```text
3(d_x-d_y)=d_x-d_y,
```

and hence `d_x=d_y` on every edge.  Since `mu=2`, every nonadjacent pair
has a common neighbor and the graph is connected.  Therefore `d` is
constant on all 99 vertices.

The same-triangle premise is active.  Mutating `Z_xz=+1` and `Z_zy=-1`
makes the local commutator equal two; equation (2) then permits
`d_x-d_y=-3` instead of forcing equality.

## 7. Divisibility contradiction

Let `b=|I|`.  Summing the constant signed degree by vertices and by signed
triangles gives

```text
99d=3(2b-231),
33d=2b-231.
```

Because `231=7*33` and `gcd(2,33)=1`,

```text
33 divides b.                                    (3)
```

The submitted frame calculation is correct.  Restricting
`X^TX=21S^(-1)` to the selected block, multiplying by `S_I`, and taking
traces gives

```text
4b=21r.                                          (4)
```

Consequently `r=4k`, `b=21k`.  The ten proper ranks
`r=4,8,...,40` give row counts

```text
21,42,63,84,105,126,147,168,189,210,
```

whose residues modulo 33 are respectively

```text
21,9,30,18,6,27,15,3,24,12.
```

None satisfies (3).

There is a shorter verifier strengthening.  Coordinate block diagonality
and `E^2=E` make the selected block `E_I` an orthogonal projector.  Since
`E_ii=4/21`,

```text
rank(E_I)=tr(E_I)=4b/21.
```

Its integral rank directly gives `21|b`.  Combining this with (3) gives

```text
lcm(21,33)=231 divides b.
```

The selected block is nonempty and proper, so `0<b<231`, a contradiction.
This uses no new hypothesis and confirms the submitted rank-trace route
from a more economical direction.  In particular, the Wave 30 sides have
`105=6 mod 33` and `126=27 mod 33`, so both fail independently.

## 8. Hostile controls and limitations

The full objection ledger is
`verification/wave31-sign-commutant/failed-objections.md`.  Exact
countermodels confirm that the proof can fail after deleting the
nonzero-component minimum floor, `DE=ED`, symmetry of `K`, the shared
triangle sign, connectedness, or actual incidence transport.  The `[1,3]`
control concerns loss of that norm floor, not deletion of evenness alone.
It also serves as a control when integrality and evenness are dropped
together.

Once an integral `S`-decomposition has induced a proper coordinate block of
`E`, the remainder of the contradiction needs only the actual graph
incidence/projector data.  Rootlessness is not used again.  This observation
narrows the role of the hypothesis; it does not extend the theorem to rooted
forms because rootedness is precisely where the coordinate-block implication
can fail.

## 9. Reproduction

The independent standard-library checker produced

```text
Ran 21 tests
OK
```

It exactly derives the SRG spectrum and multiplicities, projector
coefficients, incidence scale, block-support patterns, commutator
coefficients, all 99 adjacent summands, connectedness, all eight constant
signed-degree sizes, all ten proper ranks, and the direct projector-trace
strengthening.  It also retains exact 2-by-2 countermodels and fails closed
when any named essential premise is removed.

The frozen submitted package separately produced

```text
Ran 15 tests
OK
```

Its regenerated JSON is byte-identical to the submitted
`exact-results.json`, including LF termination and SHA-256
`e5155e67a59168767639273ee70fc6d63e81b104e9b415e228ca09a0f9317587`.

## 10. Status wall

```text
rootless integrally decomposable endpoint S-forms: VERIFIED IMPOSSIBLE
Wave 30 rank-20 plus rank-24 decomposable type:    VERIFIED IMPOSSIBLE
rootless integrally indecomposable endpoint forms: UNKNOWN
rooted endpoint forms:                             UNKNOWN
n3=708:                                           UNKNOWN
Conway-99 existence/nonexistence:                  UNKNOWN
novelty:                                           UNKNOWN
```

The PASS verdict is scoped to the conditional endpoint theorem.  It is not
evidence for a global resolution beyond that scope.

## 11. Verifier QA correction

Before freeze, verifier QA corrected one hostile-control label.  The initial
label suggested that `[1,3]` showed failure after deleting evenness while
retaining all other premises.  It does not: minimum at least four alone
forbids both nonzero components.  The control now represents deletion of
the nonzero-component norm floor, potentially together with loss of the
integral lattice-component interpretation and evenness.  Evenness alone
remains inherited but unused in the support step.

This correction changes no candidate byte, equation, scoped PASS verdict,
or `UNKNOWN` status.
