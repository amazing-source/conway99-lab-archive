# Wave 41 failed and deferred routes

## Plain generalized-unit propagation

The complete zero-search closure of the published branch-15 OPB forces 830
variables but reaches a consistent fixed point. It therefore does not close
branch 15. The 174 forced primary variables leave 3,312 primary graph-edge
variables unset.

## One-level failed-literal propagation

Both polarities of the 32 primary variables with the greatest incidence in
one-slack constraints were tested. None propagated to contradiction. Positive
assumptions sometimes forced 112 further variables; negative assumptions
often forced none. The retained records are useful for branching heuristics
only.

## Static complete all-prism formula

The complete schema includes exactly 24,388,892,640 labelled clauses in the
residual-only subfamily before branch simplification. Materializing or solving
this OPB was rejected as unsafe and impractical. The Wave 38 lazy oracle is
the exact practical alternative.

## New unrestricted or endpoint-scale Exact run

No new target-scale Exact run was launched. Earlier ten-second full-target
runs generated 123--155 MB raw proofs and ended in checked `NO CONCLUSION`.
During this audit, free physical memory fell below 1.3 GB and then below
0.4 GB while unrelated research processes remained active. Starting another
large solver would have been resource-unsafe and would likely have created
another non-evidentiary proof log.

Two bounded WSL shell probes, used only to locate and recheck the pinned
proof-tool binaries, did not finish within 20 and 30 seconds under this
pressure. This is an environment observation, not a solver or checker result.

## Existing embedded scouts

The pre-existing Gluecard4 33-case sweep and MiniCard parent-4 sweep were
observed alive and CPU-active. Over a two-second sample their CPU totals each
increased by about one second. Neither requested JSON output existed. The
scripts journal only after their selected queue finishes, so no case result
can be harvested from the live processes. They were not signaled, stopped,
or modified.

## CP-SAT, SMT, and MILP

OR-Tools, Z3, PuLP, SCIP, CBC, HiGHS, GLPK, Gurobi, and CPLEX were not
available as configured Python modules or command-line programs. Installing
one would not by itself solve the certification problem: the project needs a
retained, independently checkable infeasibility proof. No dependency was
installed and no uncertified reformulation was launched.

## Embedded PySAT proof logging

The environment has many PySAT backends, including CaDiCaL and Kissat, but the
current endpoint formula uses 5,838 native pseudo-Boolean cardinality rows.
No accepted end-to-end target proof replay is configured for the embedded
translation. An unchecked solver `UNSAT` would not close a case, so this route
was used only for infrastructure inventory.

## Resulting roadblock

The strongest exact route still requires one of:

1. a terminal proof-producing solve for each of the 33 sound endpoint cases;
2. a solve--decode--global-prism-cut loop that ends with a checked prism-free
   SRG witness or an independently checked UNSAT proof; or
3. a new mathematical reduction that shrinks the 33 cases before solving.

Wave 41 supplies a full propagation closure and branch-pressure measurements,
but none of these three terminal events occurred.
