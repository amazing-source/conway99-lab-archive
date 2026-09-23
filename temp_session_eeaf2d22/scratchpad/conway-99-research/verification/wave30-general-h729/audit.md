# Wave 30 independent audit: decomposable rootless `h=729` forms

Verdict:

```text
scoped conditional mathematical classification:  VERIFIED
submitted discovery replay:                        FAIL
publication of the submitted package as-is:        VETOED
```

The mathematical implication survives a fresh reconstruction. Under the full
frozen `n3=708` endpoint package, every rootless, even, integral,
positive-definite rank-44 `S`-form of determinant 729 which has a nontrivial
integral orthogonal decomposition necessarily reduces to

```text
S = A_20 orthogonal_sum U_24,
det(A_20)=729,
det(U_24)=1,
rows=(105,126),
tr(B_A)=36,
tr(B_U)=24,
B_U=I_24.
```

Fourteen of the fifteen aggregate rank/determinant types are excluded.

This verification does **not** certify the submitted discovery package for
publication without repair. Its checker freezes a Wave 29 audit hash that is
not the hash of the committed artifact, so its advertised test and generator
commands fail before performing the census. The theorem and the package gate
are reported separately below.

The remaining rank-20 plus rank-24 type, rooted or integrally indecomposable
forms, the full `h=729` endpoint, `n3=708`, Conway-99, and novelty remain
`UNKNOWN`.

## 1. Blind freeze and preserved replay failure

At `2026-07-24T04:24:29Z`, before opening any Wave 30 discovery content, the
verifier recorded SHA-256 hashes for the report and all seven discovery
package files. The freeze is
`verification/wave30-general-h729/protocol-freeze.md`. It also fixes:

```text
branch: codex/first-research-wave
HEAD: ae8fd70baaeb35302f957653e20ad710e5e77281
HEAD tree: 385605545e6784ee290d17afdfd460e4fe526ef3
public branch: aadc0dafce387233fc16406cc9822f069becd645
```

All eight discovery hashes still match that freeze.

The submitted checker and input-freeze file expect:

```text
4101a394252807fb9de8c39fb32b780bc88410d99e47dfe698da251b49f3e061
  verification/wave29-s0-frame-exclusion/audit.md
```

The current applicable and committed artifact is:

```text
dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d
  verification/wave29-s0-frame-exclusion/audit.md
```

Git history has only one commit for that path,
`5dbff08f8cb53102118acd281a6d4b353a962cf8`, and hashing its blob gives the
current `dbdcb88b...` value. Thus the submitted `4101a394...` input is not
reconstructible from the tracked version of that path.

Fresh submitted replay gives:

```text
python -B -m unittest -v test_exact_check.py
  setUpClass ERROR
  Ran 0 tests
  frozen input drift: dbdcb88b... != 4101a394...

python -B exact_check.py --output <temporary-path>
  ERROR at verify_frozen_inputs
  no output written
```

This is a substantive provenance and replay failure, not a mathematical
counterexample. The independent verifier therefore reconstructed the theorem
against the current committed `dbdcb88b...` audit and did not edit any
discovery artifact.

## 2. Exact imported hypotheses

The current Wave 24, Wave 25, Wave 28, and Wave 29 artifacts independently
support the endpoint premises used here:

```text
X in Z^(231 x 44), full column rank,
G=X^T X=21 S^(-1),
M=XSX^T,
W=M o M,
Q=X^T W X,
B=SQ=I+2C,
```

with:

```text
S, G, Q even integral positive definite,
det(S)=729,
B integral and self-adjoint for G,
B has positive real spectrum,
M 1=0,
diag(M)=4,
offdiag(M) in {0,1,-1,-2},
M^2=21M,
tr(B)=60,
det(B)=det(S)det(Q)<=6525,
det(Q)>=5,
det(Q)=1 mod 4.
```

The current hashes of all five prior artifacts used by the verifier are
checked before result generation. The proof below is conditional on this
endpoint package. It does not derive the package from an independently
constructed graph.

## 3. Integral decomposition forces row support

Let a unimodular basis make

```text
S=S_1 orthogonal_sum ... orthogonal_sum S_m,  m>=2.
```

