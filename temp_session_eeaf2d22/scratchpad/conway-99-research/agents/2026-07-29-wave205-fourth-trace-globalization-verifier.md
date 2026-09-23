# Wave 205 fourth-trace globalization verifier

```yaml
role: verifier
date_utc: 2026-07-29T20:31:05Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: VERIFIED
scope: >-
  Independently verify the sealed Wave 205 nonedge, global fourth-moment,
  and hostile-control packages after first sealing a source-blind algebra
  and radical-guard implementation.
inputs:
  attempts/wave205-nonedge-fourth-trace-proof-a/package-manifest.sha256: 2c9976b6cb07a3036df07fd0e7ceb7ffce6a339651d604fcecdcf8c0c3da3d96
  attempts/wave205-global-fourth-moment-proof-b/package-manifest.sha256: a91a2a1cdbc129fa66e9d63b34031a774d5af78c458d18d9a1aadd7e4be217e7
  attempts/wave205-fourth-trace-hostile-controls/package-manifest.sha256: b9700d135bbfdebc34aeaad88eb1264b95732fa0f9da773cf90bd002331cc971
  verification/wave205-fourth-trace-globalization-verifier/SOURCE_BLIND_FREEZE.sha256: f8fb87d76c5eda2ff2569ec49a935b8bdb4022671f6d51f2752c14e153bcc853
method: >-
  Source-blind exact F_3 derivation; hostile Gram-radical realization;
  independent post-source census and JSON-certificate reconstruction that
  imports no discovery Python; separate discovery replay and mutation tests.
command: >-
  python -B -m unittest -v
  verification/wave205-fourth-trace-globalization-verifier/test_independent_verifier.py
  verification/wave205-fourth-trace-globalization-verifier/test_post_source_audit.py
outputs:
  verification/wave205-fourth-trace-globalization-verifier/audit.md: see package manifest
  verification/wave205-fourth-trace-globalization-verifier/post_source_result.json: see package manifest
  verification/wave205-fourth-trace-globalization-verifier/package-manifest.sha256: sealed package
limitations:
  - The Proof-A controls are local 28-vertex controls, not global target graphs.
  - The Proof-B first-moment control repeats projector labels.
  - The stronger hostile controls fail projective distinctness and the target lambda/mu laws.
  - Literature novelty and completeness were not independently certified.
  - No endpoint or Conway-99 status changes.
```

## Verdict

`VERIFIED_WITH_SCOPE_NO_FINDING`.

The independent source-blind freeze was sealed at

```text
f8fb87d76c5eda2ff2569ec49a935b8bdb4022671f6d51f2752c14e153bcc853.
```

After source exposure, all three package manifests and their entries matched.
The independent checker reproduced:

- Proof A: the forced nonedge corner/profiles, `t>=6`, average `t=7`,
  `g=2t`, normalized counts 646 and 7,886, admissible counts
  `[0,18,0]` and `[297,324,144]`, and all four 28-vertex controls;
- Proof B: `H=U K_D U^T`, `rank(U)=99`, the row-localizer and `w_TU`
  contractions, the correct operator dimensions, and the scoped
  zero-first-moment countercontrol; and
- hostile controls: exact 99-projector/231-column/incidence coupling,
  rank-11 square-zero Grams, full pair-trace agreement, edge fourth-trace
  agreement, and 3,888 ordered nonedge fourth-trace differences.

The package replays passed.  Pytest itself was unavailable for the hostile
wrapper, but its six plain test functions were invoked directly and all
passed; the independent checker separately reconstructed the certificate.

No mathematical or scope discrepancy was found.

## Promoted boundary

```text
pair-local premises force t>=7:                REFUTED_WITH_SCOPE
fixed t=7 and listed pair data determine h:    REFUTED_WITH_SCOPE
sum_x P_x=0 generically forces H 1=0:           REFUTED_WITH_SCOPE
fourth-trace factorization/localizers:           VERIFIED
rank(U)=99 and tensor dimensions:                VERIFIED
stronger 99x231 hostile control predicates:      VERIFIED_RELAXED_CONTROL
actual nonedge h classification:                 UNKNOWN
rank-11 endpoint / n3=4158 / Conway-99:           UNKNOWN
```

The exact next missing invariant is global: simultaneous 99-center
extension compatibility, equivalently graph-specific control of the
restriction of `K_D` to `row(U)`, the Hadamard localizers
`Q o (D S_x D)`, or the vectors `w_TU=B(D_T o D_U)`.
