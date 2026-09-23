# Wave 38 failed routes and restrictions

## Terminal-buffered live sweeps

Both live scouts buffer all case records in memory and emit their JSON only
after the final selected case returns. No output exists at the recorded
snapshot. Therefore no completed prefix, current-case identity, model,
proof, or solver conclusion can be recovered. Future runs need an atomic
per-case journal.

## Conflict-budget interpretation

Each embedded PySAT call has a nominal 100,000-conflict budget. A return of
`None` becomes `BUDGET_UNKNOWN`. That is a timeout-equivalent engineering
event with zero mathematical evidentiary value. A long runtime or positive CPU
activity is also zero evidence.

## Embedded UNSAT interpretation

The live Gluecard4 and MiniCard engines are not configured to retain a proof.
Even if a future terminal JSON says `UNSAT_UNVERIFIED`, that string and its
solver counters cannot eliminate a case. The case must be re-exported to the
canonical OPB and solved through the pinned Exact/VeriPB/CakePB pipeline.

## Partial prism encoding

Each parent formula forbids prisms meeting six already fixed triangles. It
does not enumerate every triangular prism. These clauses are necessary
endpoint consequences. Hence checked UNSAT is useful, but SAT alone is not an
endpoint construction.

## Scope accounting

The underlying oriented refinement has 78 orbits. Only 33 lie over the five
parents surviving the independently audited endpoint-unit propagation. Calling
the live full sweep a "78-case" or a "33 arbitrary cases" run would be wrong:
it is exactly the endpoint-compatible 33-case subcover.

## Resource restriction

No new solver was started during this audit. The host had less than one GiB
of free physical memory while the two requested workers and other research
jobs were active. The continuation plan therefore specifies one
proof-producing case at a time until resource availability is re-established.
