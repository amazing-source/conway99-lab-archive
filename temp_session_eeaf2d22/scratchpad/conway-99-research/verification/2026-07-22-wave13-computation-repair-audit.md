# Independent audit of the repaired Wave 13 computation bundle

```yaml
role: verifier
date_utc: 2026-07-23T09:11:29Z
git_commit: 3e4da49df2743529bf2d565dbee9580f09eb77e2
claim_label: VERIFIED
scope: >
  The repaired Wave 13 n3=45 computation bundle only: arithmetic and local
  reductions, 17-branch coverage, exact formula streams, the positive
  no-common-point diagnostic, v2 diagnostic schema and validator behavior,
  and source/artifact provenance. VERIFIED is restricted to these bundle
  properties. No solver-negative branch, n3=45 exclusion, project target,
  or novelty claim is promoted.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  agents/2026-07-22-wave13-n3-45-computational.md: f1ace31438aa147018cb8210fa92cd940a0a4795e698bc09d34f3537debf8904
  agents/2026-07-22-wave13-n3-45-computational-repair.md: ed3946befd9c006c440f7fca599652d887c0fdb3c6b1091de6926cfa7f943607
  verification/2026-07-22-wave13-computation-audit.md: b1914cd618aea228cf0c442c6e6fa94c00faf241ddd8d787ce7ba0ae91f14fa3
  code/wave13_n3_45_profiles.py: 63f38178722cae08723c458e8fd1a3d6bcbadc3f0a9cec2ca50f45c27b13ce92
  code/wave13_n3_45_active_sat.py: 936cd43e3f0efcf38acf19af363d06cb14916a6bb405873c679c8f82d2e91532
  code/wave13_n3_45_test.py: 7b7fbdc455619fec68b540c9621b765ebc9a6cd933c8d495a31c7dd2700a6dd6
  attempts/wave13-computation/n3-45-local-census.json: 6546819c11dbecbf21a4cfaff00b71d338629c045c7bf156493426391b25ac55
  attempts/wave13-computation/n3-45-active-local-sat-scan.json: a9cdeca479ffb8283a44a742b0afd241333d6f7d55b082af23e177a95d0c707c
  attempts/wave13-computation/n3-45-no-common-point-m5-111.json: 629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8
  verification/n3-45-computation/independent_audit.py: b2241fe21f0dee7f390f5935577a553eb2537a4642f0f707d087393997f0dcb7
  verification/n3-45-computation/independent_formula_audit.py: c2a1fae2f74e2420d4e89acae627cf40de06ca5301ccffbbb7d19268a045b3c5
  verification/n3-45-computation/test_independent_audit.py: a2a370758c486dc4f5b5914773a283e0557b37f6179635939d7b36f88a85ac0e
method: >
  Fresh adversarial wrapper and schema checker; independent arithmetic,
  rooted-mode, graph, signature, and branch reconstruction; exact use of
  the separately written independent PySAT formula builder without importing
  the repaired formula builder; clause-by-clause positive-model checking;
  independent Berge certificates; 31 refreshed-integrity hostile mutations;
  direct regeneration of the census, scan, and two positive candidates.
command: |
  .venv\Scripts\python.exe --version
  .venv\Scripts\python.exe -c "import platform; import pysat; print(platform.platform()); print(pysat.__version__)"
  $env:PYTHONPATH='code'; .venv\Scripts\python.exe code\wave13_n3_45_test.py -v
  .venv\Scripts\python.exe -m unittest discover -s verification\n3-45-computation -p 'test_*.py' -v
  .venv\Scripts\python.exe verification\n3-45-computation\independent_formula_audit.py --json
  .venv\Scripts\python.exe verification\n3-45-computation-repair\independent_repair_audit.py --output verification\n3-45-computation-repair\independent-repair-audit-result.json
  .venv\Scripts\python.exe -m unittest discover -s verification\n3-45-computation-repair -p 'test_*.py' -v
  .venv\Scripts\python.exe code\wave13_n3_45_profiles.py --output verification\n3-45-computation-repair\local-census-regenerated.json --json
  .venv\Scripts\python.exe code\wave13_n3_45_active_sat.py --scan --solver cadical195 --conflict-budget 400000 --scan-output verification\n3-45-computation-repair\scan-regenerated.json
  .venv\Scripts\python.exe code\wave13_n3_45_active_sat.py --size3 5 --root-mode 111 --variant no_common_point --solver cadical195 --conflict-budget 300000 --candidate verification\n3-45-computation-repair\candidate-generation-1.json --json
  .venv\Scripts\python.exe code\wave13_n3_45_active_sat.py --size3 5 --root-mode 111 --variant no_common_point --solver cadical195 --conflict-budget 300000 --candidate verification\n3-45-computation-repair\candidate-generation-2.json --json
  .venv\Scripts\python.exe code\wave13_n3_45_active_sat.py --validate attempts\wave13-computation\n3-45-no-common-point-m5-111.json
  .venv\Scripts\python.exe code\wave13_n3_45_active_sat.py --validate verification\n3-45-computation-repair\candidate-generation-1.json
  .venv\Scripts\python.exe code\wave13_n3_45_active_sat.py --validate verification\n3-45-computation-repair\candidate-generation-2.json
outputs:
  verification/n3-45-computation-repair/independent_repair_audit.py: 92f748b7d987c05c1bb4da7628a2b83ea3ee60546c35279a7cb89c036cdcc346
  verification/n3-45-computation-repair/independent-repair-audit-result.json: 0418419cbdaf923745914a789b0eefd0ce97fac4b224ee325566504ccfbd3583
  verification/n3-45-computation-repair/test_repair_regressions.py: e6c121e5ed0ea29acb6af9d1edaa668587a1d729e1c506f7a415176ab074be31
  verification/n3-45-computation-repair/local-census-regenerated.json: 6546819c11dbecbf21a4cfaff00b71d338629c045c7bf156493426391b25ac55
  verification/n3-45-computation-repair/scan-regenerated.json: 2a995f3e575938d947e66ff3ac1e0bba1b7a8dd40b72a6ed825134b94dc850d0
  verification/n3-45-computation-repair/candidate-generation-1.json: 629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8
  verification/n3-45-computation-repair/candidate-generation-2.json: 629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8
  repaired_bundle: PASS
  solver_negative_branches: UNSAT_UNVERIFIED
  target_result: UNKNOWN
  novelty_status: UNKNOWN
limitations: >
  The formulas encode only the declared active-local restricted model, not a
  completed 99-vertex graph. No DRAT, FRAT, LRAT, or other negative proof
  trace was emitted or checked. The full v2 candidate validator has no
  positive full-model artifact in this bundle; the archived diagnostic-v2
  artifact and its complete validation path were audited directly. Commit
  identity is the frozen identity supplied to this audit; no Git operation
  was performed. No Wave 14 file was inspected.
```

