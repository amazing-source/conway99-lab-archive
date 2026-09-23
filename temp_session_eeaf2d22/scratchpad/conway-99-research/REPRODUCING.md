# Reproducing results

## Trust model

Discovery code may be complicated, optimized, randomized, or wrong. A result
is promoted only when a small independent checker validates a complete
certificate using exact arithmetic.

The minimum positive certificate is a 99-vertex edge list or adjacency matrix.
The canonical validator checks, from scratch:

1. input syntax and vertex count;
2. simplicity, symmetry, and zero diagonal;
3. degree 14 at every vertex;
4. exactly one common neighbor for every edge;
5. exactly two common neighbors for every nonedge; and
6. the integer matrix identity `A^2 = 12 I - A + 2 J`.

Checks 3--5 and check 6 are deliberately redundant implementations of the
same mathematics. A second validator should use a different representation or
language.

## Environment policy

- Pin interpreter, solver, and package versions in every run manifest.
- Record operating system, CPU, wall time, command, random seed, input hashes,
  output hashes, and Git commit.
- Keep exact integer/rational artifacts; floating-point output can guide a
  search but cannot certify a claim.
- Calibrate encodings on known strongly regular graphs and known infeasible
  parameter sets before running the target instance.
- Verify SAT/UNSAT results independently. For UNSAT, retain a checkable proof
  artifact such as LRAT when technically feasible.

Create the optional search environment without changing the global Python
installation:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --requirement requirements-search.txt
```

The independent validators do not import this environment or trust its solver
bindings.

## Baseline commands

Run the test suite and the known-positive `srg(9,4,1,2)` calibration fixture:

```powershell
python -m unittest discover -s verification -p "test_*.py" -v
python verification/check_srg.py `
  verification/fixtures/rook-3x3.srg.json `
  --vertices 9 --degree 4 --lambda 1 --mu 2
powershell -NoProfile -ExecutionPolicy Bypass -File verification/Check-Srg.ps1 `
  -Certificate verification/fixtures/rook-3x3.srg.json `
  -Vertices 9 -Degree 4 -AdjacentCommon 1 -NonadjacentCommon 2
```

Check the deterministic rooted scaffold and its constraint counts:

```powershell
python code/root_model.py
python code/matching_orbits.py
```

Run the SAT encoding's positive and negative calibration cases:

```powershell
.venv\Scripts\python -m unittest discover -s code -p "test_*.py" -v
.venv\Scripts\python code/sat_model.py --pair-count 2 --solve `
  --candidate candidates/calibration-srg-9.srg.json
python verification/check_srg.py candidates/calibration-srg-9.srg.json `
  --vertices 9 --degree 4 --lambda 1 --mu 2
```

Run the native-cardinality discovery backend on the same positive control, or
make a bounded non-evidentiary pass over all complete target branches:

```powershell
.venv\Scripts\python code/sat_model.py --pair-count 2 `
  --cardinality native --solve
.venv\Scripts\python code/scout_branches.py --cardinality native `
  --fresh-solvers --conflict-budget 100000 `
  --output logs/local/native-100000.json
```

The embedded MiniCard solve is discovery-only, but the native formula now has
an exact archival export. Generate the canonical LF OPB positive and negative
controls with:

```powershell
.venv\Scripts\python code/sat_model.py --pair-count 2 `
  --cardinality native --opb formal/opb-calibration/pair2.opb
.venv\Scripts\python code/sat_model.py --pair-count 3 `
  --cardinality native --opb formal/opb-calibration/pair3.opb
```

The committed formulas, raw VeriPB proofs, and elaborated CakePB-compatible
proofs replay as documented in
`verification/2026-07-22-veripb-calibration.md`. The same exporter can produce
the target formula:

```powershell
.venv\Scripts\python code/sat_model.py --pair-count 7 `
  --cardinality native --opb logs/local/conway99-native-lf.opb
```

The independently audited theorem-forced normalization is available only for
the target:

```powershell
.venv\Scripts\python code/sat_model.py --pair-count 7 --n3 `
  --cardinality native --opb logs/local/conway99-n3-native-lf.opb
```

Fixing the N3 witness changes the stabilizer, so the old 11 representatives
remain incompatible and the CLI rejects that combination. Use the separately
verified 12-branch cover instead:

```powershell
.venv\Scripts\python code/matching_orbits.py --n3-joint
.venv\Scripts\python verification/n3-joint-cover/verify.py
1..12 | ForEach-Object {
  $branch = '{0:D2}' -f $_
  .venv\Scripts\python code/sat_model.py --pair-count 7 `
    --cardinality native --n3 --n3-branch $_ `
    --opb "logs/local/conway99-n3-branch-$branch.opb"
}
```

All 12 branches together cover the normalized search. They act on the
invariant shared fiber `S_2`; the legacy `S_0` fiber is moved by part of the
stabilizer and has 78 orbits under its preserving subgroup. The exact
derivation, public certificate, and independent audit are in
`agents/2026-07-22-wave5-n3-joint-cover.md` and
`verification/2026-07-22-n3-joint-cover-audit.md`.

Reproduce the verified second-stage refinement with:

```powershell
.venv\Scripts\python code\matching_orbits.py --n3-refined
.venv\Scripts\python verification\n3-refined-cover\verify.py
1..78 | ForEach-Object {
  $branch = '{0:D3}' -f $_
  .venv\Scripts\python code\sat_model.py --pair-count 7 `
    --cardinality native --n3 --n3-refined-branch $_ `
    --opb "logs/local/conway99-n3-refined-$branch.opb"
}
```

The 78 cases cover the same normalized search more finely. They combine one
of the twelve shared-fiber matchings with the forced choice of an additional
coordinate-4 neighbor. The standalone checker verifies the full finite cover;
generating or briefly solving the OPBs does not establish a target result.

Replay the exact arithmetic for the conditional `n3 >= 24` structural bound
and its twelve branch-local refinements with:

```powershell
.venv\Scripts\python verification\n3-count-bound\verify.py
```

The corresponding human derivation and its source boundary are recorded in
`agents/2026-07-22-wave6-opposite-edge-graph.md` and
`verification/2026-07-22-n3-count-bound-audit.md`.

Replay the Wave 7 strengthening from `n3>=24` to `n3>=30` with two
independent standard-library implementations:

```powershell
.venv\Scripts\python verification\n3-side-incidence\verify.py
.venv\Scripts\python verification\n3-side-incidence\audit_generic.py
```

The first checker follows the complement-component analysis directly. The
second generates all admissible point-clique families, permits unused
complement edges, and adds singleton fillers. Their scope and clean-source
replay are recorded in
`verification/2026-07-22-n3-side-incidence-audit.md` and
`verification/2026-07-22-wave7-clean-clone.md`.

Replay the Wave 8 exclusion of the remaining equality case `n3=30` with:

```powershell
.venv\Scripts\python verification\n3-equality\verify.py
.venv\Scripts\python -m unittest verification.test_n3_equality -v
```

The compact checker is an arithmetic regression companion to the human
proof. An optional independent census audit regenerates all 21 cubic types,
674,880 point-clique families, and the committed exact JSON certificate. It
uses only the standard library but takes about five minutes:

```powershell
.venv\Scripts\python verification\n3-equality\audit_exhaustive.py `
  --check verification\n3-equality\n3-30-audit.json
```

The derivation, adversarial audit, and frozen-commit replay are recorded in
`agents/2026-07-22-wave8-n3-equality.md`,
`verification/2026-07-22-n3-equality-audit.md`, and
`verification/2026-07-22-wave8-clean-clone.md`. They establish the conditional
necessary bound `n3>=33`, not a target construction or nonexistence proof.

Replay the Wave 9 exclusion of `n3=33` with:

```powershell
.venv\Scripts\python verification\n3-33-equality\verify.py
.venv\Scripts\python -m unittest verification.test_n3_33_equality -v
```

The optional exhaustive secondary audit uses the complete connected quartic
order-11 catalog from House of Graphs, attributed there to Meringer's
`genreg`. The catalog is hashed but not vendored. Download and verify it, then
regenerate the scratch certificate and replay it independently:

```powershell
$wave9Catalog = Join-Path ([System.IO.Path]::GetTempPath()) "11_4_3.g6.gz"
$wave9Certificate = Join-Path ([System.IO.Path]::GetTempPath()) "n3-33-audit.json"
$wave9Replay = Join-Path ([System.IO.Path]::GetTempPath()) "n3-33-replay.json"
Invoke-WebRequest `
  -Uri "https://houseofgraphs.org/data/quartics/11_4_3.g6.gz" `
  -OutFile $wave9Catalog
$wave9CatalogHash = (Get-FileHash $wave9Catalog -Algorithm SHA256).Hash.ToLower()
if ($wave9CatalogHash -ne "05ee6bb0c2b40d63d5c44efc8e89ed1c0a381a170d81a3d052749c8edf6b14fd") {
  throw "unexpected Wave 9 catalog hash: $wave9CatalogHash"
}
.venv\Scripts\python verification\n3-33-equality\audit_exhaustive.py `
  --catalog $wave9Catalog --certificate $wave9Certificate `
  --git-commit 19f27d1ede9cdb0b4110540f52eeb3ad9c94cc94
.venv\Scripts\python verification\n3-33-equality\verify_exhaustive.py `
  --catalog $wave9Catalog --certificate $wave9Certificate `
  --output $wave9Replay
```

The expected census is 266 quartic types, 610 admissible point-clique
families, and zero survivors. The derivation, precise-status search,
adversarial audit, deterministic manifest, and clean replay are recorded in
`agents/2026-07-22-wave9-n3-33-equality.md`,
`agents/2026-07-22-wave9-status-search.md`,
`verification/2026-07-22-n3-33-equality-audit.md`,
`verification/n3-33-equality/n3-33-census-manifest.json`, and
`verification/2026-07-22-wave9-clean-clone.md`. They establish the conditional
necessary bound `n3>=36`; Conway-99 remains `UNKNOWN`.

Replay the Wave 10 exclusion of `n3=36` with:

```powershell
.venv\Scripts\python verification\n3-36-equality\verify.py
.venv\Scripts\python -m unittest verification.test_n3_36_equality -v
.venv\Scripts\python verification\n3-36-equality\verify_support.py `
  --certificate verification\n3-36-equality\n3-36-support.json
.venv\Scripts\python -m unittest verification.test_n3_36_support -v
```

The primary and independent support implementations use different enumeration
strategies. To regenerate the certificate in a scratch path from the technical
commit and replay it independently:

```powershell
$wave10Certificate = Join-Path ([System.IO.Path]::GetTempPath()) "n3-36-support.json"
.venv\Scripts\python verification\n3-36-equality\audit_support.py `
  --certificate $wave10Certificate `
  --git-commit 2194c2b68ebd5c34491d64f15d30f1a3597baa74
.venv\Scripts\python verification\n3-36-equality\verify_support.py `
  --certificate $wave10Certificate
```

The expected domain has 14 integer resource profiles before local pruning,
100 labeled point families in the forced `2K6` case, one point-family orbit,
216 abstract support masks, and zero survivors after the original-SRG
`lambda`/`mu` saturation check. The mask digest is
`6659fe1972cbacc6980a9792557714730572817b43224b5f1fac24bb0c4ca61a`.
The derivation, status search, adversarial audit, and clean replay are recorded
in `agents/2026-07-22-wave10-n3-36-equality.md`,
`agents/2026-07-22-wave10-status-search.md`,
`verification/2026-07-22-n3-36-equality-audit.md`, and
`verification/2026-07-22-wave10-clean-clone.md`. They establish only the
conditional necessary bound `n3>=39`; Conway-99 remains `UNKNOWN`.

Replay the Wave 11 exclusion of `n3=39` with:

```powershell
.venv\Scripts\python verification\n3-39-equality\verify.py
.venv\Scripts\python verification\n3-39-equality\verify_local.py `
  --certificate verification\n3-39-equality\n3-39-local.json
.venv\Scripts\python -m unittest -v `
  verification/test_n3_39_equality.py verification/test_n3_39_local.py
```

The committed certificate is bound to replay-code commit
`c299b88fbd956c813ff3379ff236b3123a90d242`. To regenerate it in a scratch
path and replay it independently:

```powershell
$wave11Certificate = Join-Path ([System.IO.Path]::GetTempPath()) "n3-39-local.json"
.venv\Scripts\python verification\n3-39-equality\audit_local.py `
  --certificate $wave11Certificate `
  --git-commit c299b88fbd956c813ff3379ff236b3123a90d242
.venv\Scripts\python verification\n3-39-equality\verify_local.py `
  --certificate $wave11Certificate
```

The expected replay has 8,907 records, 1,730,729 canonical JSONL bytes, and
combined SHA-256
`452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1`.
The outer JSON certificate is emitted with canonical LF bytes and has
SHA-256 `4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261`.
The two implementations use different enumeration mechanisms, freeze all nine
stream hashes, and reject eight premise, digest, conclusion, and status
mutations. The result is only the conditional necessary bound `n3>=42`;
Conway-99 remains `UNKNOWN`. The detached-clone procedure, first failed
newline-portability gate, canonical-LF repair, and exact byte comparison are
recorded in `verification/2026-07-22-wave11-clean-clone.md`.

Replay the Wave 12 exclusion of `n3=42` with:

```powershell
.venv\Scripts\python code\wave12_n3_42_active.py `
  --certificate attempts\wave12-computation\n3-42-size2-active-local-candidate.json
.venv\Scripts\python code\wave12_n3_42_size2_scout.py `
  --compare attempts\wave12-computation\n3-42-size2-active-local-candidate.json
.venv\Scripts\python code\wave12_n3_42_size2_caps.py `
  --catalog attempts\wave12-computation\n3-42-cubic-trianglefree-14.g6
.venv\Scripts\python code\test_wave12_n3_42.py -v
.venv\Scripts\python verification\n3-42-equality\verify_reduction.py
.venv\Scripts\python -m unittest verification.test_n3_42_reduction -v
```

The independent catalog replay uses Meringer's official 871-byte GENREG
shortcode archive. It is not redistributed because its source page states no
license. Download it from the official host and verify its exact digest:

```powershell
$wave12Scd = 'verification\n3-42-equality\14_3_4.scd'
$wave12ScdSha = '6f3e9cf2b7e0d85c5df59c1638ab9d2fddbfc9905c49b35da01cc892f847e9a0'
Invoke-WebRequest `
  -Uri 'https://www.mathe2.uni-bayreuth.de/markus/REGGRAPHS/SCD/14_3_4.scd' `
  -OutFile $wave12Scd
if ((Get-FileHash $wave12Scd -Algorithm SHA256).Hash.ToLower() -ne $wave12ScdSha) {
  throw 'Wave 12 GENREG archive hash mismatch'
}

$wave12Certificate = Join-Path ([System.IO.Path]::GetTempPath()) `
  'n3-42-support-certificate.json'
.venv\Scripts\python verification\n3-42-equality\build_support_certificate.py `
  --scd $wave12Scd `
  --graph6 attempts\wave12-computation\n3-42-cubic-trianglefree-14.g6 `
  --output $wave12Certificate
$wave12Expected = '8115b5f34568a463952afc399bc22db927121f3f1aa28cfc33ae191ea93dc68a'
if ((Get-FileHash $wave12Certificate -Algorithm SHA256).Hash.ToLower() -ne $wave12Expected) {
  throw 'Wave 12 regenerated certificate hash mismatch'
}
.venv\Scripts\python verification\n3-42-equality\verify_support_certificate.py `
  --certificate verification\n3-42-equality\n3-42-support-certificate.json `
  --scd $wave12Scd `
  --graph6 attempts\wave12-computation\n3-42-cubic-trianglefree-14.g6 `
  --mutations
```

The catalog audit decodes 110 connected GENREG types, independently classifies
two disconnected types, and matches all 112 graph6 records. Four types survive
the mandatory-degree filter and zero support factors survive the exact replay.
Combined with the separately checked proof reduction, this establishes only the
conditional necessary bound `n3>=45` and
`induced_C6_count>=209331`. Conway-99 and novelty remain `UNKNOWN`. See
`verification/2026-07-22-n3-42-support-audit.md` and
`verification/2026-07-22-wave12-integration-audit.md`. The complete detached
replay is recorded in `verification/2026-07-22-wave12-clean-clone.md`.

Replay the Wave 13 conditional exclusion of `n3=45` with two independent
semantic checkers:

```powershell
.venv\Scripts\python verification\n3-45-equality\verify.py --mutations
.venv\Scripts\python -m unittest verification.test_n3_45_audit -v
.venv\Scripts\python verification\n3-45-equality-b\audit_semantics.py
```

The frozen proof report has SHA-256
`e721614256f003d7266d0b3d1bb2f884febbdec33893f92ed18bf8961c6958e8`.
Both semantic audits return the conditional bounds `n3>=48` and
`induced_C6_count>=209334`, with target and novelty `UNKNOWN`. The second
verdict was frozen before it read the first audit. Neither checker assumes a
completed-graph automorphism, connectedness, or transitivity.

Replay the repaired Wave 13 computation bundle separately:

```powershell
$env:PYTHONPATH='code'
.venv\Scripts\python code\wave13_n3_45_test.py -v
.venv\Scripts\python verification\n3-45-computation-repair\independent_repair_audit.py
.venv\Scripts\python -m unittest discover `
  -s verification\n3-45-computation-repair -p 'test_*.py' -v
.venv\Scripts\python -m unittest discover `
  -s verification\n3-45-computation -p 'test_*.py' -v
