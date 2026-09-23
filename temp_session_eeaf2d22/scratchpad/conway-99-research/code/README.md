# Discovery code

Search encodings, heuristic construction tools, and structural-analysis code
live here. They may suggest candidates or prove restricted exhaustive results,
but they are not the final trust boundary.

## Root scaffold

`root_model.py` deterministically constructs the 14 root-neighbor coordinates,
the 84 allowed pair labels, their incidence matrix data, and 13 generators for
the rooted scaffold relabeling group `C2 wreath S7`. It checks the fixed
identity `B B^T = 11 I + J - M` and the linear neighbor-incidence targets.

```powershell
python code/root_model.py
.venv\Scripts\python -m unittest discover -s code -p "test_*.py" -v
```

For direct common-neighbor linearization, the full model begins with 3,486
unknown residual edge variables and 285,852 conjunction auxiliaries. This count
is diagnostic, not a claim that the direct encoding is the best search method.

## Direct SAT prototype

`sat_model.py` translates the two exact block equations into CNF or a native
cardinality formula. Its default
`compact` variant uses one-way wedge implications and common-neighbor upper
bounds; a global wedge count proves these are exact. The larger `direct`
variant keeps full conjunction equivalences and exact common-neighbor sums as a
cross-check. The default CNF backend uses sequential counters; the native
backend retains exact `AtMost` constraints. Neither makes a completed-graph
automorphism assumption. The proof of compact exactness is recorded in
`attempts/2026-07-22-compact-sat-encoding.md`.

The independently reviewed `native` cardinality backend represents the same
compact constraints directly for MiniCard. It removes sequential-counter
auxiliaries but does not change the mathematics:

```powershell
.venv\Scripts\python code/sat_model.py --pair-count 2 `
  --cardinality native --solve
.venv\Scripts\python code/scout_branches.py --cardinality native `
  --fresh-solvers --conflict-budget 100000
```

`--fresh-solvers` launches one isolated Python process per branch and
materializes branch decisions as unit clauses. This avoids sharing embedded
solver state between branches; startup time is included in each wall time.

For the target this has 289,338 variables, 285,852 ordinary clauses, and
5,838 native `AtMost` constraints. MiniCard has no accepted proof-logging path
in this project, so embedded solves are discovery-only. The same native formula
can be exported canonically with `--opb` and sent to the pinned
Exact/VeriPB/CakePB path. Sequential-counter CNF plus LRAT remains an
alternative. See `attempts/2026-07-22-native-cardinality.md` and
`verification/2026-07-22-veripb-calibration.md`.

The small `pair_count=2` instance reconstructs an `srg(9,4,1,2)`. Embedded
solver output for `pair_count=3` is still labeled `UNSAT_UNVERIFIED`, but the
same negative-control formula now has independently checked LRAT and VeriPB
proofs. Run both controls before any target experiment:

```powershell
.venv\Scripts\python -m unittest discover -s code -p "test_*.py" -v
.venv\Scripts\python code/sat_model.py --pair-count 2 --solve `
  --candidate candidates/calibration-srg-9.srg.json
python verification/check_srg.py candidates/calibration-srg-9.srg.json `
  --vertices 9 --degree 4 --lambda 1 --mu 2
```

A solver's `UNSAT` status alone is not accepted. `--cnf` and `--opb` retain
exact instances for external pinned proof-producing solvers. The PySAT
in-process proof path is intentionally disabled because adversarial
verification found unstable or incomplete traces on the current Windows/Python
build. Any proof artifact must pass independent checking before promotion.

## Theorem-forced `N3` normalization

For the target only, `--n3` fixes one induced six-vertex `N3` obtained by
combining Makhnev's cited theorem with the project's `DERIVED` inference. Global
relabeling then reduces the normalization to the single residual edge unit
`x24=1`:

```powershell
.venv\Scripts\python code/sat_model.py --pair-count 7 --n3 `
  --cardinality native --opb logs/local/conway99-n3-native-lf.opb
```

The flag is rejected on calibration sizes. Both CLI and direct API also reject
combining it with the legacy `--branch` representatives: fixing the witness
changes the stabilizer, so those 11 representatives are no longer a proved
complete joint cover. See `agents/2026-07-22-wave4-n3-normalization.md` and
`verification/2026-07-22-n3-normalization-audit.md`.

The separately proved replacement is a 12-branch cover on the invariant
shared fiber `S_2`:

```powershell
.venv\Scripts\python code\matching_orbits.py --n3-joint
.venv\Scripts\python code\sat_model.py --pair-count 7 --n3 `
  --n3-branch 1 --cardinality native `
  --opb logs\local\conway99-n3-branch-01.opb