## Verdict

No critical defect was found in the repaired bundle.

| Component | Verdict | Evidence boundary |
|---|---|---|
| Seven ordered mixed-root assignments | **PASS** | `223,232,233,322,323,332,333` were independently enumerated; each has zero local modes, and all seven rows are present in the repaired census. |
| Nine profiles and reductions | **PASS** | Nine raw profiles, three degree-filter survivors, two degree-three-obstruction survivors, all three flower censuses, and the mixed-profile graph reduction reconstruct. |
| Four order-15 modes and aggregate census | **PASS** | Eight ordered modes in four permutation classes, exactly 59 aggregate signatures, and the exact 17-branch cover reconstruct. |
| Exact full formulas | **PASS** | A separately written builder reproduced variables, clauses, and the complete deterministic DIMACS SHA-256 stream for all 17 branches. All hashes are unchanged from the failed-baseline bundle. |
| Positive diagnostic | **PASS** | The separately rebuilt formula has 328,475 variables and 1,141,796 clauses. A total assignment was checked against every clause with zero failures. The core has exactly 18 independently certified Berge violations. |
| Diagnostic-v2 schema and validator | **PASS** | Exact nested schemas, raw canonicality, all material metadata/status/root/restriction/source/formula bindings, and full top-level integrity coverage passed. All 31 hostile mutations were rejected. |
| Artifact provenance | **PASS** | The census regenerated byte-identically; two fresh positive candidates are mutually byte-identical and byte-identical to the archive; a fresh scan has the same semantic digest and every material branch field. |
| Frozen FAIL audit preservation | **PASS** | Its SHA-256 remains `b1914cd618aea228cf0c442c6e6fa94c00faf241ddd8d787ce7ba0ae91f14fa3`. It was neither edited nor replaced. |
| Seventeen solver-negative rows | **`UNSAT_UNVERIFIED`** | Fresh solver returns agree, but no checked negative proof trace exists. |
| Exclusion of \(n_3=45\), project target, novelty | **UNKNOWN** | This computation audit makes no such promotion. |

## Independent arithmetic and coverage reconstruction

