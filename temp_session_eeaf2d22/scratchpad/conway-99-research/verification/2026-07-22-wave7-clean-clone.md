# Wave 7 side-incidence clean-source replay

Verdict: `PASS` for reproducibility at the frozen technical commit. Target
result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T00:43:19Z
git_commit: 0728b260e1282afdbaeaa9215659a4175cab25de
claim_label: VERIFIED
scope: clean-source tests and independent replay of both side-incidence checkers
inputs:
  verification/n3-side-incidence/verify.py: ec51e5245a886f4f10520393ed06140fb4f9f07531f5461c9fc89f04c5654441
  verification/n3-side-incidence/audit_generic.py: cf37f75ad033cb2f9d839e7fa85d6bac2e6d113cfdfc07bc78a043e453482f98
  verification/test_n3_side_incidence.py: d63a97c139b3c405c398aaba14a1e0043c492f1220580c749b9bb0298838ef73
method: fresh no-local source clone, detached frozen-commit checkout, pinned existing virtual environment, full test replay, and standalone execution of both finite checkers
command: |
  $wave7Source = "<project checkout>"
  $wave7Clean = "<new empty scratch path>"
  git clone --no-local --branch codex/first-research-wave $wave7Source $wave7Clean
  git -C $wave7Clean checkout --detach 0728b260e1282afdbaeaa9215659a4175cab25de
  $wave7Python = (Resolve-Path "$wave7Source/.venv/Scripts/python.exe").Path
  & $wave7Python -m unittest discover -s "$wave7Clean/code" -p "test_*.py"
  & $wave7Python -m unittest discover -s "$wave7Clean/verification" -p "test_*.py"
  & $wave7Python "$wave7Clean/verification/n3-side-incidence/verify.py"
  & $wave7Python "$wave7Clean/verification/n3-side-incidence/audit_generic.py"
outputs:
  persistent_output: not_applicable_clean_clone_scratch_only
  python: 3.13.14
  code_tests: 48_passed
  verification_tests: 27_passed
  structured_checker: PASS
  generic_checker: PASS
limitations: the replay reused the already pinned project virtual environment; the finite checkers certify the boundary reduction, not the existence target
```

## Results

The clean source tree was detached at exactly
`0728b260e1282afdbaeaa9215659a4175cab25de`.

- All 48 discovery and encoding tests passed.
- All 27 independent verification and strict-parser tests passed.
- The structured checker reproduced the extremal active-`q` sequences,
  support maxima `6/9/8`, Mantel threshold eleven, global bound `n3>=30`, and
  strengthened twelve-branch tuple.
- The generic checker independently enumerated complete point-clique families
  with singleton fillers and reproduced the same decisive support maxima.

This establishes clean-source reproducibility of the exact finite arithmetic.
It supplies neither a 99-vertex graph nor a complete nonexistence proof.
