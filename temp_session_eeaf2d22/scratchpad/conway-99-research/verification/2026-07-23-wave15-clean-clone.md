# Wave 15 detached clean-clone replay

```yaml
role: orchestrator_release_gate
date_utc: 2026-07-23T11:10:53Z
tested_commit: 9215f06a45cb1477b46ebb29d350155e0abd0d08
discovery_baseline_commit: 522260aa71d484c86477599de65f9e08ded437bb
public_newline_repair_commit: 874af271c775f64d49148c31a20bca6583f29c82
verification_commit: 1ecc0d40e91fbe736c26f73a5b74c5961c321654
verdict: PASS
target_result: UNKNOWN
novelty: UNKNOWN
environment:
  platform: Microsoft Windows NT 10.0.26200.0
  python: 3.13.14
  git: 2.51.0.windows.1
test_counts:
  tracked_code: 52
  focused_wave13: 12
  tracked_verification: 104
  wave14_proof: 10
  wave14_computation: 7
  wave15_global_submitted: 5
  wave15_global_independent: 11
  wave15_algebraic_independent: 7
artifact_checks:
  declared_wave15_hashes: 18
  canonical_lf_crlf_count: 0
  byte_identical_global_certificates: true
  detached_worktree_clean: true
  git_fsck: PASS
```

## Isolation protocol

A fresh local clone was created from the repository object database with
`--no-local` and checked out detached at exactly
`9215f06a45cb1477b46ebb29d350155e0abd0d08`. The source worktree's untracked
Wave 16 reports, code, attempts, and verifier files were absent. The clone
reused only the source repository's pinned virtual-environment interpreter;
no dependency directory or untracked source file was copied into it.

The clone was clean before replay and after every deterministic regeneration.
Its exact head, detached state, clean status, absence of Wave 16 paths, and
object database were checked at the end; `git fsck --no-dangling
--no-progress` passed. The fixed, prechecked temporary clone was then moved to
the Recycle Bin, so cleanup is recoverable.

## Replay results

The detached clone passed:

- YAML parsing and the Wave 15 `n3>=51`, `induced_C6_count>=209337`, target
  `UNKNOWN`, and novelty `UNKNOWN` assertions;
- 52 tracked `code/test_*.py` tests;
- 12 focused Wave 13 tests;
- 104 tracked `verification/test_*.py` tests;
- 10 focused Wave 14 proof/countermodel tests;
- 7 focused Wave 14 computation/provenance tests;
- 5 submitted Wave 15 global-lift tests;
- 11 independent Wave 15 global-lift tests;
- 7 independent Wave 15 algebraic tests; and
- both independent Wave 15 semantic checkers.

All eighteen committed Wave 15 discovery and verification files matched their
declared SHA-256 values. The three regenerated artifacts were unchanged from
the tested commit:

| artifact | SHA-256 |
|---|---|
| `attempts/wave15-global-lift/subset-moment-certificate.json` | `cb02ab80f92d7d2c8ec5140e3be2916354976442aa2e1869524aa728c73bd386` |
| `verification/n3-48-global-lift/regenerated-certificate.json` | `cb02ab80f92d7d2c8ec5140e3be2916354976442aa2e1869524aa728c73bd386` |
| `attempts/wave15-algebraic/exact-checks.json` | `a6c9109e4fcfcdd2f5a8f5d4299ac1b4cf4037b8f1e4c468b4ecd75aba762512` |

The two global certificates are byte-for-byte identical canonical-LF files.
The repaired global bundle contains zero CRLF sequences.

## Preserved failures and repairs

The scientific failures remain in the discovery and audit reports. Active
common-neighbor caps and the first two triangle-intersection moments do not
exclude the frontier. The algebraic lane's first JSON used an ambiguous
weighted-moment key; it was renamed and independently re-audited. The first
global certificate used Windows CRLF bytes that differed from its public LF
Git blob. Baseline `522260a` preserves that failure, and `874af27` preserves
the explicit canonical-LF repair.

Two local test-harness mistakes were also retained during integration. The
global independent suite was first invoked from the repository root, where
its sibling import failed before any test assertion ran; it passed 11/11 from
its verifier directory. Conversely, the algebraic suite was first invoked
from its verifier directory, where six tests passed and its repository-root
artifact lookup failed; it passed 7/7 from the repository root.

Several release wrappers failed without suppressing a test or changing an
artifact. One pre-clone wrapper used unsupported PowerShell generic-method
syntax before any command executed. A link checker mishandled the empty
parent string for root-level files after its YAML check. The first two clone
baseline wrappers called `Trim()` on the empty detached-branch output after
the clone and checkout had succeeded; the corrected check used
`git rev-parse --abbrev-ref HEAD`. Finally, the first 18-hash map contained a
transcription error in one expected algebraic-test hash; the gate rejected it,
the expected map was corrected from the audit's frozen value, and all 18
actual hashes then passed. These were orchestration or metadata-check failures,
not mathematical or test assertion failures. A final scope wrapper also
expected `git diff --name-only` to list the newly untracked replay report;
the corrected gate used `git status --short` for that file and passed.

## Status boundary

This replay verifies the repository mechanics and the internally audited,
conditional exclusion of `n3=48`. It supports only the necessary bounds

```text
n3 >= 51,
induced_C6_count >= 209337.
```

It is not a formal-kernel proof, a construction or nonexistence proof for
`srg(99,14,1,2)`, or a novelty determination. Conway-99 and novelty remain
`UNKNOWN`.
