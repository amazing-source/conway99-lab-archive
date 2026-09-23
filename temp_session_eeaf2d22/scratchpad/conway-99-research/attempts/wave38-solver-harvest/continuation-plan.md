# Wave 38 proof-producing continuation

Status: `UNKNOWN`. This is a work queue, not a proof and not a solver result.

## Harvest verdict

At `2026-07-27T00:53:21.788Z`, both requested solver workers were still
present. A three-second sample immediately beforehand showed positive CPU
movement for both workers. Neither requested JSON output existed:

- Gluecard4, all five endpoint-compatible parents: no
  `refined-100k.json`;
- MiniCard, parent 4 only: no
  `refined-100k-minicard-parent4.json`.

The scout writes its JSON only after all selected cases return. It has no
per-case journal. Consequently, the process state exposes neither the current
case nor any completed prefix. Runtime and CPU consumption are not evidence.
The processes were not attached to, signaled, stopped, or modified.

## Exact endpoint coverage

The independently verified refined cover has 78 orbits on 10,395 normalized
states. Endpoint propagation eliminates seven of the twelve parent matching
orbits. Filtering by the exact survivor list gives:

| parent | refined cases | cases | state-orbit weight |
|---:|:---|---:|---:|
| 4 | 15--18 | 4 | 132 |
| 5 | 19--22 | 4 | 528 |
| 8 | 36--41 | 6 | 704 |
| 10 | 50--57 | 8 | 1,056 |
| 12 | 68--78 | 11 | 4,224 |
| total | 33 representatives | 33 | 6,644 |

This is a normalized conditional cover under `n3=4158`. It uses only
automorphisms preserving the normalized rooted data and assumes no
automorphism of a completed graph.

The complete case table, including candidate endpoint, orbit size,
refinement literal, and collision-free artifact paths, is
`coverage-plan.json`.

## Atomic proof-producing workflow

Run no more than one case at a time on the presently memory-constrained host.
For each of the 33 case IDs:

1. Export a canonical OPB with
   `attempts/wave37-proof-producing-endpoint/export_endpoint_opb.py`.
2. Audit and hash the OPB, and require the pinned Exact binary to accept
   `--onlyparse`.
3. Invoke pinned Exact with `--proof-assumptions=0` and a case-owned proof
   log. A bounded run may be used for engineering, but a timeout is recorded
   only as `NO_CONCLUSION`.
4. If Exact reports `UNSAT`, replay the raw proof with strict VeriPB,
   elaborate it, replay the kernel proof with strict VeriPB, and require
   CakePB to report `VERIFIED UNSATISFIABLE`.
5. If Exact reports `SAT`, retain and decode the assignment independently.
   Check every degree, every adjacent/nonadjacent common-neighbor count, and
   global triangular-prism count.
6. Write the case result only after all required checks pass. Use a temporary
   file and an atomic rename so interruption cannot manufacture a terminal
   record.

The pinned Exact, VeriPB, and CakePB hashes are carried in
`coverage-plan.json` and derive from the published calibration.

## Closure rule

The endpoint `n3=4158` is excluded only when all 33 representatives have
independently checked UNSAT certificates. One missing, timed-out, or merely
solver-reported case leaves the endpoint `UNKNOWN`.

The formulas currently include every complete rooted SRG constraint, all 84
endpoint units, the `N3` normalization and refined representative, and all
prism clauses meeting one of the parent branch's six fixed triangles. The
prism clauses are necessary but not exhaustive:

- an independently certified `UNSAT` result excludes its case;
- a `SAT` result may contain another prism and does not establish the endpoint;
- only a decoded complete SRG with independently checked global prism count
  zero would establish endpoint feasibility.

Branch 15 has a published compressed formula but no SAT/UNSAT result or
proof. The remaining 32 formulas have not been exported. Current proof
coverage is therefore `0/33`.
