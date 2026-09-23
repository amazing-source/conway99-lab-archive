# Wave 47 three-root moment verifier report

```yaml
role: verifier
date_utc: 2026-07-27T17:50:14Z
git_commit: e4394aa9172fa97a6dafa9158148c2183603a01b
claim_label: VERIFIED
scope: >-
  Clean-room exact reconstruction of all eight pointwise-labelled
  three-vertex-root flag families through union order seven, both direct
  known-graph controls, all 17 immutable witness matrices, all 2664 supplied
  exact negative directions, and all 2657 deduplicated primitive cuts.
inputs:
  - path: attempts/wave47-three-root-moment/compact-handoff.json
    sha256: 8b74110bc6ae983e288d448cd1a963f81521f178e8280bbbf5864274a1639a47
  - path: attempts/wave47-three-root-moment/package-manifest.sha256
    sha256: 3fee6bf5ec42c5b70138f508ba3fbff6b44b56870601ea25111cd7da93473737
  - path: attempts/wave47-three-root-moment/coefficients.json
    sha256: 07b55f06ff8f7d5f2de53d92a3222366e122a7306028752ecd31c10962a824b3
  - path: attempts/wave47-three-root-moment/results.json
    sha256: a58d04b56ed66094536ffc158b32085e3e940e5c3e42a3983a471e95e99daf37
  - path: attempts/wave47-three-root-moment/cuts.json
    sha256: d2ea38ed74a1b9098c9cc8eae52f8d65723c2631335b0acedba647dc16aa313e
method: >-
  Exhaust every labelled simple mask through order seven under the local
  common-neighbor caps, quotient by complete vertex-permutation orbits,
  fix all three root labels pointwise while quotienting only the free pair,
  count all ordered root embeddings and ordered flag pairs, compare direct
  and expanded Gram controls, reconstruct lower decks by exact deletion
  identities, and replay every direction and primitive cut with integer
  arithmetic. No discovery implementation was imported or called.
command: >-
  .\.venv\Scripts\python.exe
  verification\wave47-three-root-moment\verify.py
outputs:
  - path: verification/wave47-three-root-moment/verification-results.json
    sha256: 1c80d2b70b8e6bef42d4d9df124cc82dc9baf642d36873c61e91e8f2acc99a43
  - path: verification/wave47-three-root-moment/verify.py
    sha256: 2a9401e1f34a736f4b75ba2a010bcbd653218b835358eb2d44735d69405d3e1b
  - path: verification/wave47-three-root-moment/test_verify.py
    sha256: b854104c9119bc544b467b36cad1c426d9fe3344c268ef0d0d26fa1a849bca85
  - path: verification/wave47-three-root-moment/verification-report.md
    sha256: b6e77985b169d9b7d5ba42b7b98aad805e5ffdbf75ac46405ef59a20a494900a
limitations:
  - The exact cuts reject only their 17 recorded aggregate source vectors.
  - The full PSD-constrained integer count region was not searched.
  - A surviving aggregate vector would not construct a graph.
  - Five matrices have additional small float-negative modes below a backward-error threshold but outside the sealed relative reporting cutoff; exact supplied directions all pass.
  - Endpoint n3=4158, a strict upper bound, graph construction, novelty, priority, and Conway-99 remain UNKNOWN or NOT_PROVED.
```

The independent labelled class counts are 683, 13,174, and 394,020, reducing
to exact unlabelled streams of 21, 62, and 208.  Flag dimensions are
`64,56,56,42,56,42,42,20`; all 57,006 nonzero upper-triangle coefficient
entries reproduce the sealed coefficient payload.

All 48 external `S3` root-order mappings pass.  Petersen and Clebsch give
exact direct-versus-expansion equality for all eight families.  Every one of
the 136 witness matrices matches its sealed hash and exact all-ones
normalization.  All 2,664 supplied integer quadratic values are strictly
negative and exact.  Primitive reconstruction produces the sealed list of
2,657 cuts exactly, with seven repeated source vectors correctly removed.

The minimum observed free physical memory was 55.34%, above the required
20% verifier floor.  Six unit tests and post-run record validation passed.

Verdict: publish only the finite Wave 47 construction and recorded-witness
refutations as `VERIFIED_SCOPED`.  Preserve every global status wall.
