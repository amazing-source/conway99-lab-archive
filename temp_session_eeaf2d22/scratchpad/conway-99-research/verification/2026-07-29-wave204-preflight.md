# Wave 204 orchestrator pre-flight

```yaml
role: orchestrator
date_utc: 2026-07-29T19:04:00Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: DERIVED
scope: >-
  Reproduce the frozen Conway-99 boundary and the targeted Wave 201 and
  Wave 203 verifier packages before extending the rank-11 endpoint.
inputs:
  verification/wave201-multiplicity-weighted-fiber-loss-verifier/package-manifest.sha256: d08624de5a64c4a49ce5a9bd6a7c65cb36eeef17c736f83070a4d12f66473854
  verification/wave203-two-center-incidence-verifier/package-manifest.sha256: ee0d994825ad9b687fb29eb7bcde02c86dacbd78042edff2111bd9fb4bc7d0ab
method: >-
  Read the Wave 171--203 package indexes, replay the source-blind exact
  checkers and tests, recompute every targeted manifest entry, and retain
  provenance mismatches without treating them as mathematical evidence.
command:
  - >-
    .\.venv\Scripts\python.exe -B
    verification\wave201-multiplicity-weighted-fiber-loss-verifier\independent_check.py
    --verify
    verification\wave201-multiplicity-weighted-fiber-loss-verifier\independent-math-result.json
  - >-
    .\.venv\Scripts\python.exe -B -m unittest -v
    verification\wave201-multiplicity-weighted-fiber-loss-verifier\test_independent_check.py
  - >-
    .\.venv\Scripts\python.exe -B
    verification\wave203-two-center-incidence-verifier\independent_check.py
    --verify
    verification\wave203-two-center-incidence-verifier\independent-math-result.json
  - >-
    .\.venv\Scripts\python.exe -B -m unittest -v
    verification\wave203-two-center-incidence-verifier\test_independent_check.py
  - >-
    .\.venv\Scripts\python.exe -B
    verification\wave203-two-center-incidence-verifier\source_comparison_check.py
    --verify
    verification\wave203-two-center-incidence-verifier\source-comparison-results.json
  - >-
    .\.venv\Scripts\python.exe -B -m unittest -v
    verification\wave203-two-center-incidence-verifier\test_source_comparison_check.py
outputs:
  - verification/2026-07-29-wave204-preflight.md
limitations:
  - This is an orchestrator replay of already verified claims, not an
    independent verification of Wave 204 discoveries.
  - One historical bibliography input freeze is not byte-replayable from
    the current tree or committed SOURCES.bib history, as recorded below.
```

## Reproduced boundary

The following exact boundary passed current replay:

```text
n3+3P=4158
708<=n3<=4158
conditional rank-11 Q>=7059
edge-isolated projective circuits=693
conditional projective short circuits=7752
conditional nonzero scalar short-circuit words=15504
m_(x->y)+m_(y->x)<=5
3n3+4p3<=5|U|
epsilon>=5b
Q>=7060: not proved
```

The conditional and unrestricted scopes remain distinct.

## Targeted replay results

```text
Wave 201 source-blind replay:             PASS
Wave 201 tests:                           11/11 PASS
Wave 201 package manifest:                11/11 PASS
Wave 201 input freeze:                     3/3 PASS

Wave 203 source-blind replay:             PASS
Wave 203 independent tests:               11/11 PASS
Wave 203 source comparison:               PASS
Wave 203 comparison tests:                 5/5 PASS
Wave 203 package manifest:                15/15 PASS
Wave 203 input freeze:                     3/3 PASS
```

Focused supporting replays also passed for the Wave 176 star projectors,
Wave 178 edge-circuit injection, Wave 181 canonical quadrilateral, and
Wave 202 equality face. The Wave 171, 176, 178, 181, and 202 package
manifests and input freezes match the current checkout.

The conditional lower boundary `n3>=708` passed the current corrected Wave
23 independent and discovery test suites. The old pre-correction Wave 23
artifact manifest does not match the corrected files and is not used as the
current seal. The general prism identity passed the Wave 100 clean-room
suite and manifest.

## Retained Wave 175 provenance defect

The Wave 175 package manifest itself passes. Its input freeze records

```text
SOURCES.bib expected:
4e1dffa7e450593b129d9b05dbbabf7951fd1872da5fb7048700e00383425d2f

SOURCES.bib current:
8d521134cbc81e33d635db31063a7004d7c4c9135b9b7ea550b088e6b3aa5dde
```

The expected bibliography bytes are not present in the committed
`SOURCES.bib` history, so that one historical input cannot be reproduced
byte-for-byte. The cited Blokhuis--Moorhouse primary entry remains present
in the current bibliography, and the Wave 175 scoped mathematical package
is intact. This is a provenance limitation, not evidence for or against its
finite-polar formulas.

