# Wave161: independent fifteen-cut verification

Status: `VERIFIED_WITH_SCOPE`.

The Wave159 count pseudowitness is an exact nonnegative rational solution of
the retained **fifteen-cut finite relaxation** at `n3 = 4158`. Independently
replaying the full certificate gives:

- order-seven/order-eight support `204 / 887`;
- `10,313 / 10,313` exact rows passing;
- `10,274` restricted rows;
- modular rank `887 / 887` modulo `1,000,003`;
- all fifteen exact cut values nonnegative, with three active;
- exact negative four-root directions at root masks 3 and 12.

The last item means this particular pseudowitness still violates the full
four-root covariance conditions. The seven blocks without stored negative
certificates are **not** thereby proved positive semidefinite.

## Separation

The verifier never imports or executes Wave159 or Wave152 discovery Python.
It uses a SHA256-pinned earlier clean-room graph/count engine, independently
rebuilds the two fresh covariance cuts and both displayed negative
directions, and recomputes every retained equality and selected modular row.
Solver statuses and floating eigenvalues are not used as evidence.

The Wave159 package manifest has 16/16 exact-byte matches. Wave152's before
and after inventories are byte-identical, and all 42 frozen paths still match
their recorded hashes.

## Reproduce

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe verification\wave161-four-root-cut-loop\independent_verify.py `
  --verify verification\wave161-four-root-cut-loop\exact-results.json
.\.venv\Scripts\python.exe -m unittest `
  verification\wave161-four-root-cut-loop\test_independent_verify.py -v
```

## Evidence boundary

The verified object is a finite-relaxation count pseudowitness, not a graph.
Endpoint existence or exclusion, a strict upper bound below `4158`, and
Conway-99 remain `UNKNOWN`. The inherited witness format/scope text saying
“after two cuts” is stale metadata; the exact replay retains fifteen cuts.
