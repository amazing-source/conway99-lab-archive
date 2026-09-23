# Wave 13 `n3=45` computational repair

```yaml
role: construction
date_utc: 2026-07-23T08:51:02Z
git_commit: 066d9c7fcf593c3b9d35cfef1031dbd9daab4145
claim_label: DERIVED
scope: repair of the Wave 13 n3=45 local census, active-local SAT artifact schema, validator, provenance, and hostile regression suite
inputs:
  - agents/2026-07-22-wave13-n3-45-computational.md sha256 f1ace31438aa147018cb8210fa92cd940a0a4795e698bc09d34f3537debf8904
  - verification/2026-07-22-wave13-computation-audit.md sha256 b1914cd618aea228cf0c442c6e6fa94c00faf241ddd8d787ce7ba0ae91f14fa3
  - frozen failed bundle commit 066d9c7fcf593c3b9d35cfef1031dbd9daab4145
method: repair the finite census coverage and replace permissive witness replay with exact schemas, raw canonicality checks, formula reconstruction, source provenance, and full material-metadata integrity binding; then regenerate every derived artifact and run hostile and reproducibility regressions
command: $env:PYTHONPATH='code'; .venv/Scripts/python.exe code/wave13_n3_45_test.py -v
outputs:
  - code/wave13_n3_45_profiles.py sha256 63f38178722cae08723c458e8fd1a3d6bcbadc3f0a9cec2ca50f45c27b13ce92
  - code/wave13_n3_45_active_sat.py sha256 936cd43e3f0efcf38acf19af363d06cb14916a6bb405873c679c8f82d2e91532
  - code/wave13_n3_45_test.py sha256 7b7fbdc455619fec68b540c9621b765ebc9a6cd933c8d495a31c7dd2700a6dd6
  - attempts/wave13-computation/n3-45-local-census.json sha256 6546819c11dbecbf21a4cfaff00b71d338629c045c7bf156493426391b25ac55
  - attempts/wave13-computation/n3-45-active-local-sat-scan.json sha256 a9cdeca479ffb8283a44a742b0afd241333d6f7d55b082af23e177a95d0c707c
  - attempts/wave13-computation/n3-45-no-common-point-m5-111.json sha256 629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8
limitations:
  - no independent verifier has promoted the repaired bundle to VERIFIED
  - all 17 full-formula UNSAT returns remain UNSAT_UNVERIFIED because no proof trace was emitted or checked
  - the positive artifact is only a weakened no_common_point diagnostic, not a target counterexample
  - target_result and novelty_status remain UNKNOWN
  - the repaired worktree was intentionally not committed; git_commit identifies the frozen failed baseline
```

## Outcome

The repaired self-test bundle passes all 12 tests. The repair does not alter
the active-local formula construction, any recorded CNF hash, or the
17-branch cover. It does not repair or overwrite the original report: that
report and the independent audit remain the immutable record that the bundle
at commit `066d9c7fcf593c3b9d35cfef1031dbd9daab4145` failed verification.

The mixed order-fourteen census now exhausts exactly the seven ordered
assignments in `{2,3}^3` containing a `3`:

```text
223 232 233 322 323 332 333
```

All seven have zero local modes. In particular, all three permutations of
`(2,3,3)` and `(3,3,3)` are now explicit. The regression requires the exact
seven-row census, so it fails against the frozen implementation that checked
only the three permutations of `(2,2,3)`.

## Validator and artifact repair

The candidate formats are now strict version-2 schemas:

- `conway99-wave13-n3-45-active-local-v2`;
- `conway99-wave13-n3-45-active-local-diagnostic-v2`.

Unknown or missing fields are rejected at the top level and in the root,
solver-statistics, and diagnostic records. Point and `K` records must be raw
canonical JSON lists, globally ordered, in range, and duplicate-free.
Validation binds and recomputes:

- `active_order`, all `q_values`, `K_degree`, the size-three count, the named
  root, and the root's actual local mode;
- the exact root-normalization justification and the assertion that no
  completed-graph automorphism was assumed;
- the exact restrictions, diagnostic variant, and omitted premise;
- `claim_label=CANDIDATE`, `target_result=UNKNOWN`,
  `novelty_status=UNKNOWN`, and `proof_trace_status=NOT_EMITTED`;
- deterministic solver metadata, formula dimensions, and the exact rebuilt
  DIMACS-stream SHA-256;
- the current builder source SHA-256;
- a core semantic digest and an integrity digest covering every material
  schema field.

Hostile regressions reject removed, duplicate, or reversed `K` edges;
duplicate or reversed points; unknown fields; altered diagnostics; and
forged active order, degree, size-three count, root mode, root normalization,
restrictions, omitted premise, status, or CNF hash. These mutations are also
rejected when the attacker recomputes the public integrity digest. A
full-label relabeling that moves the normalized root is rejected even after
the diagnostics, core digest, and integrity digest are all recomputed.

