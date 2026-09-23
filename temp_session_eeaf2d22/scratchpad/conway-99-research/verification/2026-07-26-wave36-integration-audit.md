# Wave 36 integration audit

Verdict: **PASS for the scoped Wave 36 publication checkpoint**

No integration defect was found. The six mathematical suites pass 66 tests,
all six exact `--verify` regenerations match, every audited path/hash pair and
local link resolves, structured files parse strictly, and the public status
wall remains conservative.

```yaml
role: verifier
date_utc: 2026-07-26T23:32:19Z
git_commit: 697cc02bcbe16b69aaf08822298e03c66329c64c
claim_label: VERIFIED
scope: >-
  Integration and publication-metadata audit of the uncommitted Wave 36
  modular-reflection, ternary-polar, block-compatibility, and literature
  packages. This audit does not cover the active rooted-branch search.
inputs:
  - "README.md and STRUCTURE.md"
  - "REPRODUCING.md and STATUS.yaml"
  - "CLAIMS.yaml and OBLIGATIONS.yaml"
  - "agents/2026-07-26-wave36-modular-reflection.md"
  - "agents/2026-07-26-wave36-ternary-polar-bound.md"
  - "agents/2026-07-26-wave36-block-compatibility.md"
  - "agents/2026-07-26-wave36-literature-audit.md"
  - "attempts/wave36-modular-reflection/"
  - "attempts/wave36-ternary-polar-bound/"
  - "attempts/wave36-block-compatibility/"
  - "attempts/wave36-literature-audit/"
  - "verification/wave36-modular-reflection/"
  - "verification/wave36-ternary-polar-bound/"
  - "verification/wave36-block-compatibility/"
method: >-
  Freshly replay all six mathematical suites and exact verification
  regenerations; strictly parse YAML and JSON; independently check status,
  freeze, and run-report hashes; resolve evidence paths and local Markdown
  links; scan the exact publishable working-tree set for credential-shaped
  data and private local paths; inspect status boundaries and Git whitespace.
command: |-
  .\.venv\Scripts\python.exe -B -m unittest -v attempts/wave36-modular-reflection/test_exact_check.py
  .\.venv\Scripts\python.exe -B attempts/wave36-modular-reflection/exact_check.py --verify attempts/wave36-modular-reflection/exact-results.json
  .\.venv\Scripts\python.exe -B -m unittest -v verification/wave36-modular-reflection/test_independent_check.py
  .\.venv\Scripts\python.exe -B verification/wave36-modular-reflection/independent_check.py --verify verification/wave36-modular-reflection/independent-results.json
  .\.venv\Scripts\python.exe -B -m unittest -v attempts/wave36-ternary-polar-bound/test_exact_check.py
  .\.venv\Scripts\python.exe -B attempts/wave36-ternary-polar-bound/exact_check.py --verify attempts/wave36-ternary-polar-bound/exact-results.json
  .\.venv\Scripts\python.exe -B -m unittest -v verification/wave36-ternary-polar-bound/test_independent_check.py
  .\.venv\Scripts\python.exe -B verification/wave36-ternary-polar-bound/independent_check.py --verify verification/wave36-ternary-polar-bound/independent-results.json
  .\.venv\Scripts\python.exe -B -m unittest -v attempts/wave36-block-compatibility/test_exact_check.py
  .\.venv\Scripts\python.exe -B attempts/wave36-block-compatibility/exact_check.py --verify attempts/wave36-block-compatibility/exact-results.json
  .\.venv\Scripts\python.exe -B -m unittest -v verification/wave36-block-compatibility/test_independent_check.py
  .\.venv\Scripts\python.exe -B verification/wave36-block-compatibility/independent_check.py --verify verification/wave36-block-compatibility/independent-results.json
  .\.venv\Scripts\python.exe -B - <strict structure, hash, evidence, and link audit>
  .\.venv\Scripts\python.exe -B - <exact 52-file privacy scan>
  git diff --check
outputs:
  - path: verification/2026-07-26-wave36-integration-audit.md
    sha256: "Recorded externally after this self-referential report is frozen"
limitations:
  - "The mathematical conclusions remain conditional on n3=4158."
  - "This integration replay does not independently re-prove the inherited Wave 35 graph-to-reflection bridge."
  - "No clean-clone or post-commit replay is possible before an integration commit exists."
  - "The active attempts/wave36-rooted-branches directory is outside this checkpoint and was not audited."
  - "A finite privacy-pattern scan cannot prove that arbitrary prose contains no sensitive information."
audit_verdict: PASS_SCOPED_WAVE36_PUBLICATION_CHECKPOINT
```

## Replay results

| Package | Discovery | Independent | Exact verification |
|---|---:|---:|---|
| modular reflection | 11 passed | 11 passed | both JSON files match |
| ternary polar bound | 10 passed | 12 passed | both JSON files match |
| block compatibility | 10 passed | 12 passed | both JSON files match |
| **Total** | **31** | **35** | **6/6 pass** |

The fresh total is therefore exactly

```text
31 submitted + 35 independent = 66 passing mathematical tests.
```

The test count stated in `STATUS.yaml`, `REPRODUCING.md`, and the Wave 36
index prose agrees with the replay.

## Structural and metadata checks

The independent structural audit found:

```text
strict structured parses:                    18
  central YAML ledgers:                       3
  Wave 36 run-report YAML files:              6
  Wave 36 JSON evidence files:                9

claim IDs:                                   99 unique of 99
obligation IDs:                              91 unique of 91

STATUS hash-bearing fields:                  13
STATUS unique referenced artifacts:          11
STATUS path/hash mismatches:                   0

input-freeze files:                            6
input-freeze entries:                         41
run-report path/hash pairs:                   59
hash mismatches:                               0

Wave 36 claim/obligation evidence references: 34
unique evidence paths:                        17
missing evidence paths:                        0

publishable working-tree files audited:       52
local Markdown links checked:                376
unresolved local links:                        0
credential/private-path pattern hits:          0
git diff --check:                            PASS
```

Strict JSON parsing rejected duplicate keys by construction. Strict YAML
parsing likewise rejected duplicate mapping keys. The hash audit checked
actual bytes, not normalized text.

## Status discipline

The integrated wording correctly preserves the proof boundary:

```text
rank_F3(M)>=12 and rank_F7(M)>=11: VERIFIED, conditional on n3=4158
rank-twelve nonsquare ternary class: excluded
simultaneous B/H completion:          UNKNOWN
n3=4158 endpoint:                    UNKNOWN
upper bound below 4158:              not obtained
rigorous interval:                   708<=n3<=4158
Conway-99 resolution:                NONE / UNKNOWN
novelty and priority:                UNKNOWN
```

The literature integration explicitly attributes the ambient orthogonal-graph
theory and records that Evans's 2023 theorem reproduces the ternary cutoff
after the target-specific substitution. A bounded target-specific no-hit is
not promoted to novelty.

## Rooted-search exclusion

`attempts/wave36-rooted-branches/` is an active, untracked research directory.
It is outside this publication checkpoint, was deliberately excluded from
the 52-file audit set, and **must not be staged as part of this checkpoint**.
No status inference may be made from its partial or live contents.

## Final classification

```text
Wave 36 integration metadata:       VERIFIED scoped
six mathematical suites:            66/66 PASS
six exact verification commands:     6/6 PASS
publication evidence and links:     PASS
privacy and whitespace gates:       PASS
endpoint exclusion:                 NOT OBTAINED
improved general upper bound:       NOT OBTAINED
Conway-99 and novelty:              UNKNOWN
```
