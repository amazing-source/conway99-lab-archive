# Independent Wave 205 fourth-trace globalization audit

## Verdict

`VERIFIED_WITH_SCOPE_NO_FINDING`.

The three sealed Wave 205 packages match their orchestrator-supplied
manifest hashes and replay without a mathematical discrepancy.  An
independent post-source checker that does not import discovery Python
reproduces the exact central claims.

This verification promotes only the scoped algebra, finite censuses, and
relaxed-control predicates.  It does not classify actual endpoint nonedges,
construct or exclude the endpoint, or change Conway-99 status.

## Run report

```yaml
role: verifier
date_utc: 2026-07-29T20:31:05Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: VERIFIED
scope: >-
  Source-blind and post-source independent verification of Wave 205
  fourth-trace algebra, nonedge profile/census controls, full-matrix
  factorization, tensor dimensions, and progressively stronger relaxed
  incidence/projector controls.
inputs:
  attempts/wave205-nonedge-fourth-trace-proof-a/package-manifest.sha256: 2c9976b6cb07a3036df07fd0e7ceb7ffce6a339651d604fcecdcf8c0c3da3d96
  attempts/wave205-global-fourth-moment-proof-b/package-manifest.sha256: a91a2a1cdbc129fa66e9d63b34031a774d5af78c458d18d9a1aadd7e4be217e7
  attempts/wave205-fourth-trace-hostile-controls/package-manifest.sha256: b9700d135bbfdebc34aeaad88eb1264b95732fa0f9da773cf90bd002331cc971
  verification/wave205-fourth-trace-globalization-verifier/SOURCE_BLIND_FREEZE.sha256: f8fb87d76c5eda2ff2569ec49a935b8bdb4022671f6d51f2752c14e153bcc853
method: >-
  Frozen source-blind modular algebra and hostile radical controls; then an
  independent JSON-certificate replay, independent 5-by-5 margin census,
  exact local-graph checks, exact projector/incidence reconstruction, and
  separate discovery-package replays.
command: >-
  python -B -m unittest -v
  verification/wave205-fourth-trace-globalization-verifier/test_independent_verifier.py;
  python -B -m unittest -v
  verification/wave205-fourth-trace-globalization-verifier/test_post_source_audit.py;
  run each sealed package replay and test suite as recorded below
outputs:
  verification/wave205-fourth-trace-globalization-verifier/post_source_audit.py: see package-manifest.sha256
  verification/wave205-fourth-trace-globalization-verifier/post_source_result.json: see package-manifest.sha256
  verification/wave205-fourth-trace-globalization-verifier/audit.md: see package-manifest.sha256
limitations:
  - Proof-A controls have only 28 vertices and leave global completion open.
  - Proof-B's zero-first-moment control repeats projector labels.
  - The 99-by-231 hostile controls use only 21 projective directions and fail the target lambda/mu laws.
  - The computational replay did not certify literature novelty or search completeness.
  - No endpoint, rank-11, n3=4158, strict-bound, or Conway-99 promotion follows.
```

## 1. Source-blind freeze

Before any Wave 205 discovery file was opened, the verifier sealed:

```text
SOURCE_BLIND_FREEZE.sha256
f8fb87d76c5eda2ff2569ec49a935b8bdb4022671f6d51f2752c14e153bcc853
```

All four entries rehash exactly.  The nine blind tests verified:

- the `7 by 7` cross-Gram and `6 by 6` localizer formulas;
- the crossing and wedge-square fourth-trace identities;
- the correct 2,145-dimensional quadratic feature space;
- the correct 1,539-dimensional trace-zero self-adjoint operator space for
  `wedge^2(P_x)`, not a 55-dimensional vector space;
- the prism-free disjoint-triangle cross-edge cap; and
- a hostile radical lift where a Gram-kernel word is not a true relation.

## 2. Proof A: nonedge profile and low-count census

`VERIFIED_WITH_SCOPE`.

For a nonedge, after labeling the two common neighbors first, the checker
reproduces

```text
marked corner:       [[1,2],[2,1]]
marked row/column:   0^0 1^5 2^2
ordinary total:      6
t_xy lower bound:    6
nonneighbor average: 7
g_xy:                2*t_xy in F_3
```

The two off-diagonal marked twos are forced by the two center-to-common-
neighbor edges and the prism-free cap.  Each marked row and column has one
further ordinary two.  This gives the six forced two-entries and proves
`t_xy>=6`.

The independent normalized enumeration reconstructs all four equality-
pattern boundary cases and obtains:

| `t` | normalized matrices | admissible `h=0` | `h=1` | `h=2` |
|---:|---:|---:|---:|---:|
| 6 | 646 | 0 | 18 | 0 |
| 7 | 7,886 | 297 | 324 | 144 |

