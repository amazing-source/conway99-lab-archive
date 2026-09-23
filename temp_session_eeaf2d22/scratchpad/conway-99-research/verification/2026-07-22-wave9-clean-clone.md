# Wave 9 equality-exclusion clean-source replay

Verdict: `PASS` for reproducibility at the frozen technical commit. Target
result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T02:36:20Z
git_commit: 19f27d1ede9cdb0b4110540f52eeb3ad9c94cc94
claim_label: VERIFIED
scope: clean-source tests and standalone replay of the n3=33 equality checker
inputs:
  agents/2026-07-22-wave9-n3-33-equality.md: frozen_at_git_commit
  verification/n3-33-equality/verify.py: fdac28fb0daf7a9af09dd490d878a3c848b187d64a8716e0bdabe2ce36d2aea8
  verification/test_n3_33_equality.py: 8e2adceda27399d948844820f48718c3588ada9e16987af13a5bda411e5a113f
  verification/n3-33-equality/audit_exhaustive.py: 6f22d93c5575fea96dd459a1425fddb268408959e3c6f5e1ef21449f6de8ee1f
  verification/n3-33-equality/verify_exhaustive.py: 31d0c9158d471e16c85922c4647e5081ba4510b430eb1228250084b50bb4bb73
  verification/n3-33-equality/n3-33-census-manifest.json: 92cf3e612a44ab24be5e191bd8ffdb59f5f6dae5335e7ce917ef5ab73c083b9e
  house_of_graphs_quartic_catalog: 05ee6bb0c2b40d63d5c44efc8e89ed1c0a381a170d81a3d052749c8edf6b14fd
method: fresh no-local source clone, detached frozen-commit checkout, pinned existing virtual environment, full test replay, compact checker execution, and independent exhaustive census regeneration/replay
command: |
  $wave9Source = "<project checkout>"
  $wave9Clean = "<new empty scratch path>"
  git clone --no-local $wave9Source $wave9Clean
  git -C $wave9Clean checkout --detach 19f27d1ede9cdb0b4110540f52eeb3ad9c94cc94
  $wave9Python = (Resolve-Path "$wave9Source/.venv/Scripts/python.exe").Path
  & $wave9Python -m unittest discover -s "$wave9Clean/code" -p "test_*.py"
  & $wave9Python -m unittest discover -s "$wave9Clean/verification" -p "test_*.py"
  & $wave9Python "$wave9Clean/verification/n3-33-equality/verify.py"
  & $wave9Python "$wave9Clean/verification/n3-33-equality/audit_exhaustive.py" `
    --catalog "<hashed House of Graphs catalog>" `
    --certificate "<scratch certificate>" `
    --git-commit 19f27d1ede9cdb0b4110540f52eeb3ad9c94cc94
  & $wave9Python "$wave9Clean/verification/n3-33-equality/verify_exhaustive.py" `
    --catalog "<hashed House of Graphs catalog>" `
    --certificate "<scratch certificate>" `
    --output "<scratch replay report>"
outputs:
  persistent_output: not_applicable_clean_clone_scratch_only
  python: 3.13.14
  code_tests: 48_passed
  verification_tests: 46_passed
  equality_checker: PASS
  exhaustive_census: PASS
  quartic_types: 266
  point_clique_families: 610
  surviving_families: 0
limitations: the replay reused the already pinned project virtual environment and the externally sourced hashed quartic catalog; both checkers accompany a human proof and are not standalone Conway-99 certificates
```

## Results

The clean source tree was detached at exactly
`19f27d1ede9cdb0b4110540f52eeb3ad9c94cc94` and remained clean after replay.

- All 48 discovery and encoding tests passed.
- All 46 independent verification and strict-parser tests passed.
- The standalone checker recovered the two active-`q` profiles, excluded the
  mixed profile by the singleton sum, found no nonempty singleton crossing,
  recovered point-size alternatives `(x2,x3)=(12,3),(15,1)`, forced exactly
  one local `K5` closure, rejected all 360 labeled residual
  `K6`-minus-matching local choices, and returned `n3>=36`,
  `p6>=209322`, and the strengthened twelve-branch tuple.
- The primary census regenerated all 610 point-clique families across 266
  quartic types, and the independent implementation reproduced the canonical
  graph, family, per-type, and forbidden-degree digests with zero survivors.

This establishes clean-source reproducibility of the exact finite arithmetic.
The graph-theoretic implications are supplied by the separate human proof and
adversarial reconstruction. No 99-vertex graph or complete nonexistence proof
is claimed.
