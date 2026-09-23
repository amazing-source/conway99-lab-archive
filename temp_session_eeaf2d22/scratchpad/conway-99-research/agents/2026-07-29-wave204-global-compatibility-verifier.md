# Wave204 global-compatibility independent verifier

```yaml
role: verifier
date_utc: 2026-07-29T19:18:24Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: VERIFIED
scope: >-
  Independently verify the exact relaxed V1 certificate, the V2
  fixed-column coboundary and scoped failures of center-walk/total-S5
  implications, and the V3 conditional adjacent fourth-order detector;
  preserve all missing SRG, global-column, graph/code, cover, endpoint,
  and Conway-99 premises.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  attempts/wave204-literature-hostile-controls/package-manifest.sha256: b725463de29c60e14094de5b4f58c2051e5db5657b3f47772efbbd461cc187a9
  attempts/wave204-global-slot-holonomy-proof-a/package-manifest.sha256: e060f0f39c2b66b6b64a20694a2a6505f229cd85c7784374976e39cdba61dd84
  attempts/wave204-projector-fourth-order-proof-b/package-manifest.sha256: 6074ec95b7a92cdf26626a031c9373fa94ccd3ab47c627d31183a64af0bdc181
  verification/wave204-global-compatibility-verifier/SOURCE_BLIND_FREEZE.sha256: 88f502d4d49f6866a73bff006097f66cf4eefb36b3cdf0eca24280df1d70f7a2
method: >-
  Freeze an independent protocol, deterministic constructions, exact F3
  checker, hostile mutation tests, results, and hashes before source
  exposure; validate all submitted manifests and declared replays; then
  perform a separate JSON-level replay that imports no submitted Python
  and records every blind/source semantic discrepancy.
command: >-
  python -m unittest -v test_independent_verifier.py;
  python independent_verifier.py;
  python -m unittest -v test_post_source_replay.py;
  python post_source_replay.py
outputs:
  verification/wave204-global-compatibility-verifier/audit.md: eadad44ea0e7ac653defb7e5431c13b2ef06ae53eced0bbf6412f82fc3244c65
  verification/wave204-global-compatibility-verifier/blind_result.json: 2140d3979be0eafa0be3ba5cb354b02579989bd3b67e80a51b765c877cdd78e5
  verification/wave204-global-compatibility-verifier/post_source_result.json: a3369575a4aca8ec91edc08052b0c6ccfd1b0364ae3d84114573d7db9d883d8c
limitations:
  - V1 proves only existence of the explicit relaxed certificate and refutes only the frozen local-interface force-b-positive implication.
  - V2 controls omit 99 stars, 231 global columns, global frame, SRG incidence, cover totals, and endpoint realization.
  - V3 is a conditional adjacent-pair detector; nonedge fourth traces and global compatibility remain unknown.
  - The optional V3 99-projector controls were source-replayed but not independently reconstructed before source exposure, and remain quarantined as relaxed.
  - No rank-11 or endpoint exclusion, strict n3 improvement, graph/code construction, or Conway-99 resolution follows.
```

## Labels

- V1 exact relaxed certificate predicates: `VERIFIED`.
- V1 implication that the frozen local interface forces `b>0`:
  `REFUTED_WITH_SCOPE`.
- V2 fixed-column coboundary/telescoping identity: `VERIFIED`.
- V2 center-walk chaining and determined total-`S_5` implications:
  `REFUTED_WITH_SCOPE`.
- V3 conditional local fourth-order detector: `VERIFIED`.
- V3 implication that pair trace plus intersection dimension fixes fourth
  trace: `REFUTED_WITH_SCOPE`.
- Optional V3 global controls: `SOURCE_REPLAYED_SCOPED_RELAXED`, not promoted
  independently.

All 32 submitted manifest entries match.  Submitted V1/V2/V3 replays and
their 8/10/10 tests pass.  The source-blind suite passes 11/11 tests, and the
post-source independent JSON replay passes 5/5 tests.

