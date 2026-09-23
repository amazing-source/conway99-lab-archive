# Wave 11 equality-exclusion clean-source replay

Verdict: `PASS` for reproducibility at the frozen documentation commit. Target
result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T05:51:32Z
git_commit: 7895a7da129a5d5415b21603872c3a002e6c7f6d
claim_label: VERIFIED
scope: clean-source tests, compact n3=39 checker, canonical local-certificate regeneration, independent replay, and byte-portability check
inputs:
  agents/2026-07-22-wave11-n3-39-equality.md: frozen_at_git_commit
  verification/n3-39-equality/verify.py: 195f0c87ddca000839ea41edf5569fd4791b1068f2edaaff72c05e0b327c17c5
  verification/test_n3_39_equality.py: bcbe59dc51aa261481010148c936da9e48c08efdd63d28e5d02c31d8692b8b67
  verification/n3-39-equality/audit_local.py: 8db04ec4bb4db4266226581f70e1abc1f74a2e00ddde3277206da634d36c5a9b
  verification/n3-39-equality/verify_local.py: 0113924cc8c36f8cbccad31630e54174de49aeaadcb874c1005f2e8e5622d887
  verification/test_n3_39_local.py: c90029a2a1a452456804efe0a2dd43739dfa7e83cd6baa844eed7842fcd87603
  verification/n3-39-equality/n3-39-local.json: 4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261
method: fresh no-local source clone, detached frozen-commit checkout, pinned existing virtual environment, full test replay, primary regeneration to scratch, independent replay of committed and scratch certificates, exact byte comparison, and clean-tree check
command: |
  $wave11Source = "<project checkout>"
  $wave11Clean = "<new empty scratch path>"
  git clone --no-local $wave11Source $wave11Clean
  git -C $wave11Clean checkout --detach 7895a7da129a5d5415b21603872c3a002e6c7f6d
  $wave11Python = (Resolve-Path "$wave11Source/.venv/Scripts/python.exe").Path
  & $wave11Python -m unittest discover -s "$wave11Clean/code" -p "test_*.py"
  & $wave11Python -m unittest discover -s "$wave11Clean/verification" -p "test_*.py"
  & $wave11Python "$wave11Clean/verification/n3-39-equality/verify.py"
  & $wave11Python "$wave11Clean/verification/n3-39-equality/verify_local.py" --certificate "$wave11Clean/verification/n3-39-equality/n3-39-local.json"
  & $wave11Python "$wave11Clean/verification/n3-39-equality/audit_local.py" --certificate "<scratch.json>" --dump-dir "<scratch-streams>" --git-commit c299b88fbd956c813ff3379ff236b3123a90d242
  & $wave11Python "$wave11Clean/verification/n3-39-equality/verify_local.py" --certificate "<scratch.json>"
  & $wave11Python -m unittest -v verification.test_n3_39_equality verification.test_n3_39_local
outputs:
  persistent_output: not_applicable_clean_clone_scratch_only
  python: 3.13.14
  git: 2.51.0.windows.1
  os: Microsoft_Windows_NT_10.0.26200.0
  code_tests: 48_passed
  verification_tests: 79_passed
  focused_tests: 17_passed
  equality_checker: PASS
  local_replay: PASS
  certificate_records: 8907
  canonical_jsonl_bytes: 1730729
  combined_stream_sha256: 452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1
  outer_certificate_bytes: 2787
  committed_certificate_sha256: 4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261
  regenerated_certificate_sha256: 4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261
  committed_and_regenerated_bytes_equal: true
  clone_clean_after_replay: true
limitations: the replay reused the already pinned project virtual environment; the certificate verifies only the stated conditional n3=39 local reduction, while the graph-theoretic bridge is supplied by the separately audited human proof; this is not a construction or complete nonexistence certificate
```

## Results

The source tree was cloned with `--no-local`, detached at exactly
`7895a7da129a5d5415b21603872c3a002e6c7f6d`, and remained clean after replay.

- All 48 discovery and encoding tests passed in the pinned environment.
- All 79 verification and strict-parser tests passed.
- All 17 focused Wave 11 tests passed, including the canonical-LF regression.
- The compact checker recovered the four active profiles, excluded all mixed
  profiles, checked the size-four and size-three crossing witnesses, reached
  the parity contradiction, and returned the conditional bounds `n3>=42` and
  `induced_C6_count>=209328` with target status `UNKNOWN`.
- The independent replay accepted both certificates and rejected all eight
  premise, digest, conclusion, and status mutations.
- The regenerated outer certificate was byte-for-byte identical to the
  committed 2,787-byte file. Both had SHA-256
  `4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261`.

## Failed portability gate retained

The first detached replay, at documentation commit
`d919a3c1b25aec74295e5f57891d6feed765b7de`, passed all mathematical checks but
failed the whole-file portability gate. Git stored a 2,787-byte LF certificate
with SHA-256
`c9dea5589e4425d89d8cce72902829589288ee9134fdb0b01b2f77cdae171e0e`, while
the Windows regeneration used CRLF and had SHA-256
`48f14aaff09ab0a7fd9fa2bb7e07c643849f6094acbded4c8a05f22113c09e3e`.
Their parsed JSON and internal canonical stream digest were identical, so this
was a packaging defect rather than a mathematical discrepancy.

Commit `c299b88fbd956c813ff3379ff236b3123a90d242` changed both writers to emit
canonical LF bytes, and commit
`19d77662fe6885b12eef731cdc04ca08652f4917` rebound the archived certificate.
The frozen replay above establishes byte-stable clean-source reproduction of
the repair. The conditional count bound is verified; Conway-99 remains
`UNKNOWN`.