The nine raw \(q\)-profiles were regenerated from
\(\sum q(T)=30\), \(q(T)\ge2\), \(3q(T)\le r-1\), with
\(d_K(T)=r-1-3q(T)\):

| \(r\) | \(q\)-profile | disposition |
|---:|---|---|
| 15 | \(2^{15}\) | survives |
| 14 | \(2^{12}3^2\) | survives the arithmetic obstruction, later removed by the mixed reduction |
| 14 | \(2^{13}4\) | fails the no-singleton degree filter |
| 13 | \(2^9 3^4\) | survives the degree filter, fails the degree-three obstruction |
| 13 | \(2^{11}4^2\) | fails the degree filter |
| 13 | \(2^{10}3^2 4\) | fails the degree filter |
| 12 | \(2^6 3^6\) | fails the degree filter |
| 11 | \(2^3 3^8\) | fails the degree filter |
| 10 | \(3^{10}\) | fails the degree filter |

The repaired mixed-root census is exact:

| ordered \(q\)-assignment | local modes |
|---|---:|
| 223 | 0 |
| 232 | 0 |
| 233 | 0 |
| 322 | 0 |
| 323 | 0 |
| 332 | 0 |
| 333 | 0 |

This directly repairs the failed baseline's omitted `233,323,332,333`
coverage. The all-\(q=2\), order-14 root retains only \(t=222\). Independent
flower enumeration again gives capacity-feasible/degree-survivor counts
\(1/0\), \(157/0\), and \(45/0\) for order-15 size 5, order-15 size 4, and
order-14 size 4. The cubic residual has candidate orders 4 and 6; there are
zero labeled triangle-free cubic graphs at order 4 and ten at order 6, all
\(K_{3,3}\), with the same open-twin injection contradiction.

For order 15, independent enumeration gives eight ordered modes in four
classes:

| sorted \((t,z)\) class | multiplicity |
|---|---:|
| `(1,0),(1,0),(1,0)` | 1 |
| `(1,0),(2,0),(2,0)` | 3 |
| `(2,0),(2,0),(2,0)` | 1 |
| `(2,0),(2,0),(3,1)` | 3 |

The 59 aggregate signatures have histogram
\(2,7,16,21,12,1\) at \(m=1,3,5,7,9,11\). Before the 15-label cap,
the minimum integral label use is 18 at \(m=13\) and 20 at \(m=15\).
The exact rooted cover is therefore:

```text
(1,111)
(3,111) (3,122)
(5,111) (5,122) (5,222) (5,223)
(7,111) (7,122) (7,222) (7,223)
(9,111) (9,122) (9,222) (9,223)
(11,222) (11,223)
```

The normalization is label naming under the full active-label action. The
archived metadata expressly says
`completed_graph_automorphism_assumed=false`; the validator binds that exact
claim and rejects changing it.

## Exact formula reconstruction

The formula reconstruction used
`verification/n3-45-computation/independent_formula_audit.py` at pinned
SHA-256
`c2a1fae2f74e2420d4e89acae627cf40de06ca5301ccffbbb7d19268a045b3c5`.
That builder does not import either repaired Wave 13 discovery module.
It independently constructs the point, \(K\), \(F\), crossing, overlap,
root, and sequential-cardinality clauses and hashes the exact DIMACS stream.