```

The last command is the historical FAIL-audit suite. At the current tip it
loads the defective validator and artifact directly from frozen commit
`066d9c7fcf593c3b9d35cfef1031dbd9daab4145`, so its 15 tests continue to
exercise the original defects rather than the repaired v2 files. The current
repair suite has 12 tests and the independent repair suite has six.

For direct provenance replay, regenerate the census and positive diagnostic:

```powershell
$wave13Census = Join-Path ([System.IO.Path]::GetTempPath()) `
  'n3-45-local-census.json'
$wave13Candidate = Join-Path ([System.IO.Path]::GetTempPath()) `
  'n3-45-no-common-point-m5-111.json'
.venv\Scripts\python code\wave13_n3_45_profiles.py `
  --output $wave13Census --json
.venv\Scripts\python code\wave13_n3_45_active_sat.py `
  --size3 5 --root-mode 111 --variant no_common_point `
  --solver cadical195 --conflict-budget 300000 `
  --candidate $wave13Candidate --json
.venv\Scripts\python code\wave13_n3_45_active_sat.py `
  --validate $wave13Candidate
```

The expected census SHA-256 is
`6546819c11dbecbf21a4cfaff00b71d338629c045c7bf156493426391b25ac55`;
the expected positive artifact SHA-256 is
`629cf0dd9f67b71072e94037161d99891f16c90c330b7d5746ed8a86ac8ba1e8`.
The independent audit rebuilds all 17 formula streams, checks all 1,141,796
positive clauses, certifies exactly 18 violations of the deliberately omitted
common-point premise, and rejects 31 hostile mutations. The original bundle's
FAIL audit and its later repair are both retained. No checked proof trace
exists for any solver-negative row, so every such row remains
`UNSAT_UNVERIFIED` and is not evidence for the `n3=45` exclusion. The detached
52-code-test, 12-focused-test, and 104-verification-test replay is recorded in
`verification/2026-07-22-wave13-clean-clone.md`.

Replay the Wave 14 `n3=48` structural frontier and its explicit
all-size-two relaxation object:

```powershell
.venv\Scripts\python -B attempts\wave14-proof-a\profile_modes.py
.venv\Scripts\python -B attempts\wave14-proof-a\verify_all2_countermodel.py `
  attempts\wave14-proof-a\all2-active-countermodel.json
.venv\Scripts\python -B -m unittest -v `
  attempts\wave14-proof-a\test_wave14_proof_a.py
.venv\Scripts\python -B verification\n3-48-proof\independent_reconstruction.py
.venv\Scripts\python -B verification\n3-48-proof\audit_countermodel.py `
  attempts\wave14-proof-a\all2-active-countermodel.json
```

Replay the separate active-local computation and its independent audit:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.venv\Scripts\python code\wave14_n3_48_verify.py `
  --output attempts\wave14-computation\n3-48-independent-validation.json
.venv\Scripts\python code\wave14_n3_48_test.py -v
.venv\Scripts\python verification\n3-48-computation\independent_audit.py
```

The proof audit reproduces twelve raw profiles, three inherited survivors,
both mixed-profile exclusions, and the exact unresolved `r=16` support
residual. The computation audit independently rebuilds thirteen formulas,
checks one full positive object and two weakened controls, and rejects 29
hostile mutations. Its raw scan remains exactly `1 SAT_CANDIDATE`,
`7 UNSAT_UNVERIFIED`, `1 BUDGET_UNKNOWN`, and `2 TIMEOUT_UNKNOWN`. None of
the seven negative rows has a checked proof trace. Wave 14 therefore leaves
the verified bound at `n3>=48` and `induced_C6_count>=209334`; equality,
Conway-99, and novelty remain `UNKNOWN`.

Replay the Wave 15 global-lift certificate, submitted checks, and independent
audit from the repository root:

```powershell
.venv\Scripts\python -B `
  attempts\wave15-global-lift\build_subset_moment_certificate.py `
  --countermodel attempts\wave14-proof-a\all2-active-countermodel.json `
  --output verification\n3-48-global-lift\regenerated-certificate.json
.venv\Scripts\python -B `
  attempts\wave15-global-lift\verify_subset_moment_certificate.py `
  attempts\wave15-global-lift\subset-moment-certificate.json
.venv\Scripts\python -B -m unittest -v `
  attempts\wave15-global-lift\test_subset_moment.py
.venv\Scripts\python -B `
  verification\n3-48-global-lift\independent_check.py

$wave15Python = (Resolve-Path '.venv\Scripts\python.exe').Path
Push-Location verification\n3-48-global-lift
& $wave15Python -B -m unittest -v test_independent_check.py
Pop-Location
```

The submitted certificate and independently regenerated certificate must be
byte-identical LF files with SHA-256
`cb02ab80f92d7d2c8ec5140e3be2916354976442aa2e1869524aa728c73bd386`.
The verifier-directory change is intentional: that focused suite imports its
sibling checker. The first repository-root invocation of that suite failed
before collecting tests; the corrected working directory and failure are
both recorded in the audit trail.

Replay the independent algebraic lane and its adversarial checker from the
repository root:

```powershell
.venv\Scripts\python -B attempts\wave15-algebraic\exact_checks.py `
  --output attempts\wave15-algebraic\exact-checks.json
.venv\Scripts\python -B `
  verification\n3-48-algebraic\independent_check.py `
  --artifact attempts\wave15-algebraic\exact-checks.json
.venv\Scripts\python -B -m unittest -v `
  verification\n3-48-algebraic\test_independent_check.py
```

The algebraic JSON must have SHA-256
`a6c9109e4fcfcdd2f5a8f5d4299ac1b4cf4037b8f1e4c468b4ecd75aba762512`.
These commands pass 5 submitted global tests, 11 independent global tests,
and 7 independent algebraic tests. They verify the conditional exclusion
`n3!=48`, hence `n3>=51` and `induced_C6_count>=209337`; they do not resolve
Conway-99 or establish novelty.

Replay the Wave 16 structural proof companion and independent verifier:

```powershell
.venv\Scripts\python -B `
  attempts\wave16-n3-51-structural\exact_check.py `
  --verify attempts\wave16-n3-51-structural\exact-checks.json
.venv\Scripts\python -B -m unittest -v `
  attempts\wave16-n3-51-structural\test_exact_check.py
.venv\Scripts\python -B `
  verification\n3-51-structural\independent_check.py

$wave16Python = (Resolve-Path '.venv\Scripts\python.exe').Path
Push-Location verification\n3-51-structural
& $wave16Python -B -m unittest -v test_independent_check.py
Pop-Location
```

The submitted suite passes 8 tests and the independent suite passes 24. The
checker pins repaired discovery report hash
`95d04a774397332417c9613718fe6699a5392ef5222fef1cfa00b12e2860af3f`
and final Wave 15 audit hash
`edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036`,
while retaining the failed baseline and intermediate hashes as historical
provenance. These checks verify the conditional `n3=51` exclusion and the
bounds `n3>=54`, `induced_C6_count>=209340`.

Replay the separate Wave 16 active-local computational archive:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.venv\Scripts\python -B code\wave16_n3_51_profiles.py `
  --output verification\n3-51-computation\regenerated-profile-census.json
.venv\Scripts\python -B code\wave16_n3_51_verify.py `
  --output verification\n3-51-computation\submitted-validation-replay.json
.venv\Scripts\python -B code\wave16_n3_51_test.py -v
.venv\Scripts\python -B `
  verification\n3-51-computation\independent_check.py `
  --output verification\n3-51-computation\independent-audit.json
.venv\Scripts\python -B `
  verification\n3-51-computation\test_independent_check.py -v
```

The independent audit rebuilds all seven DIMACS streams, fixes the raw
24-point/69-edge candidate into its rebuilt positive CNF, rejects 38 hostile
mutations, and passes 4 tests; the submitted suite passes 8. Regenerated
profile and validation artifacts are byte-identical. The archive status is
exactly `1 SAT_CANDIDATE`, `5 TIMEOUT_UNKNOWN`, `1 UNSAT_UNVERIFIED`, plus
one historical `BUDGET_UNKNOWN`. No negative row has a checked proof trace,
and none is used in the human exclusion.

The non-computational literature record is preserved in
`agents/2026-07-23-wave16-status-search.md` and independently checked in
`verification/2026-07-23-wave16-status-audit.md`. These reports record their
exact query families, source URLs, page locations, source-file hashes where
available, access failures, and the 2026-07-23 cutoff. Their search nonhits do
not reproduce a mathematical conclusion or establish novelty. The complete
detached replay is recorded in
`verification/2026-07-23-wave16-clean-clone.md`.

Replay the Wave 17 `n3=54` structural reduction and independent audit:

```powershell
.venv\Scripts\python.exe -B `
  attempts\wave17-n3-54-structural\exact_check.py
.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave17-n3-54-structural\test_exact_check.py
.venv\Scripts\python.exe -B `
  verification\n3-54-structural\independent_check.py
.venv\Scripts\python.exe -B -m unittest -v `
  verification\n3-54-structural\test_independent_check.py
```

The submitted suite passes 7 tests and the independent suite passes 21. They
verify the six-profile reduction, equality/equitable cut, exact `F/R`
representation, `3K3,3` parity exclusion, and the two remaining catalog
families. The restricted SAT controls may also return raw `UNSAT`, but they
emit no checked proof trace and are not evidence.

Replay the exact 457-case census and its separately written verifier without
overwriting committed artifacts:

```powershell
$wave17ReplayStem = [guid]::NewGuid().ToString('N')
$wave17ReplayRoot = [System.IO.Path]::GetTempPath()
$wave17Raw = Join-Path $wave17ReplayRoot "$wave17ReplayStem-raw.json"
$wave17Certificate = Join-Path $wave17ReplayRoot "$wave17ReplayStem-certificate.json"
$wave17Independent = Join-Path $wave17ReplayRoot "$wave17ReplayStem-independent.json"

.venv\Scripts\python.exe -B `
  attempts\wave17-n3-54-census\census.py `
  --model-limit 100000 --output $wave17Raw
.venv\Scripts\python.exe -B `
  attempts\wave17-n3-54-census\build_certificate.py `
  --output $wave17Certificate
.venv\Scripts\python.exe -B `
  attempts\wave17-n3-54-census\verify_certificate.py `
  attempts\wave17-n3-54-census\exact-certificate.json
.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave17-n3-54-census\test_certificate.py
.venv\Scripts\python.exe -B `
  verification\n3-54-census\independent_verifier.py `
  --output $wave17Independent
.venv\Scripts\python.exe -B -m unittest -v `
  verification\n3-54-census\test_independent_verifier.py

Get-FileHash -Algorithm SHA256 $wave17Raw,$wave17Certificate,$wave17Independent
```

The expected SHA-256 values are:

```text
raw census:            f81158e9dacbb4b83bdbc3f19724c304b9dc10a550297661f68272f0d83cdeb2
exact certificate:     f5c66a2ba6ee0c8b0d4ea4a15411366000faf03fdcb431e19f26747d117ced12
independent result:    159903af624a2df1975dd490ea5c267e453b5a96fe9744a9aa7a7be28390b056
```

Both implementations fetch the official House of Graphs catalogs into
memory, validate compressed and decompressed hashes, decode every record, and
reconstruct all 457 cases. The discovery tests pass 6/6 and the independent
hostile tests pass 17/17. The exact proof uses parity-kernel exhaustion and a
mixed-component degree count, not the archived proofless SAT statuses. The
audited consequence is the conditional necessary bound `n3>=57`, hence
`induced_C6_count>=209343`; Conway-99 and novelty remain `UNKNOWN`. The
separate literature reports are
`agents/2026-07-23-wave17-status-search.md` and
`verification/2026-07-23-wave17-status-audit.md`.

Replay the Wave 18 direct exclusion of conditional `n3=57` and its separately
written verifier without overwriting the committed discovery artifact:

```powershell
$wave18ReplayStem = [guid]::NewGuid().ToString('N')
$wave18ReplayRoot = [System.IO.Path]::GetTempPath()
$wave18Exact = Join-Path $wave18ReplayRoot "$wave18ReplayStem-exact.json"

.venv\Scripts\python.exe -B `
  attempts\wave18-n3-57-structural\exact_check.py `
  --output $wave18Exact
.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave18-n3-57-structural\test_exact_check.py
.venv\Scripts\python.exe -B `
  attempts\wave18-n3-57-structural\exact_check.py `
  --verify attempts\wave18-n3-57-structural\exact-checks.json
.venv\Scripts\python.exe -B `
  verification\n3-57-structural\independent_checker.py
.venv\Scripts\python.exe -B -m unittest -v `
  verification\n3-57-structural\test_independent_checker.py

Get-FileHash -Algorithm SHA256 $wave18Exact
Get-FileHash -Algorithm SHA256 `
  verification\n3-57-structural\checker-results.json, `
  verification\n3-57-structural\mutation-results.json
```

The expected SHA-256 values are:

```text
regenerated exact checks: 76decce7f0af8e3bf2db483096a10a86321a9d7143e6123ad2081ec17d28604c
independent results:      1e640f9e3a0d754f60f66638c481f01ce878ef6ccdc140c2ad79aada903aaf1d
mutation results:         eb5f4204e625bfa07f1a4f1e3c99940adacde68d73a0ae07bec1429ea7c40f59
```

The submitted suite passes 10/10 tests and the independent suite passes 14/14.
The independent checker detects all 24 frozen mutations and reconstructs all
nine `sum q=38` profiles, the endpoint crossing tables, the `r=18` equality
branches, both `r=19` active-set sizes, and exact rational spectral caps.
Wave 18 excludes `n3=57` without importing Wave 17; combining the two audited
waves gives the conditional necessary bound `n3>=60`, hence
`induced_C6_count>=209346`. Conway-99 and novelty remain `UNKNOWN`.
The source-first literature record and its independent audit are
`agents/2026-07-23-wave18-status-search.md` and
`verification/2026-07-23-wave18-status-audit.md`. They also preserve the
exact `1^20,2^51` correction to Ishihara's equation (88), while keeping both
target outcomes and Wave 18 novelty `UNKNOWN`.
The detached end-to-end release replay is recorded in
`verification/2026-07-23-wave18-clean-clone.md`.

Replay the canonical Wave 19 `n3=60` release and its separately written
verifier without overwriting committed artifacts:

```powershell
.venv\Scripts\python.exe -B -m unittest -v `
  attempts.wave19-alternate-frontier.test_exact_frontier
.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\n3-60-closure `
  -p test_independent_baseline.py -v
.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\n3-60-closure `
  -p test_independent_closure_verifier.py -v

$wave19ReplayStem = [guid]::NewGuid().ToString('N')
$wave19ReplayRoot = [System.IO.Path]::GetTempPath()
$wave19Independent = Join-Path $wave19ReplayRoot `
  "$wave19ReplayStem-independent-full.json"
.venv\Scripts\python.exe -B `
  verification\n3-60-closure\independent_closure_verifier.py `
  --phase all --output $wave19Independent
Get-FileHash -Algorithm SHA256 $wave19Independent
```

The expected independent JSON SHA-256 is
`c8fb3af52d5a929d7d88b59ef53b8825a3b2d922fdb3fad1ac4208078a27a2a2`.
The submitted suite passes 7/7 tests, the independent baseline passes 27/27,
and the focused independent verifier passes 10/10. The full verifier downloads
and validates the six pinned official cubic catalogs, reproduces all 510,489
connected and 177 disconnected dispositions, reconstructs the two-Petersen
orbit, exhausts every allowed `Z` through three edges, and replays the exact
Gram/Farkas obstruction. The official catalog completeness assertion remains
an external premise. The audited consequence is the conditional bound
`n3>=63`, hence `induced_C6_count>=209349`; Conway-99 and novelty remain
`UNKNOWN`. The detached end-to-end replay is recorded in
`verification/2026-07-23-wave19-clean-clone.md`.

Replay the Wave 20 global Schur-projector arithmetic and the separately
written independent implementation from the repository root:

```powershell
.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave20-global-obstruction `
  -p test_exact_check.py -v
.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave20-global-obstruction\independent-verifier `
  -p test_independent_check.py -v

$wave20ReplayStem = [guid]::NewGuid().ToString('N')
$wave20ReplayRoot = [System.IO.Path]::GetTempPath()
$wave20Submitted = Join-Path $wave20ReplayRoot `
  "$wave20ReplayStem-submitted.json"
