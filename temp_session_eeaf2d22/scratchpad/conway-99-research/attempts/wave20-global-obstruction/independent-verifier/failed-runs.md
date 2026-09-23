# Independent verifier failed runs

## 2026-07-23 precomparison test invocation

```yaml
role: verifier
date_utc: 2026-07-23T16:19:00Z
git_commit: NOT_USED_PER_TASK_INSTRUCTION
claim_label: REFUTED
scope: first detached invocation of the independent unit-test module
inputs:
  - attempts/wave20-global-obstruction/independent-verifier/test_independent_check.py
method: Python unittest invoked by repository-relative path from the repository root
command: >
  python -B -m unittest -v
  attempts\wave20-global-obstruction\independent-verifier\test_independent_check.py
outputs: none
limitations:
  - The test module failed during import before any test ran.
  - The cause was that independent_check.py's directory was not on sys.path.
  - This run supplies no mathematical evidence either for or against the claim.
```

Observed terminal error:

```text
ModuleNotFoundError: No module named 'independent_check'
Ran 1 test in 0.000s
FAILED (errors=1)
```

Repair: invoke `python -B -m unittest -v test_independent_check.py` with the
working directory set to the independent-verifier directory.  The source
files themselves did not need to be changed for this harness-only failure.
