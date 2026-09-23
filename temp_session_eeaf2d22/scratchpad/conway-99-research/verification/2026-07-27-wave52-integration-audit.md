# Wave 52 integration audit

```yaml
role: orchestrator
date_utc: 2026-07-27T19:31:19Z
git_commit: 30e8eab5b718bd59a161e6d43dfc1d7671d2f3bb
claim_label: VERIFIED
scope: automorphism-free one-root coherent closure and completion-free cap-incidence 2-WL
inputs:
  - path: attempts/wave52-coherent-closure/package-manifest.sha256
    sha256: 4b25853eca8ed96f5beea74e4e51ef744259a8436510d23c443b8e3f140692b3
  - path: verification/wave52-coherent-closure/package-manifest.sha256
    sha256: 37c0e3c6250e2cece2cc42b5e7c763750eab86c3cad0dd803179e76f045ee1f6
method: frozen discovery package, clean-room derivation, exact 2-WL replay, exhaustive profile comparison, hostile mutations, and scope audit
outputs:
  - verification/2026-07-27-wave52-integration-audit.md
limitations:
  - scope is one root and its forced local cap template
  - canonical cycle profiles are diagnostics, not all labelled joint completions
  - no graph, endpoint exclusion, improved upper bound, novelty, or priority claim is promoted
```

## Verdict

`PASS_SCOPED_NULL_OBSTRUCTION`. The verifier reproduces every stated local
derivation and finite refinement. The retained completions show that this
scope supplies no coherent-configuration obstruction.

## Accepted exact results

- One root triangle has 18 other incident triangles in three six-petal
  sectors, with local intersection graph exactly `3K6`.
- Global triangle-pair valencies in order `(I,K,D,C,B)` are
  `(1,18,32,144,36)`.
- Every petal has cross-sector degrees `B=2`, `C=4`, and `D=0`.
- The 19-node partial object has stable 2-WL trajectory `[6]`.
- The 163-node completion-free cap-incidence object has trajectory
  `[26,38,47]` and diagonal classes `[1,18,36,108]`.
- All stable intersection parameters are exact integers.
- All 64 canonical triples of bipartite two-factor cycle profiles satisfy the
  exact-two caps. They give 39 distinct stable fingerprints and color counts
  from 8 through 361.
- Independent and discovery computations agree on all 64 profiles and all
  4,096 fingerprint-equivalence decisions.
- Five hostile mutations are rejected.

## Meaning

The partial closure distinguishes semantic roles but forces no petal, cap, or
candidate truth assignment. Explicit integral local completions survive.
Choosing `B/C` edges before refinement produces colors that depend on that
arbitrary choice, so those colors are not forced endpoint relations.

The next coherent route must retain compatibility across multiple roots or
move to a genuine three-tuple/quadruple lift. This finite null result neither
supports nor refutes existence of a Conway graph.

## Promotion boundary

```text
one-root structure and 2-WL replay:       VERIFIED SCOPED
local cap integrality obstruction:        NONE
forced completed coherent quotient:       NONE
multi-root / three-tuple compatibility:   UNKNOWN
endpoint proof coverage:                  0/33
strict upper bound below 4158:            NOT PROVED
rigorous interval:                        708 <= n3 <= 4158
endpoint / graph / Conway-99 / novelty:   UNKNOWN
```