$wave20Independent = Join-Path $wave20ReplayRoot `
  "$wave20ReplayStem-independent.json"

.venv\Scripts\python.exe -B `
  attempts\wave20-global-obstruction\exact_check.py `
  --output $wave20Submitted
.venv\Scripts\python.exe -B `
  attempts\wave20-global-obstruction\independent-verifier\independent_check.py `
  --output $wave20Independent
Get-FileHash -Algorithm SHA256 $wave20Submitted,$wave20Independent
```

The expected submitted and independent SHA-256 values are, respectively,

```text
6aea5c4688880a33d358ccc8992ef3aa63d40be70b5c450a8a39bf83b4878dc2
575939f9abe19e5578a2efd1155495877c2080944c75cc0db6702c21a9ce2637
```

The submitted suite passes 18/18 and the independent suite passes 16/16.
They reconstruct the triangle-incidence spectrum, all 13 fixed-triangle
profiles, the rank-44 projector, the Schur trace, the mod-two nonzero-row
condition, the alternating mod-two lemma, the mod-four diagonal floor, and
the final divisibility endpoint. The audited conditional consequence is
`n3>=705`, hence `induced_C6_count>=209991`. No automorphism, graph catalog,
solver-negative, or floating-point premise is used. The source-first status
record is
`verification/global-schur/2026-07-23T170612Z-status-literature-audit.md`;
its exact-search nonhits leave novelty and Conway-99 `UNKNOWN`. The detached
end-to-end release replay is
`verification/2026-07-23-wave20-clean-clone.md`.

Replay the Wave 21 six-/seven-vertex affine-count audit from the repository
root. The submitted checker is standard-library-only:

```powershell
.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave21-six-vertex-lp\test_exact_check.py

$wave21Stem = [guid]::NewGuid().ToString('N')
$wave21Root = Join-Path ([System.IO.Path]::GetTempPath()) "wave21-$wave21Stem"
New-Item -ItemType Directory -Path $wave21Root | Out-Null
$wave21Submitted = Join-Path $wave21Root "submitted.json"

.venv\Scripts\python.exe -B `
  attempts\wave21-six-vertex-lp\exact_check.py `
  --output $wave21Submitted
Get-FileHash -Algorithm SHA256 $wave21Submitted
```

The submitted suite passes 16/16 and the expected JSON SHA-256 is
`5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b`.

The independent verifier parses fresh copies of the exact primary-source TeX.
Download, inspect, and extract the two pinned arXiv archives:

```powershell
$wave21SixArchive = Join-Path $wave21Root "six-v2.tar"
$wave21SevenArchive = Join-Path $wave21Root "seven-v1.tar"
$wave21SixRoot = Join-Path $wave21Root "six"
$wave21SevenRoot = Join-Path $wave21Root "seven"
New-Item -ItemType Directory -Path $wave21SixRoot,$wave21SevenRoot | Out-Null

Invoke-WebRequest -UseBasicParsing `
  https://export.arxiv.org/e-print/2508.03377v2 `
  -OutFile $wave21SixArchive
Invoke-WebRequest -UseBasicParsing `
  https://export.arxiv.org/e-print/2511.06572v1 `
  -OutFile $wave21SevenArchive

Get-FileHash -Algorithm SHA256 $wave21SixArchive,$wave21SevenArchive