The inverse-transpose basis change keeps all rows of `X` integral. If
`x_i=(x_i1,...,x_im)` is a norm-four row, then each nonzero component has
positive norm at least four because `S` is rootless. Hence exactly one
component is nonzero.

After permuting rows, `X` is rectangular block diagonal. Direct multiplication
then makes `M` block diagonal. Entrywise squaring preserves every cross zero,
so `W`, `Q`, `B`, and `C` inherit the same split. No rational projection or
unstated automorphism is used.

On each original block `J`,

```text
X_J^T X_J=21 S_J^(-1),
4 n_J=21 rank(S_J).
```

Thus every original rank is divisible by four. A rational orthogonal split is
insufficient: for `S=4I_2`, the rational orthogonal lines spanned by `(1,1)`
and `(1,-1)` give the integral norm-four vector `(1,0)` two nonintegral,
nonzero projections. Likewise, if the block minima are lowered to two, a
`2+2` mixed row becomes possible.

## 4. Determinant allocation and the complete fifteen-type census

The endpoint bound gives:

```text
det(Q)<=floor(6525/729)=8.
```

Together with `det(Q)>=5` and `det(Q)=1 mod 4`, this leaves only
`det(Q)=5`. Positive integer block determinants therefore put determinant
five on exactly one original block, called `A`; every other `Q` block has
determinant one.

Every determinant-one `Q` block is even unimodular positive definite, hence
has rank divisible by eight. Group them as `R`. Since the total rank is 44:

```text
rank(A) in {4,12,20,28,36}.
```

The independent checker enumerates every unordered partition of each
complement rank into positive multiples of eight. This verifies that grouping
arbitrarily many original blocks into `R` does not omit a decomposition type.

Write `det(S_A)=3^a`. The odd-determinant congruence for an even form is:

```text
det(S_A)=(-1)^(rank(A)/2) mod 4.
```

Every listed exceptional rank is `4 mod 8`, so `a` is even. The case `a=0`
would make `S_A` even unimodular in forbidden signature `4 mod 8`. Therefore:

```text
a in {2,4,6}.
```

These five ranks and three exponents give the complete fifteen aggregate
types. This is a necessary arithmetic census, not an existence claim for
fifteen lattices.

## 5. Block traces are positive multiples of six

For one row, let `a_i,b_i,c_i,z_i` count off-diagonal entries
`+1,-1,-2,0`. The exact row-sum and projector-square equations are:

```text
4+a_i-b_i-2c_i=0,
16+a_i+b_i+4c_i=84,
a_i+b_i+c_i+z_i=230.
```

Independent nested integer enumeration gives exactly:

```text
a_i=32-c_i,
b_i=36-3c_i,
z_i=162+3c_i,
0<=c_i<=12.
```

The cubic row sum is `60-6c_i`. On a block:

```text
tr(B_J)
 =tr(S_J X_J^T W_J X_J)
 =tr(M_J W_J)
 =sum_(i,j in J) M_ij^3.
```

Every block trace is therefore a multiple of six. It is positive because
`B_J` is similar to a symmetric positive-definite matrix. Consequently:

```text
tr(B_A)+tr(B_R)=60,
tr(B_A),tr(B_R) in {6,12,...,54}.
```

## 6. Exact AM-GM and characteristic-pseudodeterminant cap

For a positive-spectrum rank-`d` block with trace `t` and determinant `D`,
AM-GM is checked with integers:

```text
t^d >= d^d D.
```

For the second bound, write the real eigenvalues of integral,
positive-form-self-adjoint `C_J` as `mu_i`. Positivity of
`B_J=I+2C_J` gives `mu_i>-1/2`. Set:

```text
L=log(3),
c=L-2/3.
```

The positive-term `atanh(1/2)` series proves the exact rational enclosure:

```text
1 < log(3) < 4/3,
```

which is more than enough for `2/3<L<2` and `c>0`. For nonzero
`x>-1/2`:

```text
log(1+2x)<=xL-c log|x|.
```

On `x>0`, direct formal differentiation gives:

```text
x(1+2x)F'(x)=(x-1)(2Lx+c),
```

so equality occurs only at `x=1`. On `-1/2<x<0`, the inequality is strict
because `g'(x)<L-2<0` and `g(0)=0`.

