# Wave 8 equality-exclusion clean-source replay

Verdict: `PASS` for reproducibility at the frozen technical commit. Target
result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T01:30:45Z
git_commit: b2a31846d243a76b9e516f85304e21137e3fe874
claim_label: VERIFIED
scope: clean-source tests and standalone replay of the n3=30 equality checker
inputs:
  verification/n3-equality/verify.py: 17b306d0e7d198d5c30e068a9c4e7b490ff01dfc91758416b9e67ed641007bf6
  verification/test_n3_equality.py: 8f6a7c6772733386ccb71810c24c996b2ef1739588846a622d670bffa44ad313
method: fresh no-local source clone, detached frozen-commit checkout, pinned existing virtual environment, full test replay, and standalone equality-checker execution
command: |
  $wave8Source = "<project checkout>"
  $wave8Clean = "<new empty scratch path>"
  git clone --no-local $wave8Source $wave8Clean
  git -C $wave8Clean checkout --detach b2a31846d243a76b9e516f85304e21137e3fe874
  $wave8Python = (Resolve-Path "$wave8Source/.venv/Scripts/python.exe").Path
  & $wave8Python -m unittest discover -s "$wave8Clean/code" -p "test_*.py"
  & $wave8Python -m unittest discover -s "$wave8Clean/verification" -p "test_*.py"
  & $wave8Python "$wave8Clean/verification/n3-equality/verify.py"
outputs:
  persistent_output: not_applicable_clean_clone_scratch_only
  python: 3.13.14
  code_tests: 48_passed
  verification_tests: 35_passed
  equality_checker: PASS
limitations: the replay reused the already pinned project virtual environment; the arithmetic checker accompanies a human proof and is not a standalone Conway-99 certificate
```

## Results

The clean source tree was detached at exactly
`b2a31846d243a76b9e516f85304e21137e3fe874` and remained clean after replay.

- All 48 discovery and encoding tests passed.
- All 35 independent verification and strict-parser tests passed.
- The standalone checker recovered ten active `q=2` triangles, fixed-side
  endpoint count four, point counts `(x1,x2,x3)=(0,15,0)`, the forbidden
  overlapping-set degree one, `n3>=33`, `p6>=209319`, and the strengthened
  twelve-branch tuple.

This establishes clean-source reproducibility of the exact finite arithmetic.
The graph-theoretic implications are supplied by the separate human proof and
adversarial reconstruction. No 99-vertex graph or complete nonexistence proof
is claimed.
