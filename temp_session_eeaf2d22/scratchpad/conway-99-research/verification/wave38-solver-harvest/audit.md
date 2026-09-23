# Wave 38 solver-harvest adversarial audit

Verdict: **PASS for the exact queue and null harvest only**.

The 33-case endpoint work queue, its orbit weights, artifact paths, frozen
hashes, schemas, and privacy boundary were independently checked. The two
recorded workers were observed again read-only and still had no output.
Neither process activity nor the published branch-15 formula contributes any
proof coverage:

```text
independently checked UNSAT cases:  0
independently checked endpoint graphs: 0
proof coverage:                     0 / 33
n3=4158 endpoint:                   UNKNOWN
upper bound on n3:                  4158
```

## Independent case reconstruction

The verifier did not import either Wave 38 discovery script. It reconstructed
the 12 normalized parent matching orbits, all 78 oriented refinement orbits,
and the endpoint-compatible parent filter from the frozen independent rooted
definitions. The resulting queue agrees case by case with
`coverage-plan.json`, including every candidate endpoint, orbit size,
refinement edge, and refinement literal.

| parent | refined cases | count | orbit weight |
|---:|:---|---:|---:|
| 4 | 15--18 | 4 | 132 |
| 5 | 19--22 | 4 | 528 |
| 8 | 36--41 | 6 | 704 |
| 10 | 50--57 | 8 | 1,056 |
| 12 | 68--78 | 11 | 4,224 |
| total | 33 cases | 33 | 6,644 |

The other 45 normalized refinement orbits have total weight 3,751, and
`6,644+3,751=10,395`, the full refined state count. This is a conditional
normalized cover under `n3=4158`; it does not assume an automorphism of a
completed graph.

## Process-observation boundary

The discovery snapshot was captured at `2026-07-27T00:53:21.788Z`. It
recorded two live process trees, positive worker CPU movement, no terminal
JSON, and no candidate or proof paths. The original CPU sample is historical
and cannot be replayed.

At `2026-07-27T01:04:27.665Z`, the independent verifier inspected the same
process trees and command scopes read-only and sampled the workers again:

| run | worker PID | CPU delta | output present |
|:---|---:|---:|:---:|
| full 33-case Gluecard4 | 27,676 | 0.3125 s | no |
| parent-4 MiniCard | 20,988 | 0.78125 s | no |

The processes were not attached to, signaled, stopped, or modified. Positive
CPU movement shows only that work occurred during the sample. Because the
scout writes after the whole selected sweep and has no per-case journal, a
missing output exposes no completed prefix and no case verdict.

## Artifact paths and absence boundary

Each of the 33 cases owns seven planned paths below
`logs/local/wave38-endpoint-33`, for 231 paths total. The verifier checked:

- exact case-specific stems and file-type suffixes;
- relative POSIX spelling under the owned directory;
- no `..`, absolute path, drive prefix, backslash, trailing dot/space, or
  Windows reserved component;
- no exact or case-insensitive collision; and
- no collision with the published branch-15 seed formula.

None of the 231 planned artifacts exists. The Wave 38 package contains no
`.pbp` proof and no `.srg.json` graph. Branch 15 has a separately published
compressed OPB formula, already audited as a formula artifact only; it has no
solver verdict or proof.

## Hash, schema, and privacy checks

All 11 discovery input-freeze entries, 11 run-report input hashes, and 10
run-report output hashes match current bytes. The verifier freeze contains 15
additional exact inputs and independently passes a full hash replay.

Strict JSON parsing rejects duplicate keys and non-standard constants.
Coverage, case, artifact, snapshot, and live-observation key sets and critical
types/statuses were checked fail-closed. Thirteen text artifacts were scanned:
no absolute user path, home path, credential marker, bearer token, or API-key
name was found.

Hostile mutations rejected:

- a missing case;
- an altered orbit size;
- case-insensitive path collision;
- path traversal;
- an uncertified proof promotion;
- a fabricated snapshot terminal result;
- duplicate JSON keys and `NaN`; and
- injected credential or absolute-user-path text.

The independent suite passed 12 tests.

## Promotion gate

The endpoint can be excluded through this split only after all 33 cases have
independently checked UNSAT certificates. A solver-reported or timed-out
negative result without the required VeriPB/CakePB checks covers zero cases.

A SAT assignment also does not establish the endpoint until it is decoded and
independently verified as a complete `srg(99,14,1,2)` with global prism count
zero. The fixed-triangle clauses are necessary but not a complete all-prism
encoding.

Final scoped status:

```text
33-case queue and weights:       VERIFIED
path/hash/schema/privacy plan:   VERIFIED
live process result:             NONE
independently checked proofs:    0
proof coverage:                  0/33
n3=4158 endpoint:                UNKNOWN
Conway-99:                       UNKNOWN
```