| \(m\) | root | variables | clauses | DIMACS SHA-256 |
|---:|---:|---:|---:|---|
| 1 | 111 | 13,209 | 32,224 | `584e4c7b7f8d366496729dc71da3bbb207e7344fee3d9f59a59fe99fd064580d` |
| 3 | 111 | 15,467 | 338,785 | `445366fc33eccbf5f86daedf6d3678c1cf64cb753f97991a7534157f018f90e0` |
| 3 | 122 | 15,467 | 338,792 | `6eaabc69cae2c83f33b5f8851287527dfdbf6e9616805a74c15b399ee9c41df9` |
| 5 | 111 | 328,475 | 1,142,251 | `613726bf378c1c3d78abdca387e4dbdb686309b228fa3f73ca621d9a77564f34` |
| 5 | 122 | 328,475 | 1,142,258 | `687abee000cf9e3603ac71c1f13fc3544e8afe1af87af443b307cfbc59bd6cad` |
| 5 | 222 | 328,475 | 1,142,262 | `a22446e091fcd382b6089da239a5f1a5d9a7a6a048788c91ea69edaa49e329fd` |
| 5 | 223 | 328,475 | 1,142,266 | `b34c9a5b18f78dd3ed9d232fd150808978bea9a60d12402a2d2e151d7bbf3395` |
| 7 | 111 | 330,247 | 1,145,795 | `c66c51e9c27bd16a47f3c523923a4c8f84f7359b91d8495ed7140dcf3658a174` |
| 7 | 122 | 330,247 | 1,145,802 | `de43df31f717eedbaa566b8278c827f80e4d952fe2e72abaeb1ff0a6ec283e32` |
| 7 | 222 | 330,247 | 1,145,806 | `e00aaef09785d119aec27499d642437387c3e2e445c9dd19aef5e7ca2b3ddeff` |
| 7 | 223 | 330,247 | 1,145,810 | `ba13ba49f105d7cf2ea51ee00b68e1612f2c001c8f7a810751397a61ff0ea99f` |
| 9 | 111 | 332,003 | 1,149,307 | `ab5bf8a6caebd6b8b22d4e19248c884d84695436f12141cbcaab221cbba6a4a7` |
| 9 | 122 | 332,003 | 1,149,314 | `d7934da69aa58fe545363e7e70039f281dfcad5fbf75840e18ce873695b1ed1c` |
| 9 | 222 | 332,003 | 1,149,318 | `5a6ee86c4ac0354814098dd0061a59b84a42b719de1e6dcdca315369544ff8a1` |
| 9 | 223 | 332,003 | 1,149,322 | `de887573e63a96ec7c74b392e5f0c5a6c138c71f9f7132924fd73940ca9e075a` |
| 11 | 222 | 333,743 | 1,152,798 | `7d03e957abf1d2b8993a0cd7c41337b3a05abceaa9b3565947360d0c6ecf40b2` |
| 11 | 223 | 333,743 | 1,152,802 | `6f73c69537a1cfd57dff985a083efa4d547db1da20c8d592951babc3ff11c6a5` |

All 17 archived triples match the independent rebuild, all hashes are
distinct, and every triple is unchanged from the failed baseline. The scan
semantic digest is
`b83e8dba483a4e17d1ae007a39b0dc68670f27391a47a84f71037d537f99b35a`.

## Positive diagnostic

The independently rebuilt \(m=5\), root-111, `no_common_point` formula has:

```text
variables:       328475
clauses:         1141796
DIMACS SHA-256:  8260378538dccf0b3b3355619ceb237d7d6f89e1f3b26d86ea316f7e593df146
fixed primary assumptions: 665
total variables assigned: 328475
clauses checked: 1141796
violated clauses: 0
```

Reconstructing \(F\) as the exact union of selected point-clique pairs gives
exactly these 18 full-model common-point/Berge violations:

```text
0,1,6    0,2,11   0,6,11   1,2,9    1,6,9    2,9,11
3,4,7    3,4,10   3,5,7    3,5,10   4,5,7    4,5,10
4,7,10   5,7,10   8,12,13  8,12,14  8,13,14  12,13,14
```

For every row, the independent certificate identifies three distinct point
owners of the three pairs. Complete owner records are in
`independent-repair-audit-result.json`. The core digest remains
`2492601fb4dbb6dd642d73e34404f446ff8d0f1cee6edfaec7babbba39424e03`.

## Strict schema, integrity, and hostile attacks

The archived positive object has the exact schema
`conway99-wave13-n3-45-active-local-diagnostic-v2`, with:

- 21 exact top-level fields;
- 4 exact root-normalization fields;
- 13 exact solver-statistics fields;
- 15 exact diagnostic fields;
- 20 globally canonical, duplicate-free raw point records; and
- 60 globally canonical, duplicate-free raw \(K\)-edge records.

The independently recomputed integrity digest is
`5c1758f2a4efc67289ab2e6c987fc31cd75ea4ac9e33eb032cf3a339a13290a1`.
Its payload is exactly every top-level schema field other than the digest
itself. The core digest independently binds the variant, raw point records,
raw \(K\) records, and diagnostics. The validator additionally reconstructs
the formula and binds the current builder source
`936cd43e3f0efcf38acf19af363d06cb14916a6bb405873c679c8f82d2e91532`.

All 31 hostile mutations were rejected with `AssertionError`, including:

| Attack family | Result |
|---|---|
| duplicate and reversed raw point records | **rejected** |
| duplicate and reversed raw \(K\) records | **rejected** |
| missing top/root/solver/diagnostic fields | **rejected** |
| unknown top/root/solver/diagnostic fields | **rejected** |
| forged active order, \(q\)-values, \(K\)-degree, size-three count | **rejected after refreshed integrity** |
| forged root mode, justification, or completed-graph automorphism claim | **rejected after refreshed integrity** |
| forged restrictions or omitted premise | **rejected after refreshed integrity** |
| forged claim, target, novelty, or proof-trace statuses | **rejected after refreshed integrity** |
| forged builder source, formula hash, formula clause count, or solver proof-trace metadata | **rejected after refreshed integrity** |
| altered diagnostic count | **rejected after core and integrity digests were both refreshed** |
| full label shift moving the normalized root | **rejected after diagnostics, core digest, and integrity digest were all refreshed** |

The full relabel attack was a shift by three labels. It preserves the
unrooted core structure but moves the selected normalized root away from
\(\{0,1,2\}\). The validator rejected it because the claimed normalized
root was absent. This directly repairs the baseline root-binding defect.

The source also declares a strict full-candidate v2 schema, but no positive
full artifact exists in this bundle, so an end-to-end positive traversal of
that separate path is not claimed here.

## Direct provenance

The final repaired source regenerated the census byte-for-byte:

| object | SHA-256 |
|---|---|
| archived census | `6546819c11dbecbf21a4cfaff00b71d338629c045c7bf156493426391b25ac55` |
| fresh census | `6546819c11dbecbf21a4cfaff00b71d338629c045c7bf156493426391b25ac55` |

Two independent fresh solver executions generated positive candidate bytes
identical to each other and to the archive:

| object | bytes | SHA-256 |
|---|---:|---|
| archived candidate | 6,096 | `629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8` |
| fresh generation 1 | 6,096 | `629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8` |
| fresh generation 2 | 6,096 | `629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8` |

Both fresh runs had the same 5,973 conflicts, 296,834 decisions, 6,844,615
propagations, and 571 restarts. Their wall-clock timings differed, but
runtime timing is intentionally absent from the deterministic candidate.
All three candidate validations returned the same formula, core, and
integrity digests.

A fresh 17-branch scan also came directly from the final source. Its raw
SHA-256 is
`2a995f3e575938d947e66ff3ac1e0bba1b7a8dd40b72a6ed825134b94dc850d0`,
while the archived raw scan SHA-256 is
`a9cdeca479ffb8283a44a742b0afd241333d6f7d55b082af23e177a95d0c707c`.
The raw files differ only in recorded `solver_time_seconds`. Branch cover,
statuses, accumulated solver statistics, formula dimensions and hashes,
source binding, and the semantic digest are identical. Raw scan
byte-reproducibility is therefore not asserted.

## Historical verifier-suite compatibility

The current repair suite passes:

```text
Ran 12 tests in 20.530s
OK
```

The focused independent repair-regression suite also passes:

```text
Ran 6 tests in 5.095s
OK
```

The historical suite under `verification/n3-45-computation` is intentionally
baseline-pinned and is not forward-compatible with the repaired tip:

```text
Ran 15 tests in 5.129s
FAILED (failures=5)
```

The five failures are evidence that the baseline defects disappeared, not
new repaired-tip defects:

1. it expects the archived solver statistics to omit `cnf_sha256`, which v2
   now includes;
2. it expects the frozen validator to accept a relabeled core with its
   claimed root absent, which v2 rejects;
3. it expects the frozen validator to accept a duplicate \(K\) record, which
   v2 rejects;
4. it expects the frozen validator to accept forged unbound metadata, which
   v2 rejects; and
5. its independent strict checker requires the old diagnostic-v1 schema.

Recommended transparent current-tip handling, without changing those files
in this audit:

- retain the historical suite unchanged as the executable record of the
  failed baseline;
- mark or gate it explicitly as a baseline-only suite tied to commit
  `066d9c7fcf593c3b9d35cfef1031dbd9daab4145` and its pinned artifact hashes;
- do not include it unqualified in default current-tip test discovery; and
- use the repaired 12-test suite plus this separate repair-verification path
  as the current-tip checks, while reporting historical-suite failures as
  expected baseline-pin outcomes rather than current regressions.

## Status boundary

Every fresh full-branch solver return is retained as:

```text
UNSAT_UNVERIFIED
```

Neither solver agreement, a solver exit code, conflict statistics, nor an
unchanged formula hash is a negative certificate. There is no checked proof
trace. Consequently:

```text
repaired computation-bundle properties: VERIFIED
17 solver-negative branches:             UNSAT_UNVERIFIED
n3=45 exclusion by this computation:      UNKNOWN
project target:                           UNKNOWN
novelty:                                  UNKNOWN
```
