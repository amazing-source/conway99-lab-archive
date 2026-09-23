# Waves 60--63 alternative-space integration audit

```yaml
role: orchestrator
date_utc: 2026-07-27T22:20:38Z
git_commit: 81c8d45426938ea8490af55d81f05b7c2ad99035
claim_label: VERIFIED
scope: conditional integration of the kappa=3 component, finite-field, one-root invariant-SDP, and rational pair-cone results at n3=4158
inputs:
  - path: logs/2026-07-27-wave59-public-checkpoint.json
    sha256: 12175e98e1aba3c7b2d79f319d37cc7ad07f6ffe9313c68fbe9cd1bed98fa424
  - path: attempts/wave60-c3-incidence-design/package-manifest.sha256
    sha256: ccf35d05a4125178a7cb065b73972ef310584b14c6a447ea889f3b06a170629b
  - path: verification/wave60-c3-incidence-design/package-manifest.sha256
    sha256: 9bb26011e087e8f127d2a830635ebeecdae3da72d31e69b6e31f73d7513e3f2f
  - path: attempts/wave61-c3-finite-field/package-manifest.sha256
    sha256: 63343515a1abd1e053e4fed84de0ba88d9c53833994a8ac08d4325520b83c252
  - path: verification/wave61-c3-finite-field/package-manifest.sha256
    sha256: f2ffa83a03772af8f8aa3ecf5e17459eaaa24f8c566474c61b81dd004f587cc9
  - path: attempts/wave62-terwilliger-sdp/package-manifest.sha256
    sha256: d62af7171cd825001c8bce4b9b1502970718640f5c441164eb49d4e59ba26401
  - path: verification/wave62-terwilliger-sdp/package-manifest.sha256
    sha256: 439bd26e463ae19ce7cbac9989b23a681236d7a1df623005e5a829e5f8957968
  - path: attempts/wave63-c3-integer-cone/package-manifest.sha256
    sha256: c85f9dcf3d0bdba2a41299c4a3c4fdd8c9802903cff04ab237f40d9840df6018
  - path: verification/wave63-c3-integer-cone/package-manifest.sha256
    sha256: 3c19b9c226e141850a7763467c1eb7e19a15752dac03cdca9f6a4b7cb3dae017
method: enforce discovery-verifier separation, replay every exact finite claim, retain verifier corrections, and preserve the unresolved integer and endpoint walls
outputs:
  - verification/2026-07-27-wave63-integration-audit.md
  - verification/2026-07-27-wave63-orchestrator.md
  - logs/2026-07-27-wave63-public-checkpoint.json
limitations:
  - every result is conditional on the prism-free endpoint and several are restricted relaxations
  - neither rational nor invariant-SDP feasibility constructs a graph
  - no endpoint case is closed and no strict upper bound below 4158 follows
```

## Verdict

`PASS_SCOPED_WITH_CORRECTIONS`.

Four independent verifiers reconstruct the finite claims. Wave 60 passes
without a mathematical correction. Wave 61 receives a narrow scope
correction: its cubic margin identity and scalar totals pass, but it did not
test nonnegative integral tensor feasibility. Wave 62 receives a count
clarification: the declared nontrivial scan has 1,949 matrices because the
tautological `(E0,0,0)` matrix is deliberately skipped; including it still
produces no negative block. Wave 63 passes with zero mathematical mismatches.

## Accepted component and finite-field boundary

The three-component lane has 18 fibre-preserving component types, 1,140
unordered triples, 275 safe simultaneous-coordinate orbits, and
15,936--27,200 individually allowed columns per triple. The exact binary
target-rank histogram is

```text
14:67, 16:415, 18:412, 20:185, 22:51, 24:10.
```

No binary-rank, within-component, full-pair, pattern-parity, quadratic/Witt,
or stated odd-prime screen eliminates a triple. This verifies a failure of
those relaxations, not existence of any incidence design.

## Accepted invariant-SDP boundary

The 84 signed-edge scaffold has valencies `[1,2,1,20,20,40]` and primitive
multiplicities `[1,6,7,14,21,35]`. Every integer endpoint parameter
`y=0,...,42` survives the exact invariant projector SDP. The nontrivial
degree-24 Schur census contains 23,388 exact scalar blocks:

```text
positive: 23,316
zero:         72
negative:      0.
```

This is an exact null result only for the averaged one-root family.

## Accepted rational-cone boundary

The fixed 74-lane subset contains 82 declared memberships with eight overlaps
removed. Its verifier independently reconstructs every allowed six-set and
checks all `74*630=46,620` pair equations with rational arithmetic. Every
certificate has total weight 60 and coefficients in `(0,1]`. Support sizes
438--462 match the corresponding full-pair binary generator ranks.

The certificates are fractional. They do not settle semigroup membership,
zero-one feasibility, third-order realizability, compatibility with `A_Y`, or
the endpoint.

## Promotion boundary

```text
Waves 60--63 finite conditional claims:           VERIFIED SCOPED
Wave 61 cubic tensor feasibility:                  NOT TESTED
Wave 62 negative invariant blocks:                0
Wave 63 integer designs:                           0
simultaneous B and compatible A_Y:                 UNKNOWN
strict upper bound below 4158:                     NOT PROVED
rigorous interval:                                 708 <= n3 <= 4158
endpoint / graph / Conway-99 / novelty:            UNKNOWN
```