## Regeneration and invariant hashes

The positive artifact was generated directly by the final repaired source:

```powershell
.venv/Scripts/python.exe code/wave13_n3_45_active_sat.py `
  --size3 5 --root-mode 111 --variant no_common_point `
  --solver cadical195 --conflict-budget 300000 `
  --candidate attempts/wave13-computation/n3-45-no-common-point-m5-111.json `
  --json

.venv/Scripts/python.exe code/wave13_n3_45_active_sat.py `
  --validate attempts/wave13-computation/n3-45-no-common-point-m5-111.json
```

Its replay result is:

```yaml
status: PASS weakened active-local diagnostic
schema: conway99-wave13-n3-45-active-local-diagnostic-v2
cnf_sha256: 8260378538dccf0b3b3355619ceb237d7d6f89e1f3b26d86ea316f7e593df146
core_semantic_sha256: 2492601fb4dbb6dd642d73e34404f446ff8d0f1cee6edfaec7babbba39424e03
integrity_sha256: 5c1758f2a4efc67289ab2e6c987fc31cd75ea4ac9e33eb032cf3a339a13290a1
common_point_Berge_triangle_count: 18
claim_label: CANDIDATE
target_result: UNKNOWN
novelty_status: UNKNOWN
proof_trace_status: NOT_EMITTED
```

The CNF hash and core semantic hash are unchanged from the independently
audited positive core. Two fresh solver runs produced identical candidate
objects, identical integrity digests, and bytes identical to the archived
version-2 artifact.

The census and full branch scan were regenerated with:

```powershell
.venv/Scripts/python.exe code/wave13_n3_45_profiles.py --json `
  --output attempts/wave13-computation/n3-45-local-census.json

.venv/Scripts/python.exe code/wave13_n3_45_active_sat.py --scan `
  --solver cadical195 --conflict-budget 400000 `
  --scan-output attempts/wave13-computation/n3-45-active-local-sat-scan.json
```

The scan again covered all 17 frozen branches. Every row is
`UNSAT_UNVERIFIED`, every row says `proof_trace_status=NOT_EMITTED`, and the
top-level target and novelty statuses are `UNKNOWN`. The exact variables,
clauses, and CNF hashes for all 17 branches are pinned in
`code/wave13_n3_45_test.py`; all match the frozen values.

## Old and new file hashes

| Path | Frozen failed bundle | Repaired worktree |
|---|---|---|
| `code/wave13_n3_45_profiles.py` | `7685a370166c0caa41460d5cbfab3b3a51d28da52441db63f5befeb396e4cf7c` | `63f38178722cae08723c458e8fd1a3d6bcbadc3f0a9cec2ca50f45c27b13ce92` |
| `code/wave13_n3_45_active_sat.py` | `ad4b0c41e7aeebb3f9b9c5d1253c317e59b96d69f3d782f2ea83de655bf052e7` | `936cd43e3f0efcf38acf19af363d06cb14916a6bb405873c679c8f82d2e91532` |
| `code/wave13_n3_45_test.py` | `0d2d4d868618ce714599c014ab0f8ac247c2f240a521848433fe94298bfbd3d3` | `7b7fbdc455619fec68b540c9621b765ebc9a6cd933c8d495a31c7dd2700a6dd6` |
| `attempts/wave13-computation/n3-45-local-census.json` | `f0fcbd3457e5b39f56e68492d2a29ae2f45a5deeff99cc30803178d3f3ee2019` | `6546819c11dbecbf21a4cfaff00b71d338629c045c7bf156493426391b25ac55` |
| `attempts/wave13-computation/n3-45-active-local-sat-scan.json` | `d526bc59b4000a59ff8cc607be89744072a8845763883c8f60af65075bfdd933` | `a9cdeca479ffb8283a44a742b0afd241333d6f7d55b082af23e177a95d0c707c` |
| `attempts/wave13-computation/n3-45-no-common-point-m5-111.json` | `e32486506a5da0607c0deddaced42ff77f059b39abc3ba29923cd5d056762bb0` | `629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8` |

The frozen report hash remains
`f1ace31438aa147018cb8210fa92cd940a0a4795e698bc09d34f3537debf8904`.
The independent FAIL audit hash remains
`b1914cd618aea228cf0c442c6e6fa94c00faf241ddd8d787ce7ba0ae91f14fa3`.

## Commands and test result

```powershell
.venv/Scripts/python.exe -m py_compile `
  code/wave13_n3_45_profiles.py `
  code/wave13_n3_45_active_sat.py `
  code/wave13_n3_45_test.py

$env:PYTHONPATH='code'
.venv/Scripts/python.exe code/wave13_n3_45_test.py -v
```

```text
Ran 12 tests in 24.210s
OK
```
