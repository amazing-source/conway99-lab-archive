# Wave 13 detached clean-clone replay

```yaml
role: orchestrator_replay
date_utc: 2026-07-23T09:33:27Z
git_commit: 4e354b80101b24cd9ef0861e9f65f948b912621f
claim_label: VERIFIED
scope: detached clean-source replay of the integrated Wave 13 conditional n3=45 exclusion and repaired computation bundle
environment:
  platform: Windows-11-10.0.26200-SP0
  python: 3.13.14
  python_sat: 1.9.dev7
  pyyaml: 6.0.2
  dependency_boundary: the clean clone reused the repository workspace's pinned virtual-environment interpreter; no dependency directory was copied into the clone
method: local no-hardlink clone, detached checkout of the frozen integration commit, complete committed test discovery, direct proof-checker replay, YAML parse, and byte-hash regeneration outside the clone
outputs:
  code_tests: 52_passed
  focused_wave13_tests: 12_passed
  verification_tests: 104_passed
  first_proof_checker: PASS
  second_blind_semantic_checker: PASS
  yaml_parse: PASS
  regenerated_census_sha256: 6546819c11dbecbf21a4cfaff00b71d338629c045c7bf156493426391b25ac55
  regenerated_positive_candidate_sha256: 629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8
  detached_worktree_status: CLEAN
  conditional_n3_lower_bound: 48
  conditional_induced_C6_lower_bound: 209334
  target_result: UNKNOWN
  novelty_status: UNKNOWN
limitations: the replay is a clean-source and deterministic-artifact check, not a proof-assistant kernel check; the virtual environment was reused; no negative SAT proof trace exists; no Wave 14 work was present in the detached commit
```

## Result

The exact integration commit
`4e354b80101b24cd9ef0861e9f65f948b912621f` was cloned with local hardlink
reuse disabled and checked out in detached-HEAD state. The clone contained no
uncommitted Wave 14 files. After all tests and regenerations, `git status
--short` was empty.

The committed suites passed:

```text
code discovery:               52 tests, OK
Wave 13 repaired-code suite:  12 tests, OK
verification discovery:      104 tests, OK
```

The 104-test verification discovery includes both the current repaired-bundle
regressions and the historical FAIL-audit suite. The latter reads the failed
validator and artifact directly from frozen commit
`066d9c7fcf593c3b9d35cfef1031dbd9daab4145`, so it continues to test the
original permissive behavior without switching or mutating the clean
worktree.

Both human-proof checkers also returned successfully:

```powershell
.venv\Scripts\python verification\n3-45-equality\verify.py --mutations
.venv\Scripts\python verification\n3-45-equality-b\audit_semantics.py
```

The first attempt to orchestrate the clone stopped before checkout or tests
because PowerShell promoted Git's ordinary `Cloning into ...` progress on
standard error to a terminating wrapper error. The clone itself had completed
at the correct commit. After verifying its `HEAD` and clean status, the replay
resumed there using quiet/manual exit-code handling. This was a shell-wrapper
failure only; it did not alter the repository or suppress a test failure.

## Deterministic artifacts

Fresh outputs were written outside the clone. The local census regenerated at
SHA-256
`6546819c11dbecbf21a4cfaff00b71d338629c045c7bf156493426391b25ac55`,
byte-identical to the repaired archive. The positive `no_common_point`
diagnostic regenerated at SHA-256
`629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8`,
validated against the final v2 source, and was likewise byte-identical.

The independent repair audit already reconstructs all 17 formula streams and
checks the positive assignment clause-by-clause. This replay does not promote
the 17 solver-negative rows: no checked DRAT, FRAT, LRAT, or other proof trace
exists, so they remain `UNSAT_UNVERIFIED`.

## Status boundary

The detached replay supports only the internally verified conditional claim

```text
n3 >= 48,
induced_C6_count >= 209334.
```

It does not construct or exclude `srg(99,14,1,2)`, establish literature
novelty, or supply a formally checked proof. Conway-99 and novelty remain
`UNKNOWN`.