```

The normalized stabilizer has order 768. Its 945 compatible fiber matchings
split into 12 exact orbits. Each branch fixes all 66 shared-fiber edges, with
six positive and 60 negative units; `+24` is already supplied by `--n3`, so
the branch itself adds 65 clauses. The certificate and independent checker are
under `verification/n3-joint-cover/`.

## Wave 35 prism-free endpoint models

`wave35_n3_endpoint_root_scout.py` adds the 84 exact negative residual-edge
units forced by `n3=4158`, intersects them with the verified 12-way normalized
`N3` cover, and reproduces the five surviving branches
`4,5,8,10,12`. Solver use is optional and discovery-only.

`wave35_n3_endpoint_local_extension.py` exports deterministic OPB
relaxations for the four one-edge cycle partitions `2+2+2`, `2+4`, `3+3`,
and `6`. Each reduced model has 5,184 binary variables and 380 equality rows.
The model omits adjacencies among 72 outside vertices and is not a graph
encoding.

```powershell
.venv\Scripts\python -B -m unittest discover -s code `
  -p "test_wave35_n3_endpoint_local_extension.py" -v
```

The exact instances and bounded, non-evidentiary scout records are under
`attempts/wave35-n3-upper-triple-overlap/`.

## Refined `N3` common-neighbor cover

The exact coordinate-4 profile of `label(0,2)` forces one additional neighbor
besides the normalized `label(2,4)`. Orienting the witness reduces the safe
stabilizer to `C2 wreath S4`, of order 384. Its action on 945 matchings times
eleven additional-neighbor choices has 78 verified orbits:

```powershell
.venv\Scripts\python code\matching_orbits.py --n3-refined
.venv\Scripts\python verification\n3-refined-cover\verify.py
.venv\Scripts\python code\sat_model.py --pair-count 7 --n3 `
  --n3-refined-branch 1 --cardinality native `
  --opb logs\local\conway99-n3-refined-001.opb
```

One refined case contains the parent matching decisions plus one additional
positive edge. From the unnormalized target base, `--n3` and the refined case
add 67 unit clauses in total: seven positive and 60 negative. The option is
mutually exclusive with `--n3-branch` and the legacy `--branch`. The public
certificate and standard-library checker are under
`verification/n3-refined-cover/`.

## Eleven complete matching branches

`matching_orbits.py` exhausts all 10,395 perfect matchings in one 12-vertex
endpoint fiber and independently traverses the action generated by `C2 wreath
S6`, verifying exactly 11 orbits indexed by partitions of six. This produces a
safe complete split:

```powershell
python code/matching_orbits.py
.venv\Scripts\python code/sat_model.py --pair-count 7 --branch 3+2+1
```

One branch is conditional; all 11 together cover the full rooted search.
This statement concerns the legacy unnormalized search. Do not combine these
representatives with `--n3`; use `--n3-branch 1..12` for the separately
verified normalized split.

Use a conflict budget for scouting runs that must terminate reproducibly:

```powershell
.venv\Scripts\python code/sat_model.py --pair-count 7 --branch 6 --solve `
  --conflict-budget 1000
```

`UNKNOWN` at the budget is expected and has no mathematical evidentiary value.

For a bounded pass over all 11 branches, `scout_branches.py` reuses one
incremental solver and carries learned clauses between assumption branches:

```powershell
.venv\Scripts\python code/scout_branches.py --conflict-budget 100
```

This is explicitly a scouting workflow. An `UNSAT` branch must be regenerated
with its decisions as unit clauses and accompanied by a separately checked
proof before it counts as evidence.

## Wave 12 `n3=42` discovery tools

The Wave 12 programs are discovery-lane artifacts with explicit scope labels:

- `wave12_n3_42_active.py` replays the six active profiles, local flower
  obstructions, and the retained weakened active-local candidate;
- `wave12_n3_42_size2_scout.py` regenerates that restricted SAT candidate;
- `wave12_n3_42_size2_caps.py` runs the first 112-type all-size-two support
  census; and
- `test_wave12_n3_42.py` supplies four focused regression tests.

```powershell
.venv\Scripts\python code\wave12_n3_42_active.py `
  --certificate attempts\wave12-computation\n3-42-size2-active-local-candidate.json
.venv\Scripts\python code\wave12_n3_42_size2_caps.py `
  --catalog attempts\wave12-computation\n3-42-cubic-trianglefree-14.g6
