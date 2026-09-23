# Waves 53--55 integration audit

```yaml
role: orchestrator
date_utc: 2026-07-27T20:45:00Z
git_commit: a4a61658356253fb95cf68252c972a4f79df38fe
claim_label: VERIFIED
scope: corrected integration of the endpoint proof cover, two-root coherent lift, exact rational cut loop, ordinary ternary enumerator, and bounded branch-15 continuation
inputs:
  - path: attempts/wave53-proof-cover/package-manifest.sha256
    sha256: b6b5c0de2290e1ed68c42f0ca63328025c456655ebe6328896a97100d08a0c38
  - path: verification/wave53-proof-cover/package-manifest.sha256
    sha256: d7b363449397315773a910caba1cdd0a17151576c27c8175de6ace386a1231f8
  - path: attempts/wave53-multi-root-wl/package-manifest.sha256
    sha256: 78b4ef6fd50a3c7e7dbde0b1ce0b13efb3570b22396d9ab0b21aa24ec77d1d03
  - path: verification/wave53-multi-root-wl/package-manifest.sha256
    sha256: 2fd2f932ea427db817a60b26cc569fbf573cd41eb93d2607099ee4968c7dad80
  - path: attempts/wave53-exact-cut-loop/package-manifest.sha256
    sha256: b4a8f2215c61dcf01469665401f966bebede73ff6466873df3c03f51e5fdd25e
  - path: verification/wave53-exact-cut-loop/package-manifest.sha256
    sha256: 68516589bf504b0720c536b4e43846107c359291d9ae44bd651e99938cd62e58
  - path: attempts/wave54-centered-enumerator/package-manifest.sha256
    sha256: 4e6fa530dee3c30be6423d9b08f87e6389a59f20d972a5df999ca97541a2db23
  - path: verification/wave54-centered-enumerator/package-manifest.sha256
    sha256: a6254c7121d55b6372dccfc444b171c50d58392c15ef571df809d5358bd53abb
  - path: attempts/wave55-branch15-remainder-search/package-manifest.sha256
    sha256: 4ab349a92de45428071a4f6d12ac64d9c74777079a6e0d0a328f76598f61784e
method: independent exact reconstruction, proof-tool status replay, hostile tests, manifest rehash, correction-ledger enforcement, and claim-scope audit
outputs:
  - verification/2026-07-27-wave55-integration-audit.md
  - verification/2026-07-27-wave55-orchestrator.md
  - logs/2026-07-27-wave55-public-checkpoint.json
limitations:
  - the 33-case cover is conditional on n3=4158 and has zero checked complete-case contradictions
  - local cap controls and aggregate rational or enumerator witnesses are not graphs
  - the Wave 55 solver run is nonterminal and proves no formula consequence
```

## Verdict

`PASS_WITH_MATERIAL_CORRECTION`. The proof-cover, multi-root, and ordinary
enumerator claims reproduce at their stated finite scopes. The fixed
174-to-177-cut rational sequence is exactly feasible and the three retained
Wave 49 cuts are valid. The cut-loop discovery's universal matrix headline is
not.

Integration removed one terminal blank line from the proof-cover protocol and
the exact-cut verifier README, then resealed the affected hashes. This was a
presentation-only normalization; no code, exact result, audit verdict, test
record, or mathematical status changed.

## Accepted exact results

- The normalized endpoint cover has 10,395 states and 78 refined orbits. Its
  33 compatible cases have total orbit weight 6,644; the 45 incompatible
  orbits have weight 3,751.
- Conditional case coverage is `33/33`, but checked complete-case UNSAT
  coverage is `0/33`.
- `branch15 AND x187=0` is the exact complementary shard to the checked
  `x187=1` result. Both retained bounded runs on it end nonterminal.
- The two-root relations have common-`K` counts `5,2,1,0` and stable
  `(2-WL, folklore 3-WL)` counts
  `K=(285,107), B=(584,321), C=(321,240), D=(63,61)`.
- The one shared `B` candidate is forced true under the prism-free scope.
  All four merged local cap systems retain exact positive controls.
- All four cut-loop rational witnesses satisfy all 170 base equations,
  cumulative cuts, bounds, and nonnegativity. The support sequence is
  `136,132,136,138`; retained new cuts are Wave 49 roots `220,62,221`.
- The formal ordinary ternary enumerator
  `{0:1,18:2,144:53316,153:19798,159:98496,162:5072,198:462}`
  satisfies the frozen exact integral MacWilliams system.

## Material correction

The cut-loop discovery treated an already-full symmetric Wave 45 coefficient
stream as an upper triangle and doubled off-diagonal entries. Independent
reconstruction finds:

```text
tested matrices:                         128
exactly indefinite:                      120
positive semidefinite Wave 45 matrices:    8
reported Wave 45 direction values wrong:  12
candidate records / unique rows:        32 / 28
corrected unique rows rejecting source:     25
```

The exact fourth dense-cut terminal value is positive. Its floating
`7.431e-10` residual is not an exact Farkas certificate. The affected
`128/128` headline and direction metadata are `REFUTED`; corrected fixed
177-cut feasibility remains `VERIFIED SCOPED`.

## Promotion boundary

```text
conditional endpoint case cover:           VERIFIED 33/33
complete-case terminal proof coverage:      0/33
two-root finite CSP/WL claims:               VERIFIED SCOPED
root relations excluded:                     NONE
fixed 177-cut rational feasibility:          VERIFIED SCOPED
128/128 moment matrices indefinite:          REFUTED
formal ordinary ternary enumerator:          VERIFIED SCOPED
Wave 55 bounded search:                      UNKNOWN / NO EVIDENCE
strict upper bound below 4158:               NOT PROVED
rigorous interval:                           708 <= n3 <= 4158
endpoint / graph / Conway-99 / novelty:      UNKNOWN
```
