# Wave 38 solver harvest

This directory records a read-only audit of the two long-running Wave 36
refined endpoint scouts and freezes the exact 33-case proof-producing
continuation queue.

Current verdict:

```text
live Gluecard4 full sweep:    LIVE, no output
live MiniCard parent-4 run:  LIVE, no output
terminal solver results:     0
proof-certified cases:       0 / 33
n3=4158:                     UNKNOWN
general upper bound on n3:   4158
```

Artifacts:

- `process-snapshot.json`: sanitized point-in-time process trees, exact
  invocations/configuration, activity samples, and absent output targets;
- `coverage-plan.json`: deterministic list of all 33 endpoint-compatible
  refined representatives and case-owned proof artifact paths;
- `continuation-plan.md`: proof pipeline and exact promotion gate;
- `failed-routes.md`: observability, timeout, scope, and resource failures;
- `verify_harvest.py` and `test_verify_harvest.py`: fail-closed reconstruction
  and hostile tests.

Rebuild and verify without starting a solver:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave38-solver-harvest\build_coverage.py
.\.venv\Scripts\python.exe -B attempts\wave38-solver-harvest\verify_harvest.py
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave38-solver-harvest -p "test_*.py" -v
```

The process snapshot is historical and cannot be recreated after the
processes change state. The coverage plan is deterministic from the published
refined-cover certificate and endpoint-reduction artifact.
