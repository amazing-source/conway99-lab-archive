# Wave 205 literature and hostile-construction lane

```yaml
role: literature
date_utc: 2026-07-29T19:59:12Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: CANDIDATE
scope: primary-source audit plus exact relaxed controls for nonedge fourth traces under progressively stronger endpoint-shaped premises
inputs:
  - attempts/wave205-fourth-trace-globalization/protocol.md sha256 a1d45fc0a82b9944a9e020ded3945e75944e0e00202eacbb20eb05598e30bf4d
  - verification/wave204-global-compatibility-verifier/package-manifest.sha256 sha256 48cd018c7f7cebe7f2bc93a6dbd9440422f8dc843bc6c0fa96b29968e440f9c2
  - verification/2026-07-29-wave204-orchestrator.md sha256 7760a4c5a4b6a501262bbb3b061828725cd23c6837fd724fada84d94a3124edd
  - attempts/wave204-projector-fourth-order-proof-b/exact_check.py sha256 2aa6e2560e0e03c41ea202f2c2550bb3c6aa35436a27a0ccaa27becee297dfff
  - attempts/wave204-projector-fourth-order-proof-b/exact-results.json sha256 008b098012807fa98a3874df641575c49e7030e120e4417c8eada153c792b151
method: theorem-by-theorem primary-source hypothesis audit; self-contained reconstruction of frozen local projectors; new cyclic seven-factorized linear triple incidence; exhaustive exact F_3 matrix and graph checks
command: python attempts/wave205-fourth-trace-hostile-controls/exact_check.py --verify-results attempts/wave205-fourth-trace-hostile-controls/exact-results.json --verify-certificate attempts/wave205-fourth-trace-hostile-controls/certificate.json; python -m pytest -q attempts/wave205-fourth-trace-hostile-controls/test_exact_check.py
outputs:
  - attempts/wave205-fourth-trace-hostile-controls/certificate.json sha256 c169abfcc1ebe0cbb4d0d811307eac284c52e95c751b18677afe77f54bf52ec6
  - attempts/wave205-fourth-trace-hostile-controls/derivation.md sha256 cd36b734ec9d05827ba06c1423754ecb0f3c903b690dc5f62883f3b5baee460b
  - attempts/wave205-fourth-trace-hostile-controls/exact_check.py sha256 b6b9308203191f17d3c05304dabcc55e4b0c70799c53e9b33f570616395f5013
  - attempts/wave205-fourth-trace-hostile-controls/exact-results.json sha256 5b536f035be16167b24d33c1b4dbdca9bf970ff50bab08096c868a2dd9e138bd
  - attempts/wave205-fourth-trace-hostile-controls/literature-audit.md sha256 fc8471096f1abcec30da2ee762efeee72299039a5d21f996fea4fd6b49d17d55
  - attempts/wave205-fourth-trace-hostile-controls/literature-sources.json sha256 cc1c3fa03dc92a05a99e85e09cf1683157b3f3dced50861305e947b19fea95d2
  - attempts/wave205-fourth-trace-hostile-controls/README.md sha256 4f544747d6f2e1798e8bfb0809cae02651baea5c8307d17496e4c7d751668d6d
  - attempts/wave205-fourth-trace-hostile-controls/test_exact_check.py sha256 2fb322b03fa42ede9b5f22a546f5f2d4a09b2a3e4f07a5e7b6f2a8d7e02ed799
  - attempts/wave205-fourth-trace-hostile-controls/package-manifest.sha256 sha256 b9700d135bbfdebc34aeaad88eb1264b95732fa0f9da773cf90bd002331cc971
limitations: relaxed controls use 21 projective directions; point graph is disconnected and violates lambda=1 and mu=2; no selected-orthogonality, outer-cycle, prism-free, code-distance, or cover premise; literature non-discovery is bounded; no target claim is verified
```

## Result

The construction gives two exact labelwise systems over `F_3` with:

- a nondegenerate ambient dimension 11;
- 99 rank-six trace-zero self-adjoint idempotents;
- 231 labelled singular columns and rank-11 square-zero centered Gram;
- exact seven-column simplex coupling at every star;
- a binary linear `99 by 231` triple incidence of row degree 7 and column
  degree 3;
- a simple 14-regular point graph with
  `BB^T=A+7I` over the integers and `BB^T=A+I` over `F_3`;
- identical full matrices `g_xy=tr(P_xP_y)`; and
- identical `h_xy=tr(P_xP_yP_xP_y)` on all 693 point-graph edges.

Nevertheless the two `h` matrices differ in exactly 3,888 ordered entries,
all of which are nonedges.

The new part is the cyclic incidence and its exact coupling to the local
projector simplices. The local matrices themselves are reconstructed from the
frozen Wave 204 formulas; this report does not relabel them as an independent
rediscovery.

## Exact failure ledger

The control still fails the target in every decisive graph-specific way:

1. Only 21 projective directions occur among 231 labels.
2. The point graph has components of orders `27,36,36`.
3. It has 1,329 graph triangles, 1,098 beyond the designated 231 blocks.
4. Edge common-neighbor counts have distribution
   `4:144,5:243,6:27,7:225,8:27,9:27`, not `lambda=1`.
5. Nonedge common-neighbor counts have distribution
   `0:3240,2:144,4:180,5:27,6:315,7:27,8:225`, not `mu=2`.
6. The selected 32-regular orthogonality relation, actual adjacent
   outer-cycle modules, prism-free endpoint statistic, code distance, and
   cover constraints are absent.

It is therefore a relaxed construction-level compatibility blueprint, not a
graph, code, cover, endpoint, construction, or nonexistence certificate.

## Literature verdict

The theorem audit found no applicable fourth-moment globalization theorem:

- Greaves--Iverson--Jasper--Mixon Proposition 3.5 transfers the vector-frame
  identity `G^2=cG` after spanning is checked, but does not control rank-six
  projector fourth moments.
- Bachoc--Ehler Theorems 5.3 and 5.7 require real positive weights,
  compact-Grassmannian integration, and a proved `p=2` fusion/design or
  strength-4 cubature premise.
- Roy's Grassmannian association-scheme results require complex design,
  angle-class, and annihilator-polynomial hypotheses.
- Adriaensen--De Boeck Theorem 4.18 concerns relations on a full orbit of
  anisotropic points of a quadric, not an arbitrary 99-set of six-spaces.
- trace Cayley--Hamilton identities for one matrix do not reduce the mixed
  word `tr(ABAB)` to `tr(AB)`.

The correct unconditional quadratic-lift coordinate space has dimension
`dim Sym^2(F_3^65)=2145`, so it gives only the vacuous bound
`rank(H)<=99`. The tempting `55` bound is invalid because
`wedge^2(P_x)` is an operator on a 55-space, not a vector with 55 operator
coordinates.

The latest primary source located in the audit was submitted
2026-04-24 and reports a SAT non-resolution. The evidence supports retaining
`Conway-99: UNKNOWN`; it does not establish that no later announcement exists.

## Verification request

This lane does not promote its own construction. A fresh verifier should:

1. freeze the protocol and input hashes before opening this package;
2. independently generate or replay the 231 triples and check linearity,
   degrees, colors, `BB^T`, graph statistics, and component structure;
3. independently reconstruct all projectors and star columns;
4. check the two full `99 by 99` `g` and `h` matrices; and
5. confirm that every fourth-trace difference is a nonedge and that every
   failed target premise remains explicit.
