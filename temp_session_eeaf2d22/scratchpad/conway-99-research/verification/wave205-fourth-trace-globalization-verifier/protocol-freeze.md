# Wave 205 source-blind verifier protocol freeze

```yaml
role: verifier
date_utc: 2026-07-29T20:20:38Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: VERIFIED
scope: >-
  Source-blind exact verification of fourth-trace algebra, seven-column
  star-pair localization, tensor ambient dimensions, Gram-radical hazards,
  and graph-forced constraints on a nonedge cross-Gram matrix under the
  frozen prism-free rank-11 endpoint.
inputs:
  AGENTS.md: repository instructions
  attempts/wave205-fourth-trace-globalization/protocol.md: frozen Wave 205 protocol
  verification/wave171-pq-centered-code/verification-report.md: 1f2ba5ed92ba6bb1ccc05cd753a8e359f208c3ddc7ca85766f26f8869346414f
  verification/wave176-star-projector-circuits/audit.md: f58577409f39e98b06bfbe206221d3d278f0c473bcf5057afc381094d5e65d05
  agents/2026-07-29-wave191-global-star-module-proof-b.md: afe7d35627ec14a9599b427bcca0751e86a3f32b71fb7baf4d91e9e2e335f75f
  verification/wave203-two-center-incidence-verifier/audit.md: 382d8553457557fe2ecbe0fd1733ecb06b01f5c60be879e65cab56c078edc3d7
  verification/wave204-global-compatibility-verifier/package-manifest.sha256: 48cd018c7f7cebe7f2bc93a6dbd9440422f8dc843bc6c0fa96b29968e440f9c2
  verification/2026-07-29-wave204-orchestrator.md: 7760a4c5a4b6a501262bbb3b061828725cd23c6837fd724fada84d94a3124edd
method: >-
  Independent derivation over F_3, exhaustive enumeration of all 3 by 3
  cross-edge masks satisfying the local lambda/mu inequalities, exact modular
  linear algebra, explicit two-star relaxed controls, and hostile realizations
  separating Gram-kernel words from true vector relations.
command: >-
  python -B -m unittest -v
  verification/wave205-fourth-trace-globalization-verifier/test_independent_verifier.py;
  python -B
  verification/wave205-fourth-trace-globalization-verifier/independent_verifier.py
outputs:
  - verification/wave205-fourth-trace-globalization-verifier/independent_verifier.py
  - verification/wave205-fourth-trace-globalization-verifier/test_independent_verifier.py
  - verification/wave205-fourth-trace-globalization-verifier/blind_result.json
  - verification/wave205-fourth-trace-globalization-verifier/SOURCE_BLIND_FREEZE.sha256
limitations:
  - The explicit 7 by 7 cross-Gram controls are exact local orthogonal-space
    realizations, not SRGs, 99-star systems, or 231-column configurations.
  - Integer crossing margins and local lambda/mu feasibility are necessary
    graph consequences, not a complete nonedge classification.
  - No Wave 205 discovery source, report, manifest, code, result, or hostile
    control was opened before this freeze.
  - No endpoint exclusion, construction, strict n3 improvement, external
    novelty result, or Conway-99 status change is claimed.
```

## Embargo and status wall

Until `SOURCE_BLIND_FREEZE.sha256` is written and its SHA-256 is sent to the
orchestrator, this verifier will not open or execute any Wave 205 discovery
package, report, manifest, or hostile control.

```text
Conway-99:                 UNKNOWN
rank-11 endpoint:          UNKNOWN
n3=4158 endpoint:          UNKNOWN
rigorous n3 interval:      708<=n3<=4158
conditional Q bound:       Q>=7059
Q>=7060:                   NOT PROVED
automorphism assumption:   NONE
```

## Independently frozen algebra

Let `Z_x,Z_y` be the `11 by 7` matrices of the two point-stars, let
`S=J_7-I_7`, and put

```text
Z_x^T Z_x=Z_y^T Z_y=S,
Z_x 1=Z_y 1=0,
P_x=-Z_x Z_x^T,
P_y=-Z_y Z_y^T,
C=Z_x^T Z_y.
```

Then, exactly over `F_3`,

```text
C 1=0, 1^T C=0,
rank(C)=rank(P_x P_y),
g_xy=tr(C C^T),
h_xy=tr((C C^T)^2).
```

For `L=[I_6; -1^T]`, `G=L^T L`, and
`R=G^{-1}L^T`, the localized matrix `A=R C R^T` reconstructs the full
cross-Gram matrix:

```text
C=L A L^T,
rank(A)=rank(C),
g_xy=tr(A G A^T G),
h_xy=tr((A G A^T G)^2).
```

The full fourth trace is a crossing contraction of the pure quadratic
features `P_x tensor P_x`.  Because each `P_x` is a trace-zero
self-adjoint operator on an 11-space, these features lie in

```text
Sym^2(Sym_0(V)),  dim Sym_0(V)=65,
dim Sym^2(Sym_0(V))=2145.
```

Equivalently, with `W_x=wedge^2(P_x)` acting on the 55-dimensional space
`wedge^2(V)`,

```text
k_xy=tr(W_x W_y)=((g_xy)^2-h_xy)/2,
h_xy=(g_xy)^2+k_xy                    in F_3.
```

Here `W_x` is an operator, not a vector of dimension 55.  It is
self-adjoint and has trace `binomial(6,2)=15=0` in `F_3`, so its valid
trace-Gram ambient is the 1539-dimensional trace-zero subspace of the
1540-dimensional self-adjoint operator space on `wedge^2(V)`.

## Graph-forced nonedge constraints

For a nonedge `xy`, label its two common neighbors first in both stars.
The matching two cross-Gram entries equal one because the corresponding
triangle blocks intersect.  Every other entry is the number of graph edges
between two disjoint triangles, reduced modulo three.

For disjoint triangles, the local `lambda=1, mu=2` inequalities leave 52
of the 512 bipartite cross-edge masks.  Their edge-count distribution is

```text
0: 1, 1: 9, 2: 36, 3: 6.
```

The six three-edge masks are exactly the perfect matchings, hence exactly
the induced triangular-prism cross patterns.  Under `P=0`, every disjoint
cell therefore has the integer value `0`, `1`, or `2`.

Counting against the seven triangles through the opposite center gives
the exact integer row and column margins

```text
(9,9,6,6,6,6,6).
```

The first two totals include the intersecting entry one; before adding it,
their disjoint-cell crossing total is eight.  These margins imply the
required zero row and column sums modulo three.

Three explicit matrices in the checker satisfy all these frozen local
premises, have union Gram rank 11, have 14 locally projectively distinct
columns in the resulting nondegenerate 11-space, and have the same
`g_xy=2`, but have `h_xy=0,1,2`.  They are only relaxed local controls.
Thus the listed local premises do not determine a nonedge fourth trace;
a further graph-specific/global compatibility invariant is necessary.

## Hostile kernel rule

For any column realization with span dimension `r` and Gram rank `q`,

```text
dim(radical of the span)=r-q,
r-q <= 11-r.
```

A coefficient word in the Gram kernel need not be a true column relation.
The checker builds an exact two-star control with union Gram rank 9 and a
rank-10 realization in an 11-dimensional nondegenerate space.  Its Gram
kernel has dimension five while its true-relation space has dimension four;
the remaining word maps to a nonzero radical vector.  No proof step may
replace a true relation by an unchecked Gram-kernel word.