.venv\Scripts\python code\test_wave12_n3_42.py -v
```

The restricted SAT object and the construction-lane zero-survivor census are
kept as `CANDIDATE` evidence. The promoted conditional exclusion depends on
the independent proof reduction, second catalog, proof certificate, and
adversarial reports under `verification/n3-42-equality/`; the discovery code
does not certify itself.

## Wave 13 `n3=45` discovery tools

The Wave 13 programs enumerate the nine `sum q=30` profiles, mixed-profile
local reductions, order-fifteen flower and root-mode censuses, and a restricted
active-local SAT model:

- `wave13_n3_45_profiles.py` regenerates the exact local census;
- `wave13_n3_45_active_sat.py` builds and validates the restricted formulas;
- `wave13_n3_45_test.py` supplies 12 current v2 regression, provenance, and
  hostile-mutation tests.

```powershell
$env:PYTHONPATH='code'
.venv\Scripts\python code\wave13_n3_45_profiles.py --json
.venv\Scripts\python code\wave13_n3_45_test.py -v
.venv\Scripts\python code\wave13_n3_45_active_sat.py `
  --validate attempts\wave13-computation\n3-45-no-common-point-m5-111.json
```

The first archived bundle failed independent self-validation: its mixed census
omitted four ordered `q=3` subcases, its validator left material fields and the
root claim unbound, and its archived positive object was not direct output of
the frozen source. Those artifacts and the FAIL report remain in Git history.
The repaired v2 schema checks all seven ordered subcases, raw canonicality,
root/status/restriction/formula/source metadata, and complete integrity
coverage. A fresh audit reproduced all 17 exact formula streams, checked the
positive model clause-by-clause, and rejected 31 hostile mutations.

The 17 solver-negative branches still have no checked proof trace and remain
`UNSAT_UNVERIFIED`. This discovery computation is not the proof of the
conditional `n3=45` exclusion; that promotion depends on the separately
written and twice-audited human reduction. Conway-99 and novelty remain
`UNKNOWN`.

## Wave 14 `n3=48` discovery tools

The Wave 14 programs enumerate twelve `sum q=32` profiles, replay the finite
flower and local-mode reductions, and build a deliberately scoped active-local
SAT model:

- `wave14_n3_48_profiles.py` generates the exact profile, flower, local-state,
  and finite branch census;
- `wave14_n3_48_active_sat.py` materializes thirteen exact formula streams and
  the bounded discovery scan;
- `wave14_n3_48_verify.py` validates the archived census, positive objects,
  controls, formula hashes, provenance, and status boundary; and
- `wave14_n3_48_test.py` supplies seven focused regression and hostile-mutation
  tests.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.venv\Scripts\python code\wave14_n3_48_profiles.py `
  --output attempts\wave14-computation\n3-48-profile-census.json
.venv\Scripts\python code\wave14_n3_48_verify.py `
  --output attempts\wave14-computation\n3-48-independent-validation.json
.venv\Scripts\python code\wave14_n3_48_test.py -v
```

The exact scan status is `1 SAT_CANDIDATE / 7 UNSAT_UNVERIFIED /
1 BUDGET_UNKNOWN / 2 TIMEOUT_UNKNOWN`. The solver negatives have no checked
proof traces. The positive objects encode only the active-local layer and are
not `H`, partial Conway graphs, or target certificates. The independently
audited human lane reduces equality to a finite support residual but does not
exclude it; the verified bound stays `n3>=48`.

## Wave 16 `n3=51` discovery tools

The Wave 16 programs enumerate all sixteen `sum q=34` profiles, derive a
seven-branch active-local cover, materialize exact CNF streams, and validate
their public archive:

- `wave16_n3_51_profiles.py` regenerates the profile and rooted-local census;
- `wave16_n3_51_active_sat.py` builds the branch CNFs, bounded scan, and raw
  positive relaxation candidate;
- `wave16_n3_51_verify.py` checks profiles, finite reductions, raw candidate,
  all seven formula hashes, provenance, and 20 hostile mutations; and
- `wave16_n3_51_test.py` supplies eight focused regressions.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.venv\Scripts\python code\wave16_n3_51_profiles.py `
  --output attempts\wave16-n3-51-computation\n3-51-profile-census.json
.venv\Scripts\python code\wave16_n3_51_verify.py `
  --output attempts\wave16-n3-51-computation\n3-51-discovery-validation.json
.venv\Scripts\python code\wave16_n3_51_test.py -v
```

The independently audited archive contains seven deterministic formulas and
one complete positive object for its restricted active-local encoding. Its
bounded solver outcomes remain `1 SAT_CANDIDATE`, `5 TIMEOUT_UNKNOWN`, and
`1 UNSAT_UNVERIFIED`, plus a separately preserved historical
`BUDGET_UNKNOWN`. The encoding omits inactive structure, complete fixed
support, `H`, and the global SRG equations. It is not the proof of the
conditional `n3=51` exclusion and supplies no target certificate.