The nonzero characteristic coefficient of integral `C_J` gives:

```text
|product_(mu_i nonzero) mu_i|>=1.
```

Summing the pointwise inequality therefore proves:

```text
det(B_J)<=3^tr(C_J),
tr(C_J)=(tr(B_J)-rank(J))/2.
```

This argument does not assume `C_J` is positive semidefinite. A nonintegral
control `C=(1/2)I_12` has trace six and
`det(I+2C)=4096>729`, proving that the characteristic integrality premise is
active. The integral nonsymmetric control
`C=[[1,N],[-N,1]]` has complex eigenvalues and determinant
`9+4N^2`, proving that the self-adjoint real-spectrum premise is active.

## 7. The exact census and four equality vetoes

The independent enumeration is:

| `rank(A)` | `a` | AM-GM trace pair | outcome |
|---:|---:|---:|---|
| 4 | 2 | `(12,48)` | complement log equality; rank-4 image veto |
| 4 | 4 | none | AM-GM plus trace residue |
| 4 | 6 | none | AM-GM plus trace residue |
| 12 | 2 | `(18,42)` | `45>3^3` on `A` |
| 12 | 4 | `(24,36)` | complement log equality; rank-2 image veto |
| 12 | 6 | `(24,36)` | `3645>3^6` on `A` |
| 20 | 2 | `(30,30)` | `81>3^3` on `R` |
| 20 | 4 | `(30,30)` | `405>3^5` on `A` |
| 20 | 6 | `(36,24)` | survives |
| 28 | 2 | `(36,24)` | complement log equality; rank-4 image veto |
| 28 | 4 | `(36,24)` | `405>3^4` on `A` |
| 28 | 6 | `(42,18)` | `3645>3^7` on `A` |
| 36 | 2 | `(42,18)` | `45>3^3` on `A` |
| 36 | 4 | `(48,12)` | complement log equality; rank-2 image veto |
| 36 | 6 | `(48,12)` | `3645>3^6` on `A` |

For a complement equality, every nonzero `C_R` eigenvalue is one and no
negative eigenvalue occurs. Real diagonalizability gives `C_R^2=C_R`.
Because `C_R` is an integral idempotent:

```text
Z^s=im(C_R) direct_sum ker(C_R).
```

Self-adjointness makes the split `G_R`-orthogonal. In an adapted unimodular
basis:

```text
B_R=3I_k orthogonal_sum I_(s-k),
Q_R=(G_image/7) orthogonal_sum (G_kernel/21).
```

Both nonzero `Q` restrictions are even integral positive definite. Their
positive integer determinants multiply to `det(Q_R)=1`, so both are even
unimodular and both ranks must be divisible by eight.

The four excluded equality cases have `k=4,2,4,2`, respectively. The surviving
case `(20,6)` also has complement log equality, but there `k=0` and the
kernel rank is 24, so the signature test correctly permits it. This fifth,
non-vetoed equality was explicitly retained after a hostile test caught an
initial verifier test that counted only the four vetoes.

The obstruction counts are:

```text
AM-GM plus trace residue:                    2
A logarithmic cap:                          7
R logarithmic cap:                          1
integral-idempotent signature veto:         4
survives:                                    1
```

## 8. Surviving boundary and complement constraints

For `(rank(A),a)=(20,6)`:

```text
det(S_A)=729, det(Q_A)=5, det(B_A)=3645, tr(B_A)=36,
det(S_U)=1,   det(Q_U)=1, det(B_U)=1,    tr(B_U)=24.
```

The shell equation gives 105 and 126 rows. AM-GM on the 24 positive
eigenvalues of `B_U` is equality, so every eigenvalue is one. Since `B_U` is
diagonalizable, `B_U=I_24` and `C_U=0`.

Normalize the complement rows to Euclidean vectors `y_i` and define:

```text
Phi(v)=sum_i <v,y_i> y_i tensor y_i.
```

Direct expansion gives:

```text
Phi^*Phi=S_U^(1/2) Q_U S_U^(1/2)=I_24.
```

For a row `y_i`, the relevant norms are two and four, hence Cauchy gives:

