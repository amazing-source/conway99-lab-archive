# Wave 10 equality-exclusion clean-source replay

Verdict: `PASS` for reproducibility at the frozen documentation commit. Target
result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T03:40:00Z
git_commit: d8ee17669cfd6efdc42b7595d2ae56e9b10161d1
claim_label: VERIFIED
scope: clean-source tests, compact n3=36 checker, support-certificate regeneration, and independent replay
inputs:
  agents/2026-07-22-wave10-n3-36-equality.md: frozen_at_git_commit
  verification/n3-36-equality/verify.py: 3ec131b44a25db344f164f946dd2631fcd16af0a0bc664c1efa6ed2ccb4f498a
  verification/n3-36-equality/audit_support.py: 89a244f78626b90a73bf3b90e25aed9a3b3f229b0680478bb2a88a88f1f7b27b
  verification/n3-36-equality/verify_support.py: e33a1face50be872fb9366c9e4be4271caf360869c8811ffb6e0a92deb3da831
  verification/n3-36-equality/n3-36-support.json: 5f645d5438c9c144c9afb58affec2d783e60f8533d96ffb4f5bfabb3228363e6
  verification/test_n3_36_equality.py: 0c97b857de76c9d62d6847eded70e00dd590d1349516d3db6deee5d3186a5706
  verification/test_n3_36_support.py: f1b185f5a6b84cf7919daf51a0b3b20f943c7214411177ec147e89c353af6117
method: fresh no-local source clone, detached frozen-commit checkout, pinned existing virtual environment, full test replay, primary support regeneration, independent recursive replay, and clean-tree check
command: |
  $wave10Source = "<project checkout>"
  $wave10Clean = "<new empty scratch path>"
  git clone --no-local $wave10Source $wave10Clean
  git -C $wave10Clean checkout --detach d8ee17669cfd6efdc42b7595d2ae56e9b10161d1
  $wave10Python = (Resolve-Path "$wave10Source/.venv/Scripts/python.exe").Path
  & $wave10Python -m unittest discover -s "$wave10Clean/code" -p "test_*.py"
  & $wave10Python -m unittest discover -s "$wave10Clean/verification" -p "test_*.py"
  & $wave10Python "$wave10Clean/verification/n3-36-equality/verify.py"
  & $wave10Python "$wave10Clean/verification/n3-36-equality/audit_support.py" --certificate "<scratch.json>" --git-commit 2194c2b68ebd5c34491d64f15d30f1a3597baa74
  & $wave10Python "$wave10Clean/verification/n3-36-equality/verify_support.py" --certificate "<scratch.json>"
  & $wave10Python "$wave10Clean/verification/n3-36-equality/verify_support.py" --certificate "$wave10Clean/verification/n3-36-equality/n3-36-support.json"
outputs:
  persistent_output: not_applicable_clean_clone_scratch_only
  python: 3.13.14
  code_tests: 48_passed
  verification_tests: 62_passed
  equality_checker: PASS
  resource_profiles: 14
  labeled_point_families: 100
  abstract_support_masks: 216
  support_mask_sha256: 6659fe1972cbacc6980a9792557714730572817b43224b5f1fac24bb0c4ca61a
  survivors_after_rook_saturation: 0
  regenerated_scratch_certificate_sha256: e11d091e687ac717eb6196086534f398003d288a20034a80f6b7efd663d22934
  clone_clean_after_replay: true
limitations: the replay reused the already pinned project virtual environment; certificate runtime metadata is intentionally non-deterministic, while every mathematical field and the support-mask digest were independently reproduced; the checkers accompany a human proof and are not standalone Conway-99 certificates
```

## Results

The source tree was cloned with `--no-local`, detached at exactly
`d8ee17669cfd6efdc42b7595d2ae56e9b10161d1`, and remained clean after replay.

- All 48 discovery and encoding tests passed in the pinned environment.
- All 62 independent verification and strict-parser tests passed.
- The compact checker recovered the three active profiles, rejected the mixed
  profiles by singleton forcing, recovered all four local point types, checked
  the six-vertex cubic and rook-graph subcases, rejected both size-three
  mechanisms, forced all three group pairings to `2K6`, and returned `n3>=39`,
  `p6>=209325`, and the strengthened twelve-branch tuple.
- The primary support program regenerated fourteen resource profiles, one
  hundred labeled point families, and all 216 abstract masks.
- The independent recursive implementation reproduced mask digest
  `6659fe...61a`, rejected five certificate mutations, and found zero survivors
  after the original-SRG common-neighbor check for both the regenerated and
  committed certificates.

## Environment failure retained

Before the pinned replay, the ambient Windows Store Python was used once by
mistake. Its code-suite run had 23 passes and two import errors because
`python-sat` was not installed; the 62 standard-library verification tests
still passed there. This was an environment mismatch, not a failed
mathematical assertion. The documented `.venv` run then passed all 48 and 62
tests, and the detached clean clone used that same pinned interpreter.

This establishes clean-source reproducibility of the exact finite arithmetic
and support census. The graph-theoretic implications are supplied by the
separate human proof and adversarial reconstruction. No 99-vertex graph or
complete nonexistence proof is claimed.