“Admissible” here means full union-Gram rank 11, nonsquare discriminant two,
and true-relation minimum weight at least four.  At full ambient rank, the
Gram kernel is the actual relation code; this inference is not used at
lower rank.

All four 28-vertex adjacency certificates independently reproduce:

```text
t6_h1, t7_h0, t7_h1, t7_h2.
```

Each has degree-14 frozen centers, exactly two center common neighbors,
opposite-center `mu=2` for every exclusive neighbor, local `lambda<=1` and
`mu<=2`, the selected disjoint-block crossing cap, union-Gram rank 11,
discriminant two, and the claimed fourth trace.  The `t6_h1` relation
distance is six; each `t=7` control has distance four.

Therefore these pair-local implications are refuted:

```text
local projectivity/relation distance forces t_xy>=7;
fixed t_xy=7 plus the checked pair data determines h_xy.
```

This is not an actual nonedge classification.  The missing premise is the
simultaneous 99-center extension law for overlapping two-center balls.

## 3. Proof B: global fourth-moment boundary

`VERIFIED_WITH_SCOPE`.

The exact transfer to ordered triangle-pair coordinates is:

```text
u_x[(T,U)]=B[x,T]B[x,U],
K_D[(T,U),(R,S)]=D[T,R]D[R,U]D[U,S]D[S,T],
H=U K_D U^T.
```

Any two distinct blocks through point `x` share no other point, so their
ordered-pair feature column is `e_x`.  The 99 unit columns prove:

```text
rank_F3(U)=99.
```

The independent toy contraction also reproduces

```text
sum_x u_x=vec(Q),  Q=B^T B,
M_x=D S_x D,
(H 1)_x=tr((Q o M_x)M_x),
w_TU=B(D_T o D_U),
(K_D vec(Q))_(T,U)=w_TU^T w_TU.
```

The correct dimension ledger is:

```text
self-adjoint End(V)                         66
trace-zero self-adjoint End(V)              65
Sym^2(trace-zero self-adjoint End(V))     2145
wedge^2 V                                   55
self-adjoint End(wedge^2 V)               1540
trace-zero self-adjoint End(wedge^2 V)    1539
Sym^2 V                                     66
self-adjoint End(Sym^2 V)                 2211
trace-zero self-adjoint End(Sym^2 V)      2210
```

Every listed cap exceeds 99 and gives no endpoint rank obstruction.

The independent 99-label zero-first-moment control reproduces:

```text
sum_x P_x=0
rank(pair-trace matrix)=8
pair-trace row sums: 0^99
rank(H)=9
H row sums: 0^6 1^91 2^2
g_xy != h_xy on 740 ordered pairs
quadratic moment nonzero coordinates: 302
```

Thus `sum_x P_x=0` does not generically imply `H 1=0`.  This control has
only 12 distinct projectors and no target incidence, so it cannot refute a
future identity using the omitted graph/code premises.

## 4. Stronger hostile incidence/projector controls

`VERIFIED_RELAXED_CONTROL`.

The complete JSON certificate independently verifies:

- three exact rank-six trace-zero self-adjoint projectors in the nonsquare
  11-space, each generated by a seven-column singular simplex;
- a linear `99 by 231` incidence with row degree seven, column degree three,
  and a simple 14-regular point graph;
- exact star/projector coupling at every point;
- column and centered-Gram rank 11, `D^2=0`, and zero global frame;
- identical full pair-trace matrices in the two realizations;
- identical fourth traces on all 693 graph edges; and
- 3,888 ordered nonedge fourth-trace differences.

The target failures are material:

```text
only 21 projective column directions;
components 27,36,36;
1,329 graph triangles, 1,098 beyond the 231 designated blocks;
edge common-neighbor counts 4..9, not lambda=1;
nonedge common-neighbor counts nonconstant, including 0;
no endpoint block-orthogonality, outer-cycle, prism, distance, or cover law.
```

The control is stronger than a pairwise construction but is not an SRG,
endpoint code, or endpoint configuration.

## 5. Replay integrity and findings

```text
independent blind tests:             9/9 PASS
independent post-source tests:       8/8 PASS
Proof-A frozen replay/tests:         PASS / 13 of 13
Proof-B frozen replay/tests:         PASS / 12 of 12
hostile frozen result/certificate:   PASS
hostile plain test functions:        6 of 6 PASS
hostile pytest wrapper:              NOT RUN (pytest not installed)
mathematical/scope findings:         NONE
```

The absent pytest package is a tooling limitation only: the same six plain
test functions were invoked directly and passed, and the certificate was
also reconstructed by the independent post-source checker.

## Status wall

```text
Conway-99:                 UNKNOWN
rank-11 endpoint:          UNKNOWN
n3=4158 endpoint:          UNKNOWN
rigorous n3 interval:      708<=n3<=4158
conditional Q bound:       Q>=7059
Q>=7060:                   NOT PROVED
automorphism assumption:   NONE
```