```text
|sum_j <y_i,y_j>^3|<=8.
```

Combining this with the cubic row formula forces `c_i in {9,10,11}`.
The trace gives:

```text
sum_(i in U)c_i=1256.
```

The 62 nonnegative aggregate profiles are exactly:

```text
n_9=n_11+4,
n_10=122-2n_11,
0<=n_11<=61.
```

Their directed internal totals are:

```text
+1: 2776,  -1: 768,  -2: 1256,  0: 10950.
```

All four totals have the parity required by symmetry. These are necessary
counts only. They do not construct `M`, `X`, either lattice block, or a graph.

The integral scalar control:

```text
spec(C_A)={2^1,1^6,0^13},
spec(B_A)={5^1,3^6,1^13}
```

has traces 8 and 36, trace square 10, and determinant 3645. It confirms that
the scalar inequalities alone do not exclude the final type; it is not a
lattice or frame realization.

## 9. Hostile controls and deterministic verification

The two independent test files contain 32 tests. They cover:

- all frozen discovery and current prior hashes;
- the submitted zero-test replay failure;
- all thirteen row-alphabet solutions;
- arbitrary-many-block complement partitions;
- all fifteen rank/determinant types and exact trace pairs;
- exact integer AM-GM comparisons;
- formal logarithmic derivative coefficients and exact rational log bounds;
- all four equality-rank vetoes and the permitted zero-image equality;
- the unique survivor, frame counts, Schur data, tensor profiles, and directed
  totals;
- deletion of every named essential hypothesis;
- explicit controls for minimum two, rational-only splitting, missing
  determinant congruence, missing trace residue, nonintegral `C`,
  non-self-adjoint `C`, use of only one log cap, omission of the equality
  split, and omission of evenness; and
- byte-identical LF-only JSON regeneration.

Fresh independent replay:

```text
python -B -m unittest -v test_independent_check.py test_hostile_controls.py
Ran 32 tests
OK

python -B independent_check.py --output independent-results.json
sha256:
2b948591611e9c984985f7bacc5a77c714332fbe42ed5305b84039c621358416
```

## 10. Obligation and status table

| Obligation | Result |
|---|---:|
| Blind preinspection freeze | PASS |
| Discovery artifacts unchanged after freeze | PASS |
| Current prior-artifact hashes | PASS |
| Submitted discovery test replay | **FAIL: 0 tests** |
| Submitted discovery JSON regeneration | **FAIL: input drift** |
| Integral row-support split | PASS |
| Arbitrary-many-block inheritance | PASS |
| Unique `det(Q)=5` allocation | PASS |
| Complete fifteen-type rank/determinant census | PASS |
| Row alphabet and trace residue | PASS |
| Exact AM-GM census | PASS |
| Characteristic-pseudodeterminant cap, including negative spectrum | PASS |
| Equality integral split and rank vetoes | PASS |
| Fourteen exclusions | PASS |
| Unique rank-20 plus rank-24 survivor | PASS |
| `105/126`, `36/24`, and `B_U=I` | PASS |
| Tensor-isometry necessary counts | PASS |
| Independent deterministic JSON | PASS |
| Publication of discovery package unchanged | **VETOED** |
| Remaining decomposition type | UNKNOWN |
| Rooted or indecomposable `h=729` forms | UNKNOWN |
| `n3=708` | UNKNOWN |
| Conway-99 | UNKNOWN |
| Novelty | UNKNOWN |

## 11. Required recorded repair

The following discovery artifacts must be revised in a new, preserved repair
record, not silently overwritten:

```text
agents/2026-07-24-wave30-general-h729.md
attempts/wave30-general-h729/exact_check.py
attempts/wave30-general-h729/exact-results.json
attempts/wave30-general-h729/input-freeze.sha256
attempts/wave30-general-h729/run-report.yaml
attempts/wave30-general-h729/artifact-manifest.sha256
```

The test source can remain unchanged if it passes against the repaired input,
but it must be rerun. The repaired result and all dependent hashes must then be
frozen and independently re-verified. Until that occurs:

```text
conditional mathematical classification:  VERIFIED
submitted discovery package:               REPLAY FAIL
publication gate:                          FAIL
```
