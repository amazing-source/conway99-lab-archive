# Wave 42 branch-15 endpoint strengthening

Status: `CANDIDATE_STRONGER_REDUCTION`. Refined endpoint branch 15 remains
`UNKNOWN`; checked endpoint coverage remains `0/33`.

## New exact constraint family

Wave 37 added prism clauses for the six triangles fixed by branch 15's parent
case. The refined branch itself also contains the unit `x2=1`. Under the
frozen lexicographic residual labels,

```text
x2 = edge((0,2),(0,4)),
```

so `x2` creates a seventh fixed triangle on full vertices `[1,15,17]` through
coordinate 0. Conditional on the endpoint `n3=4158`, the graph is prism-free.
For every disjoint second triangle and perfect matching to `[1,15,17]`, the
conjunction of the required residual edges is therefore forbidden.

The complete family contains:

```text
raw new clauses:                 64,932
  width 3:                          132
  width 5:                       64,800
exact row overlaps with Wave 37:      0

active after Wave 41 closure:     33,778
  width 3:                           91
  width 4:                          580
  width 5:                       33,107
immediate new units:                  0
immediate contradiction:              no
```

No completed-graph automorphism is assumed. The unsimplified 64,932-clause
delta is sound without trusting the Wave 41 discovery closure.

## Retained catalogues and serialization

- `branch-15-seventh-triangle-delta.opb.gz` retains all 64,932 clauses.
- `branch-15-seventh-triangle-active-delta.opb.gz` retains all 33,778 clauses
  after simplification by the SHA-bound Wave 41 closure.

Each decompresses to a canonical OPB stream: one header followed by clauses in
sorted positive-variable-ID order, each rendered as
`+1 ~xID ... >= 1 ;`. The JSON catalogue hashes use a compact JSON array of
sorted positive-variable-ID arrays. These serialization rules are explicit so
an independent verifier can compare clause sets rather than implementation
details.

## Combined propagation and bounded probes

Exact generalized-unit propagation on the frozen OPB plus the raw delta
reaches the same fixed point as Wave 41:

```text
forced variables:                 830
forced primary variables:         174
delta-sourced derivations:           0
active delta constraints:       33,778
```

Both polarities of the prior 32 high-pressure primary variables were replayed
on the combined formula. All 64 probes remain noncontradictory, none changes
relative to Wave 41, and no candidate implication appears. This null
lookahead result is not evidence of satisfiability.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave42-endpoint-certificate\seventh_triangle_strengthen.py

.\.venv\Scripts\python.exe -B `
  attempts\wave42-endpoint-certificate\seventh_triangle_strengthen.py `
  --verify

.\.venv\Scripts\python.exe -B `
  attempts\wave42-endpoint-certificate\combined_propagation.py

.\.venv\Scripts\python.exe -B `
  attempts\wave42-endpoint-certificate\combined_propagation.py `
  --verify

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave42-endpoint-certificate -p "test_*.py" -v
```

## Promotion boundary

- The clause family requires independent replay before promotion.
- A fixed point is neither a SAT witness nor an UNSAT certificate.
- Even checked UNSAT for branch 15 would close only one of 33 endpoint cases.
- A SAT assignment would still require independent complete-SRG and exhaustive
  prism-free checks.
- No endpoint case, upper bound, or global Conway claim is decided here.
