# Wave 204 orchestrator decision

```yaml
role: orchestrator
date_utc: 2026-07-29T19:28:41Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: VERIFIED
scope: >-
  Integrate the Wave 204 literature/hostile-control, block-holonomy,
  and projector-fourth-order lanes only after independent source-blind
  verification; preserve every relaxed-control and target boundary.
inputs:
  verification/2026-07-29-wave204-preflight.md: a370554f8f21231cf6349f6be8bf760f7aba1e4a927df19996b73400f0e0346c
  attempts/wave204-literature-hostile-controls/package-manifest.sha256: b725463de29c60e14094de5b4f58c2051e5db5657b3f47772efbbd461cc187a9
  attempts/wave204-global-slot-holonomy-proof-a/package-manifest.sha256: e060f0f39c2b66b6b64a20694a2a6505f229cd85c7784374976e39cdba61dd84
  attempts/wave204-projector-fourth-order-proof-b/package-manifest.sha256: 6074ec95b7a92cdf26626a031c9373fa94ccd3ab47c627d31183a64af0bdc181
  verification/wave204-global-compatibility-verifier/SOURCE_BLIND_FREEZE.sha256: 88f502d4d49f6866a73bff006097f66cf4eefb36b3cdf0eca24280df1d70f7a2
  verification/wave204-global-compatibility-verifier/package-manifest.sha256: 48cd018c7f7cebe7f2bc93a6dbd9440422f8dc843bc6c0fa96b29968e440f9c2
method: >-
  Freeze and replay the inherited boundary; commission disjoint literature,
  proof-A, and proof-B lanes; require a verifier that did not rely on
  discovery internals; replay all independent tests at the repository root;
  compare scopes premise by premise; and promote only claims accepted by
  the verifier.
command: >-
  From verification/wave204-global-compatibility-verifier:
  ..\..\.venv\Scripts\python.exe -B -m unittest -v test_independent_verifier.py;
  ..\..\.venv\Scripts\python.exe -B independent_verifier.py;
  ..\..\.venv\Scripts\python.exe -B -m unittest -v test_post_source_replay.py;
  ..\..\.venv\Scripts\python.exe -B post_source_replay.py
outputs:
  - verification/2026-07-29-wave204-integration-audit.md
  - verification/2026-07-29-wave204-orchestrator.md
  - logs/2026-07-29-wave204-public-checkpoint.json
limitations:
  - The V1 countermodel is a relaxed local-incidence skeleton, not an SRG.
  - The V2 controls are local rank-11 orthogonal configurations, not an endpoint.
  - The V3 detector is conditional and adjacent-pair only.
  - The optional 99-projector controls were not independently reconstructed before source exposure.
  - No rank-11 exclusion, endpoint exclusion, strict n3 improvement, graph/code construction, Conway-99 resolution, novelty, or priority claim follows.
```

## Decision

Promote with exact scope:

- `VERIFIED`: the V1 relaxed certificate predicates;
- `REFUTED_WITH_SCOPE`: the listed local interface forces `b>0`;
- `VERIFIED`: true triangle-block gains telescope because they are `dz`;
- `REFUTED_WITH_SCOPE`: Wave 203 partial slots force center chaining;
- `REFUTED_WITH_SCOPE`: one-point partial slots determine total `S_5`
  monodromy;
- `VERIFIED`: the conditional adjacent fourth-order detector;
- `REFUTED_WITH_SCOPE`: pair trace plus intersection dimension determines
  fourth trace.

Quarantine:

- optional V3 99-projector controls as
  `SOURCE_REPLAYED_SCOPED_RELAXED`;
- every inference from a relaxed control to a target graph;
- every claim beyond the focused literature search.

Retain:

```text
Conway-99:              UNKNOWN
rank-11 endpoint:       UNKNOWN
n3=4158 endpoint:       UNKNOWN
rigorous n3 interval:   708<=n3<=4158
conditional Q bound:    Q>=7059
Q>=7060:                NOT PROVED
```

## Continuation

Do not spend the next wave trying to repair center holonomy from the same
partial slot data. Instead classify nonedge fourth traces and seek a full
graph-specific identity for `(h_xy)`. Any claimed contradiction must include
the actual 99-star/231-column/SRG premises and receive a new independent
verifier.