foreach ($wave21Archive in @($wave21SixArchive,$wave21SevenArchive)) {
  $wave21Members = @(& tar -tf $wave21Archive)
  if ($LASTEXITCODE -ne 0) { throw "Could not list $wave21Archive" }
  foreach ($wave21Member in $wave21Members) {
    $wave21Normalized = $wave21Member.Replace('\','/')
    if ([System.IO.Path]::IsPathRooted($wave21Member) -or
        $wave21Normalized -match '(^|/)\.\.(/|$)' -or
        $wave21Normalized -match '^[A-Za-z]:') {
      throw "Unsafe archive path: $wave21Member"
    }
  }
}

& tar -xf $wave21SixArchive -C $wave21SixRoot
if ($LASTEXITCODE -ne 0) { throw "Six-vertex extraction failed" }
& tar -xf $wave21SevenArchive -C $wave21SevenRoot
if ($LASTEXITCODE -ne 0) { throw "Seven-vertex extraction failed" }

$wave21SixTex = Join-Path $wave21SixRoot "The_Subgraphs_of_Order_Six.tex"
$wave21SevenTex = Join-Path $wave21SevenRoot `
  "Hamiltonian_Subgraphs_of_Order_Seven.tex"
Get-FileHash -Algorithm SHA256 $wave21SixTex,$wave21SevenTex
```

Expected archive hashes, in order, are
`f8429d2f839267e2aaf98b04451cb2f0252c0353f75bee6ec6e6947eab0d5834`
and
`10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a`.
Expected TeX hashes are
`823bcaf636a99f6655af453b2a910b9953338db980480572bca81730cfa1b44f`
and
`0b06fdc1c2951a344592c6af23abd133c4a8a68d717f199e7a0e2d7ceb909d0a`.

Preserve the raw source failure, then run only the explicit correction:

```powershell
$wave21Raw = Join-Path $wave21Root "raw.json"
$wave21Corrected = Join-Path $wave21Root "corrected.json"

.venv\Scripts\python.exe -B `
  verification\wave21-six-vertex-lp\independent_check.py `
  --six-tex $wave21SixTex --seven-tex $wave21SevenTex `
  --mode raw --output $wave21Raw
$wave21RawExit = $LASTEXITCODE
if ($wave21RawExit -ne 1) {
  throw "Expected raw printed equation to exit 1; got $wave21RawExit"
}

.venv\Scripts\python.exe -B `
  verification\wave21-six-vertex-lp\independent_check.py `
  --six-tex $wave21SixTex --seven-tex $wave21SevenTex `
  --mode corrected --output $wave21Corrected
if ($LASTEXITCODE -ne 0) { throw "Corrected replay failed" }

$env:WAVE21_SIX_TEX = $wave21SixTex
$env:WAVE21_SEVEN_TEX = $wave21SevenTex
.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave21-six-vertex-lp\test_independent_check.py
Get-FileHash -Algorithm SHA256 $wave21Raw,$wave21Corrected
```

The independent suite passes 19/19. The expected raw and corrected result
hashes are, respectively,

```text
50129e12b180c4f7ad7655cb4febe229588a855042a04b28817eeb52a3b27fb6
1c0cc560206ce388308573f2174a0a6189ae909f83a4acb86093063b5adfeacd
```

The raw process exit 1 is the expected `FAIL_AS_PRINTED`: the `m7(n-5)`
equation has residual exactly `n23`. The corrected process changes only the
named missing `+n23` deletion card. The verified exhaustion leaves
`n3=705,708,...,4158`, so it supplies neither a stronger bound nor a graph
construction. The public replay record is
`verification/wave21-six-vertex-lp/2026-07-23T175223Z-orchestrator-replay.md`.
The bounded current-version and correction search is recorded separately in
`verification/wave21-six-vertex-lp/status/2026-07-23T182843Z-source-status-audit.md`;
its companion manifest pins the official arXiv records, v1/v2 TeX and PDFs,
and later author sources.

Replay the two Wave 21 endpoint-refinement packages from the repository root:

```powershell
$wave21EndpointStem = [guid]::NewGuid().ToString('N')
$wave21EndpointRoot = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave21-endpoint-$wave21EndpointStem"
New-Item -ItemType Directory -Path $wave21EndpointRoot | Out-Null

.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave21-local-diagonal\test_exact_check.py
.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave21-local-diagonal\test_independent_check.py

$wave21LocalSubmitted = Join-Path $wave21EndpointRoot "local-submitted.json"
.venv\Scripts\python.exe -B `
  attempts\wave21-local-diagonal\exact_check.py `
  --output $wave21LocalSubmitted

# The independent local checker writes beside its own script, so copy only
# that checker into the temporary replay directory.
$wave21LocalIndependentRoot = Join-Path $wave21EndpointRoot "local-independent"
New-Item -ItemType Directory -Path $wave21LocalIndependentRoot | Out-Null
Copy-Item -LiteralPath `
  verification\wave21-local-diagonal\independent_check.py `
  -Destination $wave21LocalIndependentRoot
.venv\Scripts\python.exe -B `
  (Join-Path $wave21LocalIndependentRoot "independent_check.py")

.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave21-lattice-extension\test_exact_check.py
.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave21-lattice-extension\test_independent_check.py

$wave21LatticeSubmitted = Join-Path $wave21EndpointRoot `
  "lattice-submitted.json"
$wave21LatticeIndependent = Join-Path $wave21EndpointRoot `
  "lattice-independent.json"
.venv\Scripts\python.exe -B `
  attempts\wave21-lattice-extension\exact_check.py `
  --output $wave21LatticeSubmitted
.venv\Scripts\python.exe -B `
  verification\wave21-lattice-extension\independent_check.py `
  --output $wave21LatticeIndependent

Get-FileHash -Algorithm SHA256 `
  $wave21LocalSubmitted,`
  (Join-Path $wave21LocalIndependentRoot "independent-checks.json"),`
  $wave21LatticeSubmitted,`
  $wave21LatticeIndependent
```

The submitted/independent suites pass respectively 15/18 and 12/16 tests.
The four expected replay hashes, in command order, are

```text
2d51c827f822183c7c3cfea60e429ae550c2d95270c76f2a5f469371e71b4ce8
5150e0047e09cca5b09c15eb7d5a740ff6e0f1bf4291a7a4de0db61120da25af
18235cf32229bcdf1616a7560aa2389c830e7e23fa25f0a0fc02377c174dc53b
735ff677e7837f14ec2a52cbccd827d30abc5eee68ee5e4f8e2bd6a9e5bd21b1
```

The local package verifies `q(T)<=8` and
`tr(A4^2)>=26460` at `n3=705`; its scalar and spectral survivors are
relaxations only. The lattice package verifies the necessary endpoint
condition `h in {1,9}` while leaving `h` undetermined. Neither package
changes the unconditional project bound or target status.

Replay the Wave 22 complete order-seven aggregate deck witness:

```powershell
$wave22ReplayStem = [guid]::NewGuid().ToString('N')
$wave22ReplayRoot = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave22-seven-deck-$wave22ReplayStem"
New-Item -ItemType Directory -Path $wave22ReplayRoot | Out-Null

.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave22-full-seven-deck -p test_exact_check.py -v
.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave22-full-seven-deck `
  -p test_independent_verify.py -v

$wave22Submitted = Join-Path $wave22ReplayRoot "submitted.json"
$wave22Independent = Join-Path $wave22ReplayRoot "independent.json"
.venv\Scripts\python.exe -B `
  attempts\wave22-full-seven-deck\exact_check.py `
  --output $wave22Submitted
.venv\Scripts\python.exe -B `
  verification\wave22-full-seven-deck\independent_verify.py `
  --output $wave22Independent

Get-FileHash -Algorithm SHA256 $wave22Submitted,$wave22Independent
```

The submitted and independent suites pass 15/15 and 26/26. Expected result
hashes are:

```text
ca5d9d116f6a9d6e355600429652e2bf4474b73dcf281bbcb564420d820acbd2
54a02ffda9fe13293d6732fc6bf51f47e28a876a92ebdece10dea187ae0d020c
```

Both programs reconstruct the 62-by-208 deletion system and verify all 62
rows and all 19 pinned Hamiltonian counts at `n3=705,h11=2820`. The
nonnegative integer vector is only an aggregate count-system witness; it is
not a graph.

Replay the primary Wave 23 endpoint exclusion:

```powershell
$wave23ReplayStem = [guid]::NewGuid().ToString('N')
$wave23ReplayRoot = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave23-index-$wave23ReplayStem"
New-Item -ItemType Directory -Path $wave23ReplayRoot | Out-Null

.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave23-index-pranks -p test_exact_check.py -v
.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave23-index-pranks `
  -p test_independent_check.py -v

$wave23Submitted = Join-Path $wave23ReplayRoot "submitted.json"
$wave23Independent = Join-Path $wave23ReplayRoot "independent.json"
.venv\Scripts\python.exe -B `
  attempts\wave23-index-pranks\exact_check.py `
  --output $wave23Submitted
.venv\Scripts\python.exe -B `
  verification\wave23-index-pranks\independent_check.py `
  --output $wave23Independent

Get-FileHash -Algorithm SHA256 $wave23Submitted,$wave23Independent
```

The submitted and independent suites pass 15/15 and 14/14. Expected result
hashes are:

```text
64bf8192018376961ec88562d64928f73514697000c73cbf79a4a2a2def923b5
5ddcc8f5dec1b9923e4c28d60fb998858f33a99e659b451632641f6cea62701b
```

The independent verifier also checks all 20 entries in
`verification/wave23-index-pranks/artifact-manifest.sha256`. The verified
scope is the conditional exclusion `n3!=705`, hence `n3>=708` and
`induced_C6_count>=209994`; target existence remains `UNKNOWN`.

The separately developed shorter Wave 23 cross-check can be replayed with:

```powershell
$wave23CrossStem = [guid]::NewGuid().ToString('N')
$wave23CrossResult = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave23-cross-$wave23CrossStem.json"
$wave23CrossIndependent = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave23-cross-independent-$wave23CrossStem.json"

.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave23-endpoint-crosscheck -p test_exact_check.py -v
.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave23-endpoint-crosscheck `
  -p test_independent_check.py -v
.venv\Scripts\python.exe -B `
  attempts\wave23-endpoint-crosscheck\exact_check.py `
  --output $wave23CrossResult
.venv\Scripts\python.exe -B `
  verification\wave23-endpoint-crosscheck\independent_check.py `
  --output $wave23CrossIndependent
Get-FileHash -Algorithm SHA256 `
  $wave23CrossResult,$wave23CrossIndependent
```

The corrected candidate and independent suites pass 25/25 and 17/17. Expected
result hashes are:

```text
1b31074d0fe4872c14caf1e25842377e4ddab9860f241d87d2814a350ac100a4
69fc4ee307e45f2f4a4ccf1d41817636d38c92d5094080e938ecad66d7d24693
```

The cross-check reaches the same endpoint exclusion using the exact
Maclaurin bound `det(B)<43`. The first verifier audit preserves the original
candidate snapshot and records a nonblocking invalid hostile control; the
separate correction addendum verifies the corrected control and confirms that
the mathematical result is unchanged.

The current-head correction manifest has SHA-256

```text
43bcb9fe593e1c16fbeb0a130d7a064ed7d019d688624ea99302a586abbfc6cf
```

and all 13 entries in
`verification/wave23-endpoint-crosscheck/correction-artifact-manifest.sha256`
must match. The original `artifact-manifest.sha256` is intentionally frozen
to the pre-correction candidate bytes; do not use its candidate-file entries
as a current-head integrity check.

Replay the Wave 23 orbit-refined weighted-extension result:

```powershell
$wave23WeightedStem = [guid]::NewGuid().ToString('N')
$wave23WeightedSubmitted = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave23-weighted-submitted-$wave23WeightedStem.json"
$wave23WeightedIndependent = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave23-weighted-independent-$wave23WeightedStem.json"

python -B -m unittest discover `
  -s attempts\wave23-weighted-extensions `
  -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave23-weighted-extensions `
  -p test_independent_verifier.py -v
python -B attempts\wave23-weighted-extensions\exact_check.py `
  --output $wave23WeightedSubmitted
python -B verification\wave23-weighted-extensions\independent_verifier.py `
  --output $wave23WeightedIndependent
Get-FileHash -Algorithm SHA256 `
  $wave23WeightedSubmitted,$wave23WeightedIndependent
```

The discovery and independent suites pass 18/18 and 20/20. Expected result
hashes are:

```text
83a41b78eac02d845650ccdcb5b9782aba80caff9bdb7be983ec3f9e91c65b4c
fecd813402ddb3aabd2434833f020edaf11e82c4392fc6ecc7d1f300b7d97eb4
```

All nine entries in
`verification/wave23-weighted-extensions/artifact-manifest.sha256` must
match; the manifest itself has SHA-256
`0de03a8000cdb83aa6c1c7dfbd5162c37459f3da5e033c0f63ff98f08bdd4cd6`.
The verified statement is exact feasibility of the encoded 712-by-208
necessary count relaxation for every allowed historical-endpoint parameter,
not overlap consistency, a graph construction, or a bound change.

Replay the Wave 24 `n3=708` index-boundary result:

```powershell
$wave24Stem = [guid]::NewGuid().ToString('N')
$wave24Submitted = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave24-submitted-$wave24Stem.json"
$wave24Independent = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave24-independent-$wave24Stem.json"
$wave24Survivor = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave24-survivor-$wave24Stem.json"

python -B -m unittest discover `
  -s attempts\wave24-n3-708-index -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave24-n3-708-index `
  -p test_independent_check.py -v
python -B attempts\wave24-n3-708-index\exact_check.py `
  --output $wave24Submitted
python -B verification\wave24-n3-708-index\independent_check.py `
  --output $wave24Independent `
  --matrix-certificate $wave24Survivor
Get-FileHash -Algorithm SHA256 `
  $wave24Submitted,$wave24Independent,$wave24Survivor
```

The submitted and independent suites pass 15/15 and 17/17. Expected hashes
are:

```text
a4241cdeea64a8f6073037d564e72fb7ef545287d45aca4759cec6c31d26a463
726807402388c02909171a689f3a7fe2d8d1b74307c24e322ae013d0a9cd486a
a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2
```

All ten entries in
`verification/wave24-n3-708-index/artifact-manifest.sha256` must match; the
manifest itself has SHA-256
`36b3a3b39264e502346960acf00e2b1e054bda88b21ec1559c9076dd340edb84`.
The verified result restricts the endpoint to eight arithmetic index values
and verifies an abstract `h=9` lattice survivor. It does not exclude
`n3=708` or construct the projector or graph.

Replay the Wave 25 strict endpoint refinement:

```powershell
$wave25Stem = [guid]::NewGuid().ToString('N')
$wave25Submitted = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave25-submitted-$wave25Stem.json"
$wave25Independent = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave25-independent-$wave25Stem.json"

python -B -m unittest discover `
  -s attempts\wave25-n3-708-strictness -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave25-n3-708-strictness `
  -p test_independent_check.py -v
python -B attempts\wave25-n3-708-strictness\exact_check.py `
  --output $wave25Submitted
python -B verification\wave25-n3-708-strictness\independent_check.py `
  --output $wave25Independent
Get-FileHash -Algorithm SHA256 $wave25Submitted,$wave25Independent
```

The submitted and independent suites pass 21/21 and 18/18. Expected hashes
are:

```text
6da9200adf19a5305913178c271ac584e9825aa4f3594fad20717f9418d2b40e
8c147d7b9da422c9d9b3d646015d95d737efc57d81964fabb3b33574a1d69f77
```

All six entries in
`verification/wave25-n3-708-strictness/artifact-manifest.sha256` must match;
the manifest itself has SHA-256
`473601e70d6c873e1b691d8fcf7c769d907ae2a9eadff198d72e0936e9fcc1ce`.
All four entries in
`verification/wave25-literature-audit/publication-hashes.sha256` must match;
that manifest has SHA-256
`df3621eefa727aac0a75e8562b31dcfda0c4eec313dcdb0bd5e2f3704941d395`.

The verifier reproduces `tr(C^2)>=10`, `tr(B^2)>=116`, and the combined
necessary cap `det(B)<=6525`, while preserving the exact abstract
`h=9`, `det(B)=81` survivor. The result does not exclude `n3=708`, construct
a projector or graph, improve the headline `n3>=708` bound, or resolve
Conway-99.

The detached incremental replay is recorded in
`verification/2026-07-23-wave25-clean-clone.md`. At integration commit
`156756d4ef98dc7233e29a7f8c9feeb143548197`, it passes all 39 Wave 25 tests,
regenerates both exact JSON files byte-identically, checks both manifests and
all 129 status path/hash pairs, scans the release tree and all four commits
after the prior public checkpoint for credential-shaped or private-path
payloads, and finishes with a clean tracked tree and
`git fsck --full --strict`.

Replay the two Wave 26 `A2` obstructions and their independent verifiers:

```powershell
$wave26Stem = [guid]::NewGuid().ToString('N')
$wave26FrameSubmitted = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave26-frame-submitted-$wave26Stem.json"
$wave26FrameIndependent = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave26-frame-independent-$wave26Stem.json"
$wave26CubicSubmitted = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave26-cubic-submitted-$wave26Stem.json"
$wave26CubicIndependent = Join-Path ([System.IO.Path]::GetTempPath()) `
  "wave26-cubic-independent-$wave26Stem.json"

python -B -m unittest discover `
  -s attempts\wave26-a2-frame-obstruction -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave26-a2-frame-obstruction `
  -p test_independent_check.py -v
python -B -m unittest discover `
  -s attempts\wave26-a2-cubic-obstruction -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave26-a2-cubic-obstruction `
  -p test_independent_check.py -v

python -B attempts\wave26-a2-frame-obstruction\exact_check.py `
  --output $wave26FrameSubmitted
python -B verification\wave26-a2-frame-obstruction\independent_check.py `
  --output $wave26FrameIndependent
python -B attempts\wave26-a2-cubic-obstruction\exact_check.py `
  --output $wave26CubicSubmitted
python -B verification\wave26-a2-cubic-obstruction\independent_check.py `
  --output $wave26CubicIndependent

Get-FileHash -Algorithm SHA256 `
  $wave26FrameSubmitted,$wave26FrameIndependent,`
  $wave26CubicSubmitted,$wave26CubicIndependent
```

The four suites pass 15/15, 14/14, 19/19, and 17/17. Expected generated
hashes, in the same order, are:

```text
bb2b2ffe33d0ca6a0a1f18be8b36c48060d40aef2fc6e0857fd1d23c18e84bb9
b664844d65ab553cfd2277e925f5596193c586378d880dc1a29242cb9ac8f03b
acc3ce7298c164bdee1fe32766bf18437fe79770ee69090b759d3dc774640f33
658b7eb7eec64a4560d20e9c7b272c428168876c43910d9af6e44035dde12352
```

All eight entries in
`verification/wave26-a2-frame-obstruction/artifact-manifest.sha256` must
match; the manifest SHA-256 is
`dc12aeacd906d5b7f54fca3de796ca95d829385ac3a901dbf9760ee4aed3550c`.
All nine entries in
`verification/wave26-a2-cubic-obstruction/artifact-manifest.sha256` must
match; the manifest SHA-256 is
`75572e7f356312e2f4aee94ecaa5032f7d2bfdfd530f989a9e36fd39da63f842`.
All nine entries in
`verification/wave26-literature-audit/manifest.sha256` must match; the
manifest SHA-256 is
`0d9381d47a33fa376c53510cae2a57dfd419a41bb96658b56ce7cb624d953816`.

The frame route proves the exact `21>18` root-fibre contradiction. The cubic
route independently proves `tr(A2 Q_AA)>=18`, while each explicit survivor
block has trace ten. Together they exclude the required projector-frame and
full Schur-square origins of the one `E8^5 orthogonal-sum A2^2` hostile
control. They do not classify all `h=9` forms, exclude `n3=708`, improve the
headline `n3>=708` bound, or resolve Conway-99.

The detached incremental replay is recorded in
`verification/2026-07-23-wave26-clean-clone.md`. At integration commit
`4f1f3be35e712789dcba10fda5ec8d2bc569bc17`, it passes all 65 Wave 26 tests,
regenerates four exact JSON files byte-identically, checks all three
manifests, 60 claims, 54 obligations, 151 status hashes, 172 local links, 47
BibTeX keys, and 50 LF-only Wave 26/central files. Exact-blob scans of the
integration tree and all three commits after public baseline `930cb99` find
zero credential-shaped or private-path payloads. The detached clone finishes
with a clean tracked tree and `git fsck --full --strict`.

Replay the seven Wave 27 discovery and independent-verification suites:

```powershell
$wave27Stem = [guid]::NewGuid().ToString('N')
$wave27Temp = [System.IO.Path]::GetTempPath()
$wave27A2FreeSubmitted = Join-Path $wave27Temp `
  "wave27-a2free-submitted-$wave27Stem.json"
$wave27A2FreeIndependent = Join-Path $wave27Temp `
  "wave27-a2free-independent-$wave27Stem.json"
$wave27E6TraceSubmitted = Join-Path $wave27Temp `
  "wave27-e6-trace-submitted-$wave27Stem.json"
$wave27E6TraceIndependent = Join-Path $wave27Temp `
  "wave27-e6-trace-independent-$wave27Stem.json"
$wave27TensorSubmitted = Join-Path $wave27Temp `
  "wave27-tensor-submitted-$wave27Stem.json"
$wave27A20Submitted = Join-Path $wave27Temp `
  "wave27-a20-submitted-$wave27Stem.json"
$wave27TensorIndependent = Join-Path $wave27Temp `
  "wave27-tensor-independent-$wave27Stem.json"
$wave27Generated = @(
  $wave27A2FreeSubmitted,
  $wave27A2FreeIndependent,
  $wave27E6TraceSubmitted,
  $wave27E6TraceIndependent,
  $wave27TensorSubmitted,
  $wave27A20Submitted,
  $wave27TensorIndependent
)

function Assert-Wave27ByteEqual {
  param(
    [Parameter(Mandatory = $true)][string]$Expected,
    [Parameter(Mandatory = $true)][string]$Actual
  )
  $expectedBytes = [Convert]::ToBase64String(
    [System.IO.File]::ReadAllBytes((Resolve-Path $Expected))
  )
  $actualBytes = [Convert]::ToBase64String(
    [System.IO.File]::ReadAllBytes($Actual)
  )
  if ($expectedBytes -cne $actualBytes) {
    throw "Byte mismatch: $Expected versus $Actual"
  }
}

try {
  python -B -m unittest discover `
    -s attempts\wave27-a2free-construction -p test_exact_check.py -v
  python -B -m unittest discover `
    -s verification\wave27-a2free-construction `
    -p test_independent_check.py -v
  python -B -m unittest discover `
    -s attempts\wave27-h9-classification -p test_exact_check.py -v
  python -B -m unittest discover `
    -s verification\wave27-h9-classification `
    -p test_independent_check.py -v
  python -B -m unittest discover `
    -s attempts\wave27-general-root-tensor -p test_exact_check.py -v
  python -B -m unittest discover `
    -s attempts\wave27-a20-trace-addendum -p test_exact_check.py -v
  python -B -m unittest discover `
    -s verification\wave27-general-root-tensor `
    -p test_independent_check.py -v

  python -B attempts\wave27-a2free-construction\exact_check.py `
    --output $wave27A2FreeSubmitted
  python -B verification\wave27-a2free-construction\independent_check.py `
    --output $wave27A2FreeIndependent
  python -B attempts\wave27-h9-classification\exact_check.py `
    --output $wave27E6TraceSubmitted
  python -B verification\wave27-h9-classification\independent_check.py `
    --output $wave27E6TraceIndependent
  python -B attempts\wave27-general-root-tensor\exact_check.py `
    --output $wave27TensorSubmitted
  python -B attempts\wave27-a20-trace-addendum\exact_check.py `
    --output $wave27A20Submitted
  python -B verification\wave27-general-root-tensor\independent_check.py `
    --output $wave27TensorIndependent

  Assert-Wave27ByteEqual `
    attempts\wave27-a2free-construction\exact-results.json `
    $wave27A2FreeSubmitted
  Assert-Wave27ByteEqual `
    verification\wave27-a2free-construction\independent-results.json `
    $wave27A2FreeIndependent
  Assert-Wave27ByteEqual `
    attempts\wave27-h9-classification\exact-results.json `
    $wave27E6TraceSubmitted
  Assert-Wave27ByteEqual `
    verification\wave27-h9-classification\independent-results.json `
    $wave27E6TraceIndependent
  Assert-Wave27ByteEqual `
    attempts\wave27-general-root-tensor\exact-results.json `
    $wave27TensorSubmitted
  Assert-Wave27ByteEqual `
    attempts\wave27-a20-trace-addendum\exact-results.json `
    $wave27A20Submitted
  Assert-Wave27ByteEqual `
    verification\wave27-general-root-tensor\independent-results.json `
    $wave27TensorIndependent

  Get-FileHash -Algorithm SHA256 $wave27Generated
}
finally {
  Remove-Item -LiteralPath $wave27Generated -Force -ErrorAction SilentlyContinue
}
```

The suites pass, in command order, 15/15, 16/16, 16/16, 21/21, 17/17,
8/8, and 23/23: 116 tests total. The generated files are byte-identical to
their seven stored JSON counterparts. Their expected SHA-256 values, in the
same order, are:

```text
3b1d30b6110d937f1bd4bb9ff570419625063afc5c0915382baa2466d349946d
ee0b100806de66252a9795622881adb5651e5b46f8ae0b5757fc15874257e31f
377b4edc9498ad71cb655f084970aed234ea809c8413643cb5e9cfd03b75fde2
4b0532842e506cb5de4e8d131c48da6d078be7d69b459af50b3207a8900d788a
98aba5a30b2f3a83b9f6ce6fd6a20458505b668249d97b0810907de50cae678d
dc5716cbf2537cd214906f1bf2eae96d4886e4bd88008cd7508c6a64d78f089c
7e87796980a43df199713865fed920bc094778f1828431a673938484c026e6fd
```

The six Wave 27 manifests below must validate from their containing
directories:

| package | entries | manifest SHA-256 |
|---|---:|---|
| `attempts/wave27-general-root-tensor` | 7 | `3ba7ee4683dfac361b6f2d1b09a90d485210e2debd87cbe9d4ecb62f607ebf32` |
| `attempts/wave27-a20-trace-addendum` | 7 | `8f8ef9538a4070d569cfd4415296206214af3d3b2d8fe136ec7536257ead9949` |
| `verification/wave27-a2free-construction` | 8 | `a4ab58cf5f2e1f7cd635b4ec7d7dca801d878b4ce596e85d161c2a2b7c2c1023` |
| `verification/wave27-h9-classification` | 8 | `7b9584b72e59bfeff8430cfe13b2eac8b08e02481eac7c89219cfb454332686f` |
| `verification/wave27-general-root-tensor` | 11 | `e72b134623d95ea054b348b641ca23a57ee7d29b5edd8033527cca1f8c68914c` |
| `verification/wave27-literature-audit` | 10 | `f439b850eeecbb519208200aa908434a3d7908faff9021694c6fcd3f2aeadfe1` |

The replays verify an abstract `E8^4 orthogonal-sum E6^2` arithmetic
survivor, the unrestricted local `E6` trace minimum 14, the stronger
frame/Schur cubic exclusions for orthogonal `E6` and `A6` summands, and the
separate `A20` trace addendum. Combined with the Wave 26 `A2` result, they
exclude a full orthogonal ADE endpoint form under the stated projector/Schur
premises. They do not classify general even rank-44 forms, exclude `n3=708`,
improve the headline `n3>=708` bound, resolve Conway-99, or establish novelty.

The detached Wave 27 publication replay is
`verification/2026-07-24-wave27-clean-clone.md`. At integration commit
`4a2f65d20f8fa403a3a245815799070cf126173f`, it passes all 116 tests,
regenerates seven JSON files byte-identically, validates all 51 entries in
six manifests, checks 65 claims, 59 obligations, 211 status path/hash pairs,
205 scoped local links, 52 unique BibTeX keys, and 81 LF-only Wave 27/central
files. Exact-blob scans cover 761 release-tree files and all 77 new blobs
across the seven-commit unpublished range with zero credential-shaped or
private-path findings. The detached clone finishes clean, and
`git fsck --full --strict` returns success.

## Wave 28 unrestricted-lattice controls

Replay the five Wave 28 discovery and independent-verification suites:

```powershell
python -B -m unittest discover `
  -s attempts\wave28-glue-discriminant -p test_exact_check.py -v
python -B -m unittest discover `
  -s attempts\wave28-theta-modular -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave28-glue-discriminant `
  -p test_independent_check.py -v
python -B -m unittest discover `
  -s verification\wave28-theta-modular `
  -p test_independent_check.py -v
python -B -m unittest discover `
  -s verification\wave28-simultaneous-neighbor `
  -p test_independent_check.py -v
```

The suites pass `13`, `14`, `16`, `20`, and `25` tests respectively: 88
tests total. The theta unit tests validate the stored complete shell
certificate without repeating the 15-million-node enumeration.

Regenerate all five mathematical JSON files outside the checkout:

```powershell
$wave28Generated = Join-Path `
  ([IO.Path]::GetTempPath()) `
  ("conway-wave28-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $wave28Generated | Out-Null

function Assert-Wave28ByteEqual {
  param([string]$Expected, [string]$Actual)
  $left = [IO.File]::ReadAllBytes((Resolve-Path $Expected))
  $right = [IO.File]::ReadAllBytes((Resolve-Path $Actual))
  if (-not [System.Linq.Enumerable]::SequenceEqual($left, $right)) {
    throw "byte mismatch: $Expected versus $Actual"
  }
}

try {
  $glueSubmitted = Join-Path $wave28Generated "glue-submitted.json"
  $thetaSubmitted = Join-Path $wave28Generated "theta-submitted.json"
  $glueIndependent = Join-Path $wave28Generated "glue-independent.json"
  $thetaIndependent = Join-Path $wave28Generated "theta-independent.json"
  $neighborIndependent = Join-Path $wave28Generated "neighbor-independent.json"

  python -B attempts\wave28-glue-discriminant\exact_check.py `
    --output $glueSubmitted
  python -B attempts\wave28-theta-modular\exact_check.py `
    --output $thetaSubmitted
  python -B verification\wave28-glue-discriminant\independent_check.py `
    --output $glueIndependent
  python -B verification\wave28-theta-modular\independent_check.py `
    --output $thetaIndependent
  python -B verification\wave28-simultaneous-neighbor\independent_check.py `
    --output $neighborIndependent

  Assert-Wave28ByteEqual `
    attempts\wave28-glue-discriminant\exact-results.json `
    $glueSubmitted
  Assert-Wave28ByteEqual `
    attempts\wave28-theta-modular\exact-results.json `
    $thetaSubmitted
  Assert-Wave28ByteEqual `
    verification\wave28-glue-discriminant\independent-results.json `
    $glueIndependent
  Assert-Wave28ByteEqual `
    verification\wave28-theta-modular\independent-results.json `
    $thetaIndependent
  Assert-Wave28ByteEqual `
    verification\wave28-simultaneous-neighbor\independent-results.json `
    $neighborIndependent
}
finally {
  Remove-Item -LiteralPath $wave28Generated -Recurse -Force `
    -ErrorAction SilentlyContinue
}
```

The expected SHA-256 values, in the same order, are:

```text
13a3bb8f83c56ff899991362736089b772114cff840a2cb20d68845e231b3cf1
9d7b1ffcc0cef2441aa6dd381228abaa1018f721594e930cdd7227c0647470d6
0d15724c772300072c565030e88080c05333af8f75241b633d5801e5c4ac83fe
24298ae282c7baa252a39ffe96fc37b7c696cb51f14b9ddea2318a59b4335b7f
d9f6829dc967fb3777f541b4fd16cd27acb3478d96479b8ad9c3e9fbad2afedd
```

The six Wave 28 manifests validate 46 entries:

| package | entries | manifest SHA-256 |
|---|---:|---|
| `attempts/wave28-glue-discriminant` | 7 | `5ac509e960c3b2e5e8b949aa88958f9bce6ae7b5b34a7baad140d20d3487bcbb` |
| `attempts/wave28-theta-modular` | 8 | `1a7a68019241b5f83b4f9154a1361d1ebcf8da72d287175a13e8400b83b07692` |
| `verification/wave28-glue-discriminant` | 4 | `d25e446673fcb80cb21afc87cd1f271c4c5e4d6d36f6ec6a564e7d6fbb2296a7` |
| `verification/wave28-theta-modular` | 10 | `50a5e3d4b5bb066b4b281c80d6d2caa0906afc21b9de99e12731177f661c6fed` |
| `verification/wave28-simultaneous-neighbor` | 7 | `068d9270a83b0d99a39bbc8cda8a18773c62d5899fcba202c42755f79145e985` |
| `verification/wave28-literature-audit` | 10 | `b032fa9f287bed73ae3e7526d60e48b51af43d30717187813ae8473637048df4` |

The exact theta replay is offline by default and uses the attributed,
hash-bound numeric matrices in `catalogue-data.json`. The optional live
source refresh rewrites `source-manifest.json` with the new access timestamp,
so run it only in a disposable clone. To refetch the two catalogue pages,
verify their frozen response hashes, parse the matrix data, and discard the
HTML, run there:

```powershell
$wave28RefreshOutput = Join-Path `
  ([IO.Path]::GetTempPath()) `
  ("conway-wave28-refresh-" + [guid]::NewGuid().ToString("N") + ".json")
python -B verification\wave28-theta-modular\independent_check.py `
  --refresh-sources `
  --output $wave28RefreshOutput
Remove-Item -LiteralPath $wave28RefreshOutput -Force
```

This optional command requires network access and deliberately fails closed
on source drift. Its refreshed `source-manifest.json` should be treated as
new evidence and reviewed before retention. The public package contains no
copied HTML or paper.

The verified Wave 28 scope is limited to corrected necessary
discriminant/glue and theta restrictions, a rootless bare `S/G` control, and
two abstract simultaneous-neighbor controls. It does not classify general
rank-44 forms, construct `X,M,W,Q,B`, exclude `n3=708`, improve the
`n3>=708` bound, resolve Conway-99, or establish novelty.

The detached
[Wave 28 clean-clone report](verification/2026-07-24-wave28-clean-clone.md)
records the complete offline replay at integration commit
`4c4d2cb8dec14c7834984d47a7e5b29991891e60`: 88 tests, five
byte-identical regenerations, six manifests with 46 entries, central
metadata and all-repository link checks, exact-blob privacy scans, clean
status, and strict Git object verification.

## Wave 29 single-lattice endpoint exclusion

Replay the discovery and independent-verification suites:

```powershell
python -B -m unittest discover `
  -s attempts\wave29-s0-frame-exclusion -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave29-s0-frame-exclusion `
  -p test_independent_check.py -v
```

The suites pass 18 and 27 tests, respectively: 45 tests total.

Regenerate both exact result files outside the checkout:

```powershell
$wave29Generated = Join-Path `
  ([IO.Path]::GetTempPath()) `
  ("conway-wave29-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $wave29Generated | Out-Null

try {
  $submitted = Join-Path $wave29Generated "submitted.json"
  $independent = Join-Path $wave29Generated "independent.json"

  python -B attempts\wave29-s0-frame-exclusion\exact_check.py `
    --output $submitted
  python -B verification\wave29-s0-frame-exclusion\independent_check.py `
    --output $independent

  $submittedExpected = (
    Get-FileHash -Algorithm SHA256 `
      attempts\wave29-s0-frame-exclusion\exact-results.json
  ).Hash
  $submittedActual = (
    Get-FileHash -Algorithm SHA256 $submitted
  ).Hash
  if ($submittedExpected -ne $submittedActual) {
    throw "Wave 29 submitted result differs"
  }

  $independentExpected = (
    Get-FileHash -Algorithm SHA256 `
      verification\wave29-s0-frame-exclusion\independent-results.json
  ).Hash
  $independentActual = (
    Get-FileHash -Algorithm SHA256 $independent
  ).Hash
  if ($independentExpected -ne $independentActual) {
    throw "Wave 29 independent result differs"
  }
}
finally {
  Remove-Item -LiteralPath $wave29Generated -Recurse -Force `
    -ErrorAction SilentlyContinue
}
```

The expected output hashes are:

```text
7a85c5321b5e91365c246dff7bae9264cc82494da5c866b1b351511099f6638c
c0418cec88915089d6cc2e29735ca3e7bc425cfcd2b3ce09a78a707e36e0aa04
```

The three Wave 29 manifests validate 19 entries:

| package | entries | manifest SHA-256 |
|---|---:|---|
| `attempts/wave29-s0-frame-exclusion` | 7 | `8cb5b0198ac9e787a8234820e648626dc27f900f53b7511068d5442d06d7a39b` |
| `verification/wave29-s0-frame-exclusion` | 7 | `6a62209abbca6403dee7b9ebf83edbdccd5466a278957ab9d63f37bcd3f08cf8` |
| `verification/wave29-s0-literature-audit` | 5 | `76898c9ecdcaba86bf14469700110f4ad45ea70ba576c7ebea73d725d0de9177` |

The literature ledger accounts for 81 query strings in 21 batches and 16
retained metadata-only sources. No raw paper, HTML, or API response is part
of the package.

The verified mathematical scope is exactly:

```text
S0=K12 orthogonal_sum LAMBDA(F) as a full endpoint S-form: excluded
all other determinant-729 lattices: UNKNOWN
n3=708 / Conway-99 / novelty: UNKNOWN
```

The detached
[Wave 29 clean-clone report](verification/2026-07-24-wave29-clean-clone.md)
records the complete offline replay at integration commit
`ae8fd70baaeb35302f957653e20ad710e5e77281`: 45 tests, two
byte-identical regenerations, three manifests with 19 entries, 263 status
path/hash pairs, 275 tracked Markdown files with 263 resolving local links,
exact-blob privacy over the 841-file release tree and all 32 new blobs, clean
status, and strict Git object verification.

## Wave 30 decomposable `h=729` reduction and bare construction

### Repaired general discovery

Run the repaired discovery suite in the current tree:

```powershell
python -B -m unittest discover `
  -s attempts\wave30-general-h729 -p test_exact_check.py -v
```

It passes 20 tests. Regenerate its result outside the checkout and compare it
byte for byte:

```powershell
$wave30General = Join-Path `
  ([IO.Path]::GetTempPath()) `
  ("conway-wave30-general-" + [guid]::NewGuid().ToString("N") + ".json")

python -B attempts\wave30-general-h729\exact_check.py `
  --output $wave30General

$expected = [IO.File]::ReadAllBytes(
  (Resolve-Path attempts\wave30-general-h729\exact-results.json)
)
$actual = [IO.File]::ReadAllBytes($wave30General)
if (-not [Linq.Enumerable]::SequenceEqual($expected, $actual)) {
  throw "Wave 30 repaired general result differs"
}
```

The expected SHA-256 is:

```text
cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c
```

### Historical veto and independent replay

Do not run the old general verifier against repaired discovery bytes and call
the resulting freeze error a verifier failure. Its hard freeze is an
intentional historical invariant. Extract verifier-veto commit
`0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321` into a temporary directory:

```powershell
$wave30Historical = Join-Path `
  ([IO.Path]::GetTempPath()) `
  ("conway-wave30-history-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $wave30Historical | Out-Null
$archive = Join-Path $wave30Historical "repo.tar"
$tree = Join-Path $wave30Historical "tree"
New-Item -ItemType Directory -Path $tree | Out-Null

git archive --format=tar --output=$archive `
  0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321
tar -xf $archive -C $tree

Push-Location (Join-Path $tree "verification\wave30-general-h729")
try {
  python -B -m unittest -v `
    test_independent_check.py test_hostile_controls.py
  python -B independent_check.py `
    --output (Join-Path $wave30Historical "independent.json")
}
finally {
  Pop-Location
}
```

The historical verifier passes 32 tests. Its regenerated JSON must match:

```text
2b948591611e9c984985f7bacc5a77c714332fbe42ed5305b84039c621358416
```

For failure-history auditing, perform the same extraction at original
discovery commit `091d0a458ab1f96e3b3f491b677c84824bbf8f44` and run its submitted
suite and generator. The expected result is deliberately:

```text
tests run: 0
suite: FAIL
generator: FAIL before output
objection: V30-GEN-001
```

That expected failure is not a passing mathematical test. The repaired
[re-verification audit](verification/wave30-general-h729/reverification-audit.md)
records the three snapshots separately.

### Bare `T20` and rank-44 construction

Run both current-tree construction suites:

```powershell
python -B -m unittest discover `
  -s attempts\wave30-h729-construction -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave30-h729-construction `
  -p test_independent_check.py -v
```

They pass 16 and 24 tests. Regenerate both JSON files outside the checkout:

```powershell
$wave30Construction = Join-Path `
  ([IO.Path]::GetTempPath()) `
  ("conway-wave30-construction-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $wave30Construction | Out-Null

python -B attempts\wave30-h729-construction\exact_check.py `
  --output (Join-Path $wave30Construction "submitted.json")
python -B verification\wave30-h729-construction\independent_check.py `
  --output (Join-Path $wave30Construction "independent.json")
```

The expected hashes are:

```text
submitted:
0d3723ba4c185dc7865858d16bfc6ada99fd87b4e21da616ef1b1d1ad6b67e11

independent:
d7e6f18f82045c3e589dfc003c474fa506b59e57b0a02ef277451f2f28ff03b5
```

### Manifests and literature

Six Wave 30 manifests validate 47 entries in total:

| package | entries | manifest SHA-256 |
|---|---:|---|
| repaired general discovery | 8 | `e562654891c61a1ae50d34a6a38c6d9a39e985a03d7b0a253f60871539f1f006` |
| historical general verifier | 8 | `f9f7ec7cc764fc7b1ec03f1d90dc582d64ce05af200cb98188698878458ab3e0` |
| general re-verification | 12 | `8f6cba4e72ac38c73852ed3c7b549df8c123fa87e59fffbd1a6569eb235bbefe` |
| construction discovery | 7 | `d70d00c8a278bcd8710cf7c8d53c679e05509db2b08bc7ad2f11af4bbe6e564a` |
| construction verifier | 7 | `d70590f6a9d582cd6f14a62039a8b80a7fb23716b9808e1d1e023da558d7bcdd` |
| literature audit | 5 | `ddb945fa06db29bdfd6f14f63cadeade2991fcc5803031c01d1e940d0a2fee60` |

The literature ledger accounts for 96 query strings in 24 batches and 21
retained metadata-only sources. It retains no raw paper, HTML, XML feed, or
API response. One Crossref query returned HTTP 429.

The passing mathematical total is 92 tests across the repaired current tree
and the separately extracted historical independent verifier:

```text
repaired general discovery:           20
historical independent general:       32
construction discovery:               16
construction independent verifier:    24
total:                                 92
```

The exact scope wall is:

```text
rootless integrally decomposable h=729 reduction: VERIFIED
bare T20 and T20 orthogonal_sum LAMBDA24 S/G:      VERIFIED
surviving 20+24 type / rooted / indecomposable:   UNKNOWN
h=729 row / n3=708 / Conway-99 / novelty:         UNKNOWN
```

The detached
[Wave 30 clean-clone replay](verification/2026-07-24-wave30-clean-clone.md)
freezes integration commit
`0a31b62b337153b6d45dbdf1288810cd726c17a3`. In a new clone with local-clone
optimization and hardlinks disabled, it repeats the 60 current-tree tests,
the 32-test historical verifier replay, the original expected failure, four
byte-identical regenerations, all six manifests and 47 entries, central
ledger and link checks, exact-blob privacy scans, clean-status checks, and
`git fsck --full --strict`. The replay certifies publication hygiene for the
two scoped Wave 30 results; it does not promote any broader endpoint status.

## Wave 31 sign-commutant theorem and T20 finite boundary

Run the four Wave 31 unit-test suites from the repository root:

```powershell
python -B -m unittest discover `
  -s attempts\wave31-survivor-proof -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave31-sign-commutant `
  -p test_independent_check.py -v
python -B -m unittest discover `
  -s attempts\wave31-t20-frame -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave31-t20-frame `
  -p test_independent_check.py -v
```

They pass `15`, `21`, `10`, and `11` tests, respectively: 57 unique unit
tests. Do not pass a filesystem path as a `unittest` module name from the
sign-verifier directory; two discarded wrong-directory invocations
discovered zero substantive tests and are retained as harness failures.

Run the separate skeptical checker directly:

```powershell
$wave31Tmp = Join-Path `
  ([IO.Path]::GetTempPath()) `
  ("conway-wave31-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $wave31Tmp | Out-Null

python -B verification\wave31-sign-commutant-skeptic\skeptic_check.py `
  --output (Join-Path $wave31Tmp "skeptic.json")
```

It returns `PASS_NO_FATAL_GAP`. It is a second adversarial audit, not an
additional unit-test count and not the designated promotion verifier.

Regenerate the proof and primary verifier outputs:

```powershell
python -B attempts\wave31-survivor-proof\exact_check.py `
  --output (Join-Path $wave31Tmp "proof.json")
python -B verification\wave31-sign-commutant\independent_check.py `
  --output (Join-Path $wave31Tmp "sign-independent.json")
```

The expected SHA-256 values are:

```text
proof:
e5155e67a59168767639273ee70fc6d63e81b104e9b415e228ca09a0f9317587

primary independent:
7143c403172403b21ea2cdc2851851a3a13cb08b0dd14e5d68432aafd25fc5c0

skeptical independent:
0dd057b903da3092528f4e0bc2b9283e8ee6fa3222553b24b219dda732d35007
```

The proof JSON must also be byte-identical to
`verification/wave31-sign-commutant/submitted-regenerated.json`.

Regenerate both T20 finite-search outputs:

```powershell
python -B attempts\wave31-t20-frame\exact_check.py `
  --output (Join-Path $wave31Tmp "t20-submitted.json")
python -B verification\wave31-t20-frame\independent_check.py `
  --output (Join-Path $wave31Tmp "t20-independent.json")
```

The expected hashes are:

```text
T20 submitted:
d2592a71e8600a894aa7d87e6ed1c8230010b919488b10f9854710bb77944152

T20 independent:
ac6c34e1f8c1ba98d12d5d01e9d8b05e7a60a51a76b5701c528912f94ab3bede
```

The proof, primary-sign, T20-submitted, and T20-independent JSON files
include runtime metadata. Literal byte identity is asserted for the
pinned/current environment; on another OS or Python build, compare the exact
mathematical fields separately from runtime fields. The skeptical result has
no runtime block.

Six Wave 31 manifests validate 42 entries:

| package | entries | manifest SHA-256 |
|---|---:|---|
| sign proof discovery | 7 | `c1d3b8d2a2ca25c4dcdb20fbc1d974f1561fa7c110524359443161d79bebd7f6` |
| literature audit | 6 | `ccbc52b0089484b153251fe4c37759d49618c59a78e449c61dde122e64465d25` |
| T20 finite discovery | 8 | `972640b51dd31dc6037ae26b676d1f7c39626f25d038606a71bf18728e9ea3d4` |
| primary sign verifier | 8 | `e91d4ec72d7921688700bdc5e68b1e610db1d031b1ec7ffae9b927ecd4494122` |
| skeptical sign verifier | 5 | `c9dd19b9df24e22bcfff7533bb0251582c737153dbbe9ad28e8ea23f2085c1c0` |
| T20 finite verifier | 8 | `73072c577eff876b4799455a6e0ea0080e54f5370ed8790eda6b85fe3687e1bb` |

The exact Wave 31 scope wall is:

```text
rootless integrally decomposable actual-incidence endpoint: VERIFIED impossible
displayed T20 shell and named finite restrictions:           VERIFIED
unrestricted T20 Boolean/oriented frame:                     UNKNOWN
rooted / rootless integrally indecomposable endpoints:       UNKNOWN
n3=708 / Conway-99 / novelty:                                UNKNOWN
strongest conditional bound:                                n3>=708
```

The [primary audit](verification/wave31-sign-commutant/audit.md),
[skeptical audit](verification/wave31-sign-commutant-skeptic/audit.md),
[T20 audit](verification/wave31-t20-frame/audit.md), and
[correction ledger](verification/2026-07-24-wave31-orchestrator-corrections.md)
record the proof obligations, failed harness invocations, exact restrictions,
and nonpromotion wall.

The detached
[Wave 31 clean-clone replay](verification/2026-07-24-wave31-clean-clone.md)
freezes integration commit
`f591e756ca8cca179ee35b511bb61d720dcbc42d`. In a no-local,
no-hardlink clone checked out in detached state, it repeats all 57 unit tests
and the skeptical checker, runs the five generators outside the checkout,
validates all six manifests and 42 entries, checks duplicate-key-free YAML,
77 claims, 71 obligations, 1,331 evidence references, 87 BibTeX keys, 312
local links, exact Git-blob privacy, clean status, and
`git fsck --full --strict`.

## Wave 32 rooted and indecomposable endpoint reductions

Run the five Wave 32 suites from the repository root:

```powershell
python -B -m unittest discover `
  -s attempts\wave32-rooted-vector -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave32-rooted-vector -p test_independent_check.py -v
python -B -m unittest discover `
  -s attempts\wave32-indecomposable -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave32-indecomposable -p test_independent_check.py -v
python -B -m unittest discover `
  -s verification\wave32-literature-audit-independent `
  -p test_independent_check.py -v
```

They pass `14`, `19`, `10`, `19`, and `17` tests, respectively: 79 tests
in total. The rooted and indecomposable verifiers are clean-room
implementations and do not import or execute the corresponding discovery
checker. The literature verifier freezes the corrected candidate and
supporting inputs byte for byte.

Regenerate the five deterministic outputs outside the checkout:

```powershell
$wave32Tmp = Join-Path `
  ([IO.Path]::GetTempPath()) `
  ("conway-wave32-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $wave32Tmp | Out-Null

python -B attempts\wave32-rooted-vector\exact_check.py `
  --output (Join-Path $wave32Tmp "rooted-discovery.json")
python -B verification\wave32-rooted-vector\independent_check.py `
  --output (Join-Path $wave32Tmp "rooted-independent.json")
python -B attempts\wave32-indecomposable\exact_check.py `
  --output (Join-Path $wave32Tmp "indecomposable-discovery.json")
python -B verification\wave32-indecomposable\independent_check.py `
  --output (Join-Path $wave32Tmp "indecomposable-independent.json")
python -B verification\wave32-literature-audit-independent\independent_check.py `
  --output (Join-Path $wave32Tmp "literature-independent.json")
```

The expected SHA-256 values are:

```text
rooted discovery:
9fa31703b5c4721476b1b88f217d7455615c0d92c0d6db7f150abadfc069c2a0

rooted independent:
4ed239e997e4485abdab4e26a2e28e2a981b6fff069c4d926ccff3d2241dbe6f

indecomposable discovery:
bccde9635d973e030e004800abc08c37089e036faca1edc2bb85ed70ee731472

indecomposable independent:
4b90ef54358a14abc92c925c8e0f94ed9510b4f80857fde5aa4e2abf4ba89e2a

literature independent:
f884699b464a8b1b46b63cc15546f01b72c492ae54530750fcf00226b13d913b
```

Each regenerated file must also be byte-identical to its accepted JSON in
the corresponding package. Six Wave 32 manifests validate 42 entries:

| package | entries | manifest SHA-256 |
|---|---:|---|
| rooted discovery | 8 | `ba6c7099e06e24fe2feee4d19021dac9ddf49cbfe99acdd54f905a6c40728b8e` |
| rooted verifier | 7 | `2607c3000944e6d31ab5491a7d959ae4f97f05ac3e0d754baaf2830efcd085df` |
| indecomposable discovery | 7 | `451ca652a83b3a93fd11278c25dafe43bafabc3e06e1cac429064d32211d7138` |
| indecomposable verifier | 8 | `67dd65dd491ef28b4848bbb6c1e0ae47d3814db5b0a466462d7e9f79d5d4d6cd` |
| literature package | 6 | `9bdf458203beb32c76b993af2cb6130641546b5a7816f8bed507661e640173c6` |
| literature verifier | 6 | `b333f77785db6495040e5137b8cc8c9c70f283ed5dfac513ff92f98fd15f6b24` |

The exact Wave 32 scope wall is:

```text
rooted necessary Fano-support pattern:                 VERIFIED scoped
rooted partial-control extendibility:                  UNKNOWN
root exclusion / rooted endpoint:                      UNKNOWN
rootless decomposable actual-incidence endpoint:       VERIFIED impossible
rootless indecomposable necessary reductions:          VERIFIED scoped
actual incidence forces the forbidden row motif:       UNKNOWN
rootless indecomposable endpoint:                      UNKNOWN
n3=708 / Conway-99 / novelty:                          UNKNOWN
strongest conditional bound:                          n3>=708
```

The [rooted audit](verification/wave32-rooted-vector/audit.md),
[indecomposable audit](verification/wave32-indecomposable/audit.md),
[literature audit](verification/wave32-literature-audit-independent/audit.md),
and
[correction ledger](verification/2026-07-24-wave32-orchestrator-corrections.md)
record every premise, repair, hostile control, and nonpromotion wall.

The detached
[Wave 32 clean-clone replay](verification/2026-07-24-wave32-clean-clone.md)
freezes integration commit
`ad6329f80acb4a1cb6214a7ac2923f8436256b58`. In a no-local,
no-hardlink clone checked out in detached state, it repeats all 79 tests,
runs the five generators outside the checkout, validates all six manifests
and 42 entries, checks duplicate-ID-free YAML, 80 claims, 75 obligations,
1,430 evidence references, 87 BibTeX keys, 337 local links, exact Git-blob
privacy, clean status, and `git fsck --full --strict`.

## Wave 33 rooted extension and rootless contraction boundary

Run the four live-input packages and the construction chronology package
from the integrated repository root:

```powershell
python -B -m unittest discover `
  -s attempts\wave33-rooted-extension -p test_*.py -v
python -B -m unittest discover `
  -s attempts\wave33-rootless-motif -p test_*.py -v
python -B -m unittest discover `
  -s verification\wave33-rooted-extension -p test_*.py -v
python -B -m unittest discover `
  -s verification\wave33-rootless-motif -p test_*.py -v
python -B -m unittest discover `
  -s verification\wave33-rooted-construction-chronology -p "test_*.py" -v
```

The five current-tree commands report `15+14+33+48+20=130` outer tests.
The chronology suite performs one embedded `14+36=50` replay after
materializing the exact eight historical inputs in an isolated temporary
root.  The portable source-provenance half of the sole omitted composite
verifier test passes separately.  The solver-environment half, which depends
on ignored local files, is `NOT_REPLAYED_NONBLOCKING`; v2 opens zero such
files and observes zero environment hashes.  The original historical package
layer recorded `15+14+14+33+48+37=161`; the v2 clean-clone-independent
procedure reproduces 160 of those cases plus the separate portable source
gate.  The 20 outer chronology tests and embedded 50 original cases are
separate accounting layers.

Directly running the unchanged construction suites against the integrated
root is intentionally not a reproduction command.  Their frozen input
ledger predates the Wave 33 addition to mutable `STRUCTURE.md`, so those
programs correctly reject the later live byte.  The
[chronology audit](verification/wave33-rooted-construction-chronology/audit.md)
records the isolated replay.  Candidate discovery code was never imported
or executed by the rooted and rootless comparison checkers.

Regenerate the seven live-root outputs plus the construction chronology
result outside the checkout:

```powershell
$wave33Tmp = Join-Path `
  ([IO.Path]::GetTempPath()) `
  ("conway-wave33-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $wave33Tmp | Out-Null

python -B attempts\wave33-rooted-extension\exact_check.py `
  --output (Join-Path $wave33Tmp "rooted-discovery.json")
python -B attempts\wave33-rootless-motif\exact_check.py `
  --output (Join-Path $wave33Tmp "rootless-discovery.json")
python -B attempts\wave33-rooted-construction\search_partial_design.py `
  --output (Join-Path $wave33Tmp "partial-design.json") `
  --restarts 9 --steps 200000 --seed 3301
python -B verification\wave33-rooted-extension\independent_check.py `
  --output (Join-Path $wave33Tmp "rooted-independent.json")
python -B verification\wave33-rooted-extension\static_compare.py `
  --output (Join-Path $wave33Tmp "rooted-comparison.json")
python -B verification\wave33-rootless-motif\independent_check.py `
  --output (Join-Path $wave33Tmp "rootless-independent.json")
python -B verification\wave33-rootless-motif\candidate_static_check.py `
  --output (Join-Path $wave33Tmp "rootless-comparison.json")
python -B verification\wave33-rooted-construction-chronology\chronology_replay.py `
  --output (Join-Path $wave33Tmp "construction-chronology.json")
```

Expected accepted and chronology SHA-256 values follow. The construction
base and exact values are authenticated inside the chronology replay rather
than regenerated by a direct integrated-root command.

```text
rooted discovery:
193db8ee0c155cc3a97489b4471c4a82ae09823dd9344d043a81778e1a6ba5a1

rootless discovery:
2cfb576f2deba7bb82c60eb27c72a62c913d06f2d86f3eb626dcddd6ac75afeb

construction partial design:
340e5df716ad63bceba25c745ab04c22ea1a3dca01e939072f09775a5fc5f634

construction base:
97f30719cc41bb48c3b562faf5bc7037112cd8cf35c737b3717614217a9c1ea1

construction exact:
ba6640eacd041bc8349024a1d3f13e3d74bd67cdad64d2d78c9a94927319c496

construction chronology:
b2f0b872221a3fd9f41d6a88637be21034b70e8c8129fe57617115548b425957

construction historical-input archive (authenticated input):
d62fc4311577d56cbf34f8bd4e63aefb3b796457b3d020f4322324073d82f7dd

rooted independent:
66cef570dbbb4a86e2a35f780edcfc1873d0ac2c5266f1c2065c902a8f91e778

rooted comparison:
2e36ecade28bca12d35a963a8c6b52777ac7d766a3c4b3267774000fe2e929fd

rootless independent:
68911c124a039b32b2eb5fe4c1f9886c033e17129b8b97d7a428c4bda7968253

rootless comparison:
8b7b27fd67f12bb82cb6eebf645d0c46324d7227e51bdeb0093fbcdf9d753872
```

The construction chronology command above runs all 14 unchanged discovery
tests and 36 of the 37 unchanged verifier tests in the authenticated
historical root.  The omitted composite test is named in the chronology
result: its portable standard-library source audit is reperformed and passes,
while the solver-environment half, which depends on ignored local files, is
`NOT_REPLAYED_NONBLOCKING`; v2 opens zero such files and observes zero
environment hashes.  Chronology-owned code calls the hash-pinned portable
comparison functions directly, reproduces the hostile certificate, and binds
the compact accepted comparison summary.  It never calls the unchanged
comparison CLI or its local solver-environment verifier.  Do not run the
unchanged construction CLIs directly against the later integrated
`STRUCTURE.md`.

The construction chronology command takes about 17 seconds on the audited
machine and reconstructs the hostile certificate without importing or
executing the discovery search.  With `--output`, stdout contains only the
PASS/output/SHA-256 summary; the output JSON contains the comparison
projection.  The authenticated precomparison, accepted-summary, and
chronology projection hashes are:

```text
construction verifier precomparison:
c3e626a2dada92a4dd1178b327f8c74291beba3d408a150fb4ed2efe42106acb

construction verifier comparison:
c0476fb877e0e7d6a6fc63b1a4c72bda0d7804a18a4e4b2b6d5a1bcbc4b6b459

construction chronology comparison projection:
446beb4ddd2a51194315954d7005cb01d90ff8643a64c78801d93524d65e7818
```

The older raw comparison-CLI stdout hash
`7025cc30551e219c224fe068d641a202db9f1c7a39e480908933e9a93fe597c5`
is retained only as historical metadata with status `NOT_RUN_BY_DESIGN`; it
is not a new clean-clone replay result.

Seven original publication manifests contain 73 entries.  The chronology
repair adds a seven-entry eighth manifest, for 80 entries in all:

| package | entries | manifest SHA-256 |
|---|---:|---|
| rooted discovery | 8 | `153860d39fe7274a2f55ee952bcad1135cf4134ccc36d9aec07f6da379c5ca04` |
| rootless discovery | 8 | `384081a967153059399b4e0724e901ef28183cedab8d7e253e45af560e16df95` |
| construction discovery | 16 | `0cd192c0182506b3c901806cc96abb9fe53f04dc906b0b5cd73bc9b602558ff4` |
| rooted precomparison verifier | 8 | `a0cd7d284a23aba5576f2da2a1282c9acb209953c3da5d01e706d793f61d3ea7` |
| rooted comparison verifier | 6 | `50571e1870b7fafb245e2eaf79f8331a3b5d6c7cbd282a8bd2d8937b44898f76` |
| rootless final verifier | 13 | `e51811d3dd5a35d21a1e6c7f88625b9dfdabdd1097de1898f988b40747e82822` |
| construction final verifier | 14 | `20c27560bdf9720cd1cf043b11c218130cd2891a2d3c874f9dbc9bce2f27fbbf` |
| construction chronology | 7 | `22cbb94ad5a452e9e9c3f38ac35bb31f0b5d2cf81446d0aab5827c3d30b84f69` |

The exact Wave 33 scope wall is:

```text
rooted partition/design/finite graph criterion:       VERIFIED scoped
binary rooted criterion solution or exclusion:        UNKNOWN
rootless formal q=2 algebra and R2-board reductions:   VERIFIED scoped
actual global mixed-motif forcing or avoidance:        UNKNOWN
restricted one-design timeout:                         NO EVIDENCE
hostile O-Q partial object:                             VERIFIED finite
rooted / rootless indecomposable endpoints:            UNKNOWN
n3=708 / Conway-99 / novelty:                         UNKNOWN
strongest conditional bound:                          n3>=708
```

Read the
[rooted audit](verification/wave33-rooted-extension/comparison-audit.md),
[rootless audit](verification/wave33-rootless-motif/audit.md),
[construction audit](verification/wave33-rooted-construction/audit.md), and
[orchestrator ledger](verification/2026-07-24-wave33-orchestrator-corrections.md)
for the separation chronology, wording qualifier, checker coverage gaps,
replay mistakes, and unchanged global status.

The
[Wave 33 detached clean-clone replay](verification/2026-07-24-wave33-clean-clone.md)
checks exact integration commit
`66790bc326a6a8161567a2c2b5c32ed3cbffd279` in a no-local, no-hardlink
detached clone. It passes all 130 outer tests, byte-matches all eight
regenerations, validates 80 manifest entries and 401 status path/hash pairs,
checks 358 local links, scans the exact tree and all 118 new blobs, and
finishes with clean status and `git fsck --full --strict`.

## Wave 34 rooted and rootless continuation

Run the complete current-tree unit-test set from the repository root. The
full structural census is opt-in and must be enabled:

```powershell
$env:WAVE34_FULL_CENSUS = '1'

python -B -m unittest discover `
  -s verification\wave34-rooted-structural\precomparison -p "test_*.py" -v
python -B -m unittest discover `
  -s attempts\wave34-rooted-structural -p "test_*.py" -v
python -B -m unittest discover `
  -s verification\wave34-rooted-structural\pair-census-crosscheck -p "test_*.py" -v
python -B -m unittest discover `
  -s verification\wave34-integration-chronology -p "test_*.py" -v

python -B -m unittest discover `
  -s verification\wave34-rooted-encoding\precomparison -p "test_*.py" -v
python -B -m unittest discover `
  -s attempts\wave34-rooted-encoding -p "test_*.py" -v
python -B -m unittest discover `
  -s verification\wave34-rooted-encoding -p "test_independent_compare.py" -v

python -B -m unittest discover `
  -s verification\wave34-rootless-global\precomparison -p "test_*.py" -v
python -B -m unittest discover `
  -s attempts\wave34-rootless-global -p "test_*.py" -v
python -B -m unittest discover `
  -s verification\wave34-rootless-global -p "test_comparison_check.py" -v

python -B -m unittest discover `
  -s verification\wave34-external-source-audit\kuber-selub `
  -p "test_audit_sources.py" -v
python verification\wave34-external-source-audit\status-designs\validate_results.py
```

The direct current-tree unit-test commands report

```text
rooted structural, excluding frozen-status comparison: 44
rooted encoding:   28
rootless:          63
Kuber/Selub:        6
chronology protocol: 8
outer total:       149
```

The unchanged 11-test rooted structural comparison suite must be run through
the authenticated chronology wrapper after the integrated commit exists:

```powershell
python -B verification\wave34-integration-chronology\chronology_replay.py `
  --commit <exact-integrated-commit> `
  --output <temporary-rooted-structural-chronology.json>
```

That gives 152 original Wave 34 source/verifier cases plus eight chronology
protocol cases, or 160 executed cases across the current and authenticated
historical-input contexts. Direct integrated-root execution of
`test_static_compare.py` is expected to reject the later `STATUS.yaml`; the
retained failure and exact one-file substitution rule are in
`verification/wave34-integration-chronology/`.

The status/design validator is a separate machine-result gate. Harrison's
external-clone source replay requires its pinned dependency environment and
is not counted as a clean-clone unit test; its deterministic outputs and
missing-artifact boundaries are bound by its manifest.

The raw 89,546,779-byte CNF is intentionally ignored by Git. A clean clone
contains the deterministic gzip:

```text
attempts/wave34-rooted-encoding/rooted-complete.cnf.gz
SHA-256:
6b6beb5d49c7fe75b9b475162cc4bd97de2793389df150dfab9765ba497305f0
```

Before running the encoding comparison suite in a clean clone, decompress
that file to the ignored expected raw path and verify:

```text
raw SHA-256:
2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3
```

The independent comparison then regenerates and compares all 4,323,943
clauses. Remove the ignored raw file after the replay; it is not a tracked
publication artifact.

Regenerate the five live-root compact accepted machine results to paths
outside the checkout:

```powershell
$wave34Tmp = Join-Path `
  ([IO.Path]::GetTempPath()) `
  ("conway-wave34-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $wave34Tmp | Out-Null

python -B verification\wave34-rooted-structural\precomparison\exact_check.py `
  --output (Join-Path $wave34Tmp "rooted-structural-stage1.json")
python -B verification\wave34-rooted-structural\pair-census-crosscheck\crosscheck.py `
  --output (Join-Path $wave34Tmp "rooted-pair-census.json")
python -B verification\wave34-rooted-encoding\independent_compare.py `
  --output (Join-Path $wave34Tmp "rooted-encoding-comparison.json")
python -B verification\wave34-rootless-global\precomparison\independent_check.py `
  --output (Join-Path $wave34Tmp "rootless-stage1.json")
python -B verification\wave34-rootless-global\comparison_check.py `
  --output (Join-Path $wave34Tmp "rootless-stage2.json")
```

The Stage-2 structural result freezes the pre-integration `STATUS.yaml` and
must not be regenerated in the integrated root. Export the exact integration
commit to an isolated tree, replace only that file with the authenticated
continuation-base blob, and check both the frozen input and regenerated
output:

```powershell
$wave34I0 = "0e11485de2ccdf0c1f2aa1c3e2d53a3413d9b6ea"
$wave34Base = "0fa5b8161baf8b2a5404a67051b7d61cbc906da3"
$wave34Shadow = Join-Path $wave34Tmp "rooted-structural-shadow"
$wave34Frozen = Join-Path $wave34Tmp "rooted-structural-frozen"
$wave34IntegratedZip = Join-Path $wave34Tmp "integrated.zip"
$wave34StatusZip = Join-Path $wave34Tmp "status.zip"
New-Item -ItemType Directory -Path $wave34Shadow,$wave34Frozen | Out-Null

git archive --format=zip -o $wave34IntegratedZip $wave34I0
if ($LASTEXITCODE) { throw "integrated archive failed" }
git archive --format=zip -o $wave34StatusZip $wave34Base STATUS.yaml
if ($LASTEXITCODE) { throw "frozen STATUS archive failed" }
Expand-Archive -LiteralPath $wave34IntegratedZip -DestinationPath $wave34Shadow
Expand-Archive -LiteralPath $wave34StatusZip -DestinationPath $wave34Frozen

$frozenStatus = Join-Path $wave34Frozen "STATUS.yaml"
$frozenHash = (Get-FileHash -LiteralPath $frozenStatus `
  -Algorithm SHA256).Hash.ToLowerInvariant()
if ($frozenHash -ne `
  "feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864") {
  throw "frozen STATUS hash mismatch"
}
[IO.File]::WriteAllBytes(
  (Join-Path $wave34Shadow "STATUS.yaml"),
  [IO.File]::ReadAllBytes($frozenStatus)
)

$stage2Out = Join-Path $wave34Tmp "rooted-structural-stage2.json"
Push-Location $wave34Shadow
try {
  python -B verification\wave34-rooted-structural\static_compare.py `
    --output $stage2Out
  if ($LASTEXITCODE) { throw "Stage-2 regeneration failed" }
} finally {
  Pop-Location
}
$stage2Hash = (Get-FileHash -LiteralPath $stage2Out `
  -Algorithm SHA256).Hash.ToLowerInvariant()
if ($stage2Hash -ne `
  "d73e302d6af8bbd3df28c80ded5dc922e4e6ea5084234ed15531330646fc26d8") {
  throw "Stage-2 output mismatch"
}
```

The chronology wrapper above performs the same authenticated one-file
substitution for the unchanged 11-test suite.

Sixteen nonoverlapping publication manifests contain 130 entries:

| package | entries | manifest SHA-256 |
|---|---:|---|
| current literature | 5 | `496085f741e2cda7904e23888f3723b3d51544af6ba5393a35f47c81ecda6766` |
| rooted structural candidate | 5 | `fd1372a3e0013eec265f828a33249f5bb0872e505f7e8479d2946a0e917f32de` |
| rooted structural Stage 1 | 8 | `233a32ac6cb67bcb23b7b269cc6f3f889d943bd5d0714c4f54ead9cbf28c7681` |
| rooted structural Stage 2 | 7 | `ce4bb77f33e919c3086b09521acd80297a9dcfffbc6bb2b72b331c2ee650ae3c` |
| rooted pair-census crosscheck | 7 | `de3152c245367bdc8907983e9d0d3528d153a184d9690ed45e94e2b56b5b0891` |
| rooted encoding publication | 16 | `7cba8a082545cbfcbf01785e6e15a0198bd1cf2357ed0a2b3f353b564a1433e7` |
| rooted encoding Stage 1 | 11 | `3f1bdcb0ca2d08ee0380cd1435673fddb499db8c3a8273f6676c18f17ad3550c` |
| rooted encoding Stage 2 | 8 | `f76ae0aeac6c06ca5a0de1171b619664f558710dfe060cc1c41590b697098acd` |
| rootless candidate | 5 | `bda35ed81dcca9918cff3c544956039b8949a61bfa8a232e4e2d40edcd8d5af2` |
| rootless Stage 1 | 7 | `27c13fb233af677c1619d571bf73820cddd4451172fdd749ace1c9f65f8f3c8d` |
| rootless Stage 2 | 7 | `74d1aa2a95b3ce13a47a19fddafd6e78fec193a20fd92c035e2c872345c795bc` |
| status/design sources | 5 | `1af4bad56405fb24128285fa586e2d1e2b80c82f1bdffdafa7cbdb6053cd6812` |
| Harrison source audit | 11 | `6052d3114a89af378cf412cc3126b60bab9dc9fe249a673188d3369a681db386` |
| Kuber/Selub source audit | 14 | `5053217d6432365b903b787cb53e923996e96feef404904caad89dd7ebd686bc` |
| consolidated external audit | 7 | `f21ec00738093ac6579654c88bff3a0c9b35665c2dee83cd5cd9422b9eab483c` |
| integration chronology | 7 | `3faa49fef4f49471425e830c60caccac0779542e84fd8f6dca6f34d82b6c0de3` |

The encoding candidate's overlapping 18-entry local manifest and its run
manifest are validated separately but are not double-counted in the
publication total. The exact Wave 34 scope wall is:

```text
rooted structural reduction and pair census: VERIFIED scoped
rooted complete-domain CNF:                   VERIFIED encoding-only
rooted SAT/UNSAT or binary endpoint:           UNKNOWN
rootless local-fibre and endpoint lemmas:      VERIFIED scoped
rootless wedge/four-cycle/moment bounds:       DERIVED scoped
rootless motif forcing/avoidance:              UNKNOWN
external graph-level result imported:          NONE
n3=708 / Conway-99 / novelty:                  UNKNOWN
strongest conditional bound:                  n3>=708
```

The exact detached publication replay is recorded in
[`verification/2026-07-24-wave34-clean-clone.md`](verification/2026-07-24-wave34-clean-clone.md).

See the
[rooted structural audit](verification/wave34-rooted-structural/comparison-audit.md),
[rooted encoding audit](verification/wave34-rooted-encoding/comparison-audit.md),
[rootless audit](verification/wave34-rootless-global/audit.md),
[external-source audit](verification/wave34-external-source-audit/audit.md),
and
[orchestrator ledger](verification/2026-07-24-wave34-orchestrator-corrections.md).

## Wave 35 prism-free upper endpoint

Replay the discovery and independent spectral suites:

```powershell
.venv\Scripts\python -B -m unittest discover `
  -s attempts\wave35-n3-upper-spectral -p "test_*.py" -v
.venv\Scripts\python -B attempts\wave35-n3-upper-spectral\exact_check.py `
  --verify attempts\wave35-n3-upper-spectral\exact-results.json
.venv\Scripts\python -B -m unittest discover `
  -s verification\wave35-n3-upper-spectral -p "test_*.py" -v
.venv\Scripts\python -B verification\wave35-n3-upper-spectral\independent_check.py `
  --verify verification\wave35-n3-upper-spectral\independent-results.json
```

Replay the combinatorial and construction checks:

```powershell
.venv\Scripts\python -B -m unittest discover `
  -s attempts\wave35-n3-4158-combinatorial -p "test_*.py" -v
.venv\Scripts\python -B attempts\wave35-n3-4158-combinatorial\exact_check.py `
  --verify attempts\wave35-n3-4158-combinatorial\exact-results.json
.venv\Scripts\python -B -m unittest discover -s code `
  -p "test_wave35_n3_endpoint_local_extension.py" -v
```

Expected totals are 14 submitted spectral tests, 10 independent spectral
tests, 9 combinatorial tests, and 5 construction tests. The commands verify
exact conditional identities, finite reductions, and deterministic local
models only. Do not reinterpret `BUDGET_UNKNOWN`,
`TIMEOUT_UNKNOWN_NO_INCUMBENT`, fractional LP feasibility, or the absence of
an incumbent as a mathematical result.

```text
conditional spectral/Smith identities: VERIFIED scoped
combinatorial and rooted reductions:    DERIVED, pending independent promotion
solver evidence promoted:               NONE
rigorous interval:                      708 <= n3 <= 4158
n3=4158 / Conway-99:                    UNKNOWN
```

## Wave 36 modular, polar, and block checks

Replay the endpoint modular and ternary-polar discovery packages:

```powershell
.venv\Scripts\python -B -m unittest -v `
  attempts/wave36-modular-reflection/test_exact_check.py
.venv\Scripts\python -B attempts/wave36-modular-reflection/exact_check.py `
  --verify attempts/wave36-modular-reflection/exact-results.json
.venv\Scripts\python -B -m unittest -v `
  attempts/wave36-ternary-polar-bound/test_exact_check.py
.venv\Scripts\python -B attempts/wave36-ternary-polar-bound/exact_check.py `
  --verify attempts/wave36-ternary-polar-bound/exact-results.json
```

Replay their independent reconstructions:

```powershell
.venv\Scripts\python -B -m unittest -v `
  verification/wave36-modular-reflection/test_independent_check.py
.venv\Scripts\python -B verification/wave36-modular-reflection/independent_check.py `
  --verify verification/wave36-modular-reflection/independent-results.json
.venv\Scripts\python -B -m unittest -v `
  verification/wave36-ternary-polar-bound/test_independent_check.py
.venv\Scripts\python -B `
  verification/wave36-ternary-polar-bound/independent_check.py `
  --verify verification/wave36-ternary-polar-bound/independent-results.json
```

Replay the one-triangle discovery and independent block checks:

```powershell
.venv\Scripts\python -B -m unittest -v `
  attempts/wave36-block-compatibility/test_exact_check.py
.venv\Scripts\python -B attempts/wave36-block-compatibility/exact_check.py `
  --verify attempts/wave36-block-compatibility/exact-results.json
.venv\Scripts\python -B -m unittest -v `
  verification/wave36-block-compatibility/test_independent_check.py
.venv\Scripts\python -B `
  verification/wave36-block-compatibility/independent_check.py `
  --verify verification/wave36-block-compatibility/independent-results.json
```

Expected totals are 11 submitted and 11 independent modular tests, 10
submitted and 12 independent ternary-polar tests, and 10 submitted and 12
independent block tests.  The exact promoted scope is:

```text
rank_F3(M)>=12 and rank_F7(M)>=11:       VERIFIED scoped
rank-12 nonsquare ternary factor:        excluded
reciprocal Smith pairing:                VERIFIED scoped
mixed one-triangle equations and census: VERIFIED scoped
simultaneous B/H completion:             UNKNOWN
n3 upper bound below 4158:               not obtained
Conway-99:                               UNKNOWN
```

## Wave 37 rooted, finite-polar, and proof-formula checks

Replay the rooted and finite-polar discovery packages:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave36-rooted-branches -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave37-polar-strengthen -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave37-polar-strengthen\exact_check.py `
  --verify attempts\wave37-polar-strengthen\exact-results.json
```

Rebuild and audit the branch-15 OPB artifact:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave37-proof-producing-endpoint\export_endpoint_opb.py `
  --refined-branch 15 `
  --opb attempts\wave37-proof-producing-endpoint\branch-15.opb `
  --metadata attempts\wave37-proof-producing-endpoint\branch-15-formula.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave37-proof-producing-endpoint -p "test_*.py" -v
```

Replay the three independent packages:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave37-rooted-branches -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave37-rooted-branches\independent_check.py `
  --verify verification\wave37-rooted-branches\independent-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave37-polar-strengthen -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave37-polar-strengthen\independent_check.py `
  --verify verification\wave37-polar-strengthen\independent-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave37-proof-producing-endpoint -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave37-proof-producing-endpoint\independent_check.py `
  --verify `
  verification\wave37-proof-producing-endpoint\independent-results.json
```

Expected totals are 8 rooted, 13 polar, and 5 OPB discovery tests, plus
5 rooted, 6 polar, and 5 OPB independent tests: 42 tests in total. The
formula verifier independently reconstructs all 574,615 constraints, but
does not decide satisfiability.

```text
fixed-triangle clause catalogs: VERIFIED scoped
ternary/code restrictions:      VERIFIED scoped
branch-15 OPB artifact:          VERIFIED artifact-only
solver conclusion promoted:     NONE
rigorous interval:              708 <= n3 <= 4158
n3=4158 / Conway-99:            UNKNOWN
```

## Wave 38 queue, complete-prism, coclique, and higher-order checks

Replay the read-only solver-harvest packages:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave38-solver-harvest -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave38-solver-harvest -p "test_*.py" -v
```

These commands check the exact 33-case queue and zero proof coverage; they do
not start, stop, or attach to a solver.

Replay the complete all-prism construction and independently bind the fixture
catalog and pool:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave38-complete-endpoint -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave38-complete-endpoint\prism_oracle.py `
  --candidate attempts\wave38-complete-endpoint\fixture-residual-prism.json `
  --catalog attempts\wave38-complete-endpoint\fixture-residual-prism-cuts.json `
  --verify-only
.\.venv\Scripts\python.exe -B `
  attempts\wave38-complete-endpoint\cut_pool.py `
  --catalog attempts\wave38-complete-endpoint\fixture-residual-prism-cuts.json `
  --pool attempts\wave38-complete-endpoint\fixture-cut-pool.json `
  --verify-only
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave38-complete-endpoint -p "test_*.py" -v
```

The static inventory is only a size/schema calculation. Do not invoke the
guarded 24-billion-clause stream on the current host.

Replay the coclique-rank discovery and independent packages:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave38-coclique-rank -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave38-coclique-rank\exact_check.py `
  --verify attempts\wave38-coclique-rank\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave38-coclique-rank -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave38-coclique-rank\independent_check.py `
  --verify verification\wave38-coclique-rank\independent-results.json
```

Replay the higher-order discovery and independent packages:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave38-higher-order -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave38-higher-order\exact_check.py `
  --verify attempts\wave38-higher-order\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave38-higher-order -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave38-higher-order\independent_check.py `
  --verify verification\wave38-higher-order\independent-results.json `
  --compare-submission attempts\wave38-higher-order\exact-results.json
```

```text
solver terminal evidence:    NONE
endpoint proof coverage:     0 / 33
rank_F7(M)>=13:              VERIFIED
rigorous interval:           708 <= n3 <= 4158
n3=4158 / Conway-99:         UNKNOWN
```

## Wave 39 edge-local rank and proof-shard checks

Replay the edge-local discovery and clean-room verification:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave39-edge-local-rank -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave39-edge-local-rank\exact_check.py `
  --output $env:TEMP\wave39-edge-local-rank.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave39-edge-local-rank -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave39-edge-local-rank\independent_check.py `
  --output $env:TEMP\wave39-edge-local-rank-independent.json
```

The independent command exhausts all 10,395 pulled-back matchings and
reconstructs the eleven partitions and rank formula without importing the
discovery implementation.

Replay the branch-15 proof shard:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave39-proof-solver -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave39-proof-solver\verify_certificate.py `
  attempts\wave39-proof-solver\branch-15-x187-positive-certificate.json `
  --output $env:TEMP\wave39-proof-shard.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave39-proof-solver -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave39-proof-solver\independent_check.py `
  --output $env:TEMP\wave39-proof-shard-independent.json
```

The compressed OPB and raw/kernel VeriPB proofs are retained in the attempt
package. The uncompressed `.opb` is reproducible and ignored. Fresh strict
VeriPB replay is part of the independent verifier; CakePB supplied no
conclusion.

Replay the two exact discovery-only compatibility lanes:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave39-cross-base-rank -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave39-cross-base-rank\exact_check.py `
  --output $env:TEMP\wave39-cross-base-rank.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave39-simultaneous-bh -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave39-simultaneous-bh\exact_check.py `
  --output $env:TEMP\wave39-simultaneous-bh.json
```

```text
Wave 39 tests:                         62 / 62 PASS
rank_F7(M)>=19:                       VERIFIED
branch15 AND x187=1:                  VERIFIED UNSAT
complete endpoint proof coverage:     0 / 33
rigorous interval:                     708 <= n3 <= 4158
n3=4158 / Conway-99 / novelty:         UNKNOWN
```

## Wave 40 universal rank and edge-coupling checks

Replay the rank-22 stepping stone, the rank-25 discovery package, and its
clean-room verifier:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave40-rank19-equality -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave40-rank19-equality -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave40-rank19-equality\independent_check.py `
  --verify verification\wave40-rank19-equality\independent-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave40-exact-coupling-model -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave40-exact-coupling-model\exact_check.py `
  --verify attempts\wave40-exact-coupling-model\exact-results.json `
  --certificate attempts\wave40-exact-coupling-model\subspace-certificate.json
.\.venv\Scripts\python.exe -B `
  attempts\wave40-exact-coupling-model\full_block_scout.py `
  --verify attempts\wave40-exact-coupling-model\full-block-scout-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave40-exact-coupling-model -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave40-exact-coupling-model\independent_check.py `
  --verify verification\wave40-exact-coupling-model\independent-results.json
```

The discovery and verification implementations are independent. Each covers
all eleven edge partitions and all third-fibre permutations through complete
projective-subspace and bipartite-matching certificates.

Replay the global edge-type and one-triangle lift packages:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave40-edge-type-coupling -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave40-edge-type-coupling\exact_check.py `
  --verify attempts\wave40-edge-type-coupling\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave40-edge-type-coupling -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave40-edge-type-coupling\independent_check.py `
  --verify verification\wave40-edge-type-coupling\independent-results.json
```

```text
rank_F7(M)>=25:                     VERIFIED
endpoint arithmetic rank pairs:     330
complete endpoint proof coverage:    0 / 33
rigorous interval:                   708 <= n3 <= 4158
n3=4158 / Conway-99 / novelty:       UNKNOWN
```

## Wave 43 endpoint rank, lift census, branch cuts, and count deck

Replay the conditional rank-28 theorem and its independent verifier:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave43-rank28-motif -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave43-type33-rank2 -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave43-rank28 -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave43-rank28\independent_check.py --verify `
  verification\wave43-rank28\independent-results.json --deterministic
.\.venv\Scripts\python.exe -B `
  verification\wave43-rank28\comparison_check.py --verify `
  verification\wave43-rank28\comparison.json
```

Replay the two scoped structural verifiers:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave43-all-rank33-lifts\independent_check.py --verify `
  verification\wave43-all-rank33-lifts\independent-results.json
.\.venv\Scripts\python.exe -B `
  verification\wave43-branch15-two-triangle\independent_check.py --verify `
  verification\wave43-branch15-two-triangle\independent-results.json
```

The branch-15 replay scans the full frozen OPB and can take roughly two
minutes. It proves only the named clause catalogue and probe record.

Replay the compact three-way-matching formulation tests and the independently
checked unrooted order-seven count witness:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave43-joint-completion -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave43-seven-deck-endpoint\endpoint_deck.py --verify `
  attempts\wave43-seven-deck-endpoint\exact-results.json
.\.venv\Scripts\python.exe -B `
  verification\wave43-seven-deck-endpoint\independent_check.py `
  --verify verification\wave43-seven-deck-endpoint\independent-result.json
```

The retained CaDiCaL and MILP records are `UNKNOWN`; do not treat their solver
statuses as certificates.

## Wave 44 aggregate rooted-count control

Replay the exact rooted witness and its clean-room verifier:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave44-rooted-flags\exact_check.py --verify `
  attempts\wave44-rooted-flags\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave44-rooted-flags -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave44-rooted-flags\independent_check.py --verify
```

The exact witness, not the discovery solver, is the certificate. The
historical HiGHS `infeasible` status is a retained false negative.

## Wave 45 rooted flag moments

Replay the independent finite-moment construction and immutable checkpoint:

```powershell
.\.venv\Scripts\python.exe `
  attempts\wave45-flag-moment\replay-v1.py
.\.venv\Scripts\python.exe -B `
  verification\wave45-flag-moment\independent_verify.py --verify `
  verification\wave45-flag-moment\independent-results.json
.\.venv\Scripts\python.exe -B `
  verification\wave45-flag-moment\compare_discovery.py --verify `
  verification\wave45-flag-moment\comparison-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave45-flag-moment -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave45-flag-moment\manifest_check.py
```

Only the no-clobber `checkpoint-v1-*` discovery files are in verification
scope. Mutable cutting-plane files and later live runs are not checkpoint-v1
evidence. A terminal `unknown` or timeout is not an infeasibility certificate.

The combined detached clean-source replay for Waves 21-24 is recorded in
`verification/2026-07-23-wave24-clean-clone.md`. It runs 278 submitted and
independent tests, regenerates 15 exact files from 14 commands, checks seven
publication manifests and the 108 status path/hash pairs present at the
replayed commit, scans both the release tree and all unpublished Git history
for credential-shaped or private-path payloads, and finishes with a clean
tracked tree and `git fsck --full --strict`.

The separate `attempts/wave20-n3-63-structural` package is archival. Its
14/14 tests and exact JSON replay pass, but its proof remains
`DERIVED_PENDING_INDEPENDENT_AUDIT`; the first false two-profile census is
retained as `REJECTED`, and the repaired census contains 18 profiles. The
verified global theorem numerically supersedes that lane without certifying
its derivation.

An archival UNSAT claim would require the complete public OPB formula, a
complete proof from a pinned producer, and successful independent checking.
The alternative sequential-counter CNF/LRAT route remains available. No
target proof currently exists in either format.

Validate a future Conway-format certificate using the frozen defaults:

```powershell
python verification/check_srg.py candidates/conway-99.srg.json
```

No such target certificate is currently claimed. `STATUS.yaml` remains the
authoritative machine-readable status.

## Waves 56--59 alternative-space replay

Replay the closure discovery and independent verifier:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave56-percolation-closure\percolation_closure.py --verify `
  attempts\wave56-percolation-closure\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave56-percolation-closure -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave56-percolation-closure\independent_check.py `
  --discovery attempts\wave56-percolation-closure\exact-results.json `
  --verify-output verification\wave56-percolation-closure\independent-result.json
```

Replay the corrected star-complement and cross-incidence packages:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave57-star-complement\independent_check.py `
  --verify verification\wave57-star-complement\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave57-star-complement -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  attempts\wave58-cross-incidence-rank\exact_check.py `
  --verify attempts\wave58-cross-incidence-rank\exact-results.json
.\.venv\Scripts\python.exe -B `
  verification\wave58-cross-incidence-rank\independent_check.py `
  --verify verification\wave58-cross-incidence-rank\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave58-cross-incidence-rank -p "test_*.py" -v
```

Wave 57 must be read with its verifier correction. The replay proves no
simultaneous `B,A_Y` system and no endpoint conclusion.

Replay the incidence-spectrum discovery and independent verifier:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave59-incidence-spectral-excess\incidence_spectral.py `
  --verify attempts\wave59-incidence-spectral-excess\exact-result.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave59-incidence-spectral-excess -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification\wave59-incidence-spectral-excess\independent_verifier.py `
  --compare-discovery attempts\wave59-incidence-spectral-excess\exact-result.json `
  --output verification\wave59-incidence-spectral-excess\independent-result.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave59-incidence-spectral-excess -p "test_*.py" -v
```

Wave 59 verifies conditional finite identities and non-distance-regularity.
It proves neither endpoint nonexistence nor a strict upper bound.

## Waves 130 and 132--134 alternative-space replay

Replay the exact cutoff-28 Jacobi point and its independent no-cache
reconstruction:

```powershell
$env:PYTHONPATH='attempts/wave130-cdd-exact-lp'
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts/wave130-cdd-exact-lp -p test_exact_cdd_lp.py -v
.\.venv\Scripts\python.exe -B `
  verification/wave130-cdd-exact-lp/independent_no_cache_verify.py `
  --verify verification/wave130-cdd-exact-lp/independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification/wave130-cdd-exact-lp -p "test_*.py" -v
```

Replay the distinguished split-enumerator package:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts/wave132-distinguished-biweight -p "test_*.py" -v
$wave132Manifest = (Get-FileHash -Algorithm SHA256 `
  attempts/wave132-distinguished-biweight/package-manifest.sha256).Hash.ToLowerInvariant()
.\.venv\Scripts\python.exe -B `
  verification/wave132-distinguished-biweight/verify_wave132.py `
  --repository . `
  --package attempts/wave132-distinguished-biweight `
  --expected-manifest $wave132Manifest
```

Replay the rooted-triangle holonomy and abstract surface control:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts/wave133-triangle-holonomy-topology -p "test_*.py" -v
$wave133Manifest = (Get-FileHash -Algorithm SHA256 `
  attempts/wave133-triangle-holonomy-topology/package-manifest.sha256).Hash.ToLowerInvariant()
.\.venv\Scripts\python.exe -B `
  verification/wave133-triangle-holonomy-topology/verify_wave133.py `
  --repository . `
  --package attempts/wave133-triangle-holonomy-topology `
  --expected-manifest $wave133Manifest
```

These replays certify finite or abstract controls only. They do not construct
a graph, exclude rank 28 or the endpoint, or improve the rigorous interval
`708<=n3<=4158`.

Replay the corrected quaternary forced-word and transform package and its
independent verifier:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts/wave134-z4-symmetrized-enumerator/exact_check.py `
  --verify attempts/wave134-z4-symmetrized-enumerator/exact-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts/wave134-z4-symmetrized-enumerator -p "test_*.py" -v
.\.venv\Scripts\python.exe -B `
  verification/wave134-z4-symmetrized-enumerator/independent_verify.py `
  --verify verification/wave134-z4-symmetrized-enumerator/independent-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification/wave134-z4-symmetrized-enumerator -p "test_*.py" -v
```

This certifies the corrected code-type, forced-word, and transform-state
derivations only. The corrected rational and integral enumerator systems were
not solved and remain `UNKNOWN_NOT_RUN`.

## Waves 135--142 quadratic/code/interlace replay

Replay the tightened quaternary face and its clean-room verifier:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts/wave135-z4-exact-face -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification/wave135-z4-exact-face -p "test_*.py" -v
```

Both exact row-generation records remain `UNKNOWN_WALL`.  Do not infer
infeasibility from that status.

Replay the additive-`GF(4)` graph-state and Arf/Krawtchouk packages:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification/wave136-alternative-spaces -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts/wave137-z4-arf-branches -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification/wave137-arf-krawtchouk -p "test_*.py" -v
```

The Wave 137 outputs are exact rational formal witnesses.  They do not
construct an additive code or graph.

Replay the two-adic Arf-sign boundary:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts/wave140-arf-sign-lattice -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification/wave140-arf-sign-lattice -p "test_*.py" -v
```

The opposite-sign controls are local algebraic controls, not zero-one
strongly regular adjacency matrices.

Replay the bivariate graph-code bridge:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts/wave141-bivariate-graph-code/exact_check.py --verify
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts/wave141-bivariate-graph-code -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification/wave141-bivariate-graph-code -p "test_*.py" -v
```

The numerical scout is telemetry only.  The exact evidence is the
Krawtchouk transform, `D8` rank, low rows, and `S6/n3` identity.

Replay the interlace/isotropic discovery and verifier:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts/wave142-interlace-isotropic -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification/wave142-interlace-isotropic -p "test_*.py" -v
```

Read the verifier report before using the discovery result.  It vetoes the
unsupported sizes 86--91 top band and retains only sizes 92--99.  The valid
local interlace rows give no improvement over `n3<=4158`.

## Waves 143--147 projection and overlap replay

Replay the binary `S6` projection with the environment that supplies
`python-flint`:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave143-binary-s6-projection -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave143-binary-s6-projection -p "test_*.py" -v
```

The verifier report is mandatory reading.  The rational points impose a
formal dual-distance-15 slice not proved for the graph; only minimum eight is
target-forced.

Replay the exact six-set outside-profile package and its clean-room verifier:

```powershell
python -B -m unittest discover `
  -s attempts\wave144-sixset-odd-profile -p "test_*.py" -v
python -B -m unittest discover `
  -s verification\wave144-sixset-odd-profile-cleanroom -p "test_*.py" -v
```

The 65-cell endpoint certificate is an aggregate integer witness, not a
consistent assignment to overlapping six-sets.

Replay the corrected Wave 139/145 additive-`GF(4)` audit:

```powershell
python -B -m unittest discover `
  -s verification\wave139-gf4-lower-aggregation -p "test_*.py" -v
```

This audit refutes `max` aggregation and the proposed pure-`Y` zero rows
8, 10, and 12.  It does not solve the corrected feasibility problem.

Replay the Wave 146 rooted six-to-seven exact witness:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave146-six-seven-coupling\exact_witness.py `
  --verify attempts\wave146-six-seven-coupling\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave146-six-seven-coupling -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave146-six-seven-coupling -p "test_*.py" -v
```

The stored sparse rational vector, not the retained HiGHS diagnostics, is the
certificate.  It proves feasibility only of the one-root aggregate
relaxation at `n3=4158`.

Replay the Wave 147 two-root/order-eight coefficient package:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave147-alternative-lane -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave147-pair-root-order8 -p "test_*.py" -v
```

Wave 147 builds exact PSD coefficient data and a positive control but does
not run an endpoint SDP or produce a rational dual bound.

`requirements-search.txt` pins the prototyping API version, but it is not an
archival proof lockfile. Before a proof-producing run, also pin the Python ABI,
wheel hashes, proof-producing solver binary, and independent checker binaries,
then record their cryptographic hashes in the run manifest. The current Exact,
VeriPB, and CakePB identities and hashes are in the calibration report.

## Artifact retention

Small certificates and verification reports belong in Git. Large CNF, LRAT,
solver logs, and checkpoints should be stored in a content-addressed release or
archive. Commit a manifest containing cryptographic hashes and retrieval URLs.
Never treat an unavailable artifact as verified evidence.
