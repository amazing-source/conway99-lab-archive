# Independent verification

Verification code must be small, deterministic, exact, and independent of the
search implementation where practical. Reports should include commands,
versions, hashes, expected failures on mutated fixtures, and a clear verdict.
This file is a selected orientation index, not a chronologically complete
catalog of every verification artifact; the repository map and dated
subdirectories remain authoritative for omitted waves.

## Baseline validator

`check_srg.py` accepts a strict `srg-edge-list-v1` JSON certificate. It uses
only the Python standard library and validates the graph twice: first with
adjacency-set intersections, then by evaluating the integer adjacency-matrix
identity entry by entry. The parser rejects duplicate object keys, unknown or
case-varied keys, Boolean endpoints, loops, and duplicate undirected edges.

Calibrate it on the 3-by-3 rook graph, an `srg(9,4,1,2)`:

```powershell
python verification/check_srg.py `
  verification/fixtures/rook-3x3.srg.json `
  --vertices 9 --degree 4 --lambda 1 --mu 2
python -m unittest discover -s verification -p "test_*.py" -v
```

The Conway defaults are `(99,14,1,2)`, so a future target certificate needs no
parameter flags.

`Check-Srg.ps1` is a second implementation. It independently parses the JSON
and checks the graph through .NET hash sets under Windows PowerShell 5.1 or
newer:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File verification/Check-Srg.ps1 `
  -Certificate verification/fixtures/rook-3x3.srg.json `
  -Vertices 9 -Degree 4 -AdjacentCommon 1 -NonadjacentCommon 2
```

## Small DRUP checker

`check_drup.py` is an independent, clarity-first checker for textual DRUP
proofs. It checks every addition by reverse unit propagation and requires a
verified empty clause. It is suitable for calibration and auditing encoder/
solver integration. A target-scale nonexistence claim should also use a mature,
pinned proof checker and preferably an LRAT conversion/check.

```powershell
python verification/check_drup.py path/to/instance.cnf path/to/proof.drup
```

## Mature LRAT calibration

The external proof path is calibrated separately with pinned CaDiCaL 3.0.1,
`drat-trim`, and `lrat-check` source commits. Both complete `pair_count=3`
branch-unit CNFs were accepted after DRAT-to-LRAT conversion. Exact versions,
commands, artifact hashes, and the target-scope warning are recorded in
`2026-07-22-lrat-calibration.md`.

This calibration does not make an embedded-solver `UNSAT` result evidentiary.
A target claim still requires retained proofs for a proved complete cover and
independent replay of every artifact.

## Conditional `N3` joint-cover checker

`n3-joint-cover/verify.py` is a standard-library verifier for the strict JSON
certificate describing the 12 matching orbits after canonical `N3`
normalization. It independently enumerates the full rooted scaffold
stabilizer, all 945 compatible matchings, orbit-stabilizer products, a Burnside
checksum, the legacy-fiber diagnostic, and SAT literal numbering.

```powershell
python verification/n3-joint-cover/verify.py
python verification/n3-joint-cover/verify.py `
  verification/n3-joint-cover/n3-joint-cover.json
```

The parser rejects duplicate keys, booleans masquerading as integers, unknown
fields, and non-standard JSON constants. This certificate proves only the
conditional finite branch cover. It neither establishes the upstream `N3`
occurrence theorem nor solves a target branch.

## Conditional refined `N3` checker

`n3-refined-cover/verify.py` independently reconstructs the order-768 parent
stabilizer, its twelve matching orbits, the order-384 oriented subgroup, and
all 78 orbits on the `945 * 11 = 10,395` refined states. It also derives the
forced coordinate profile, rebuilds SAT literal numbering, checks every
orbit-stabilizer product and a Burnside sum of 29,952, and enforces a strict
JSON schema.

```powershell
python verification/n3-refined-cover/verify.py
python verification/n3-refined-cover/verify.py `
  verification/n3-refined-cover/n3-refined-cover.json
```

The checker uses only the Python standard library and does not import search
code. Its `PASS` establishes the conditional symmetry case split only; it is
not a SAT/UNSAT result for any branch.

## `N3` count-bound checker

`n3-count-bound/verify.py` checks the exact arithmetic behind the auxiliary
opposite-edge graph consequence. It exhausts the sub-24 degree-sequence cases,
enumerates every forced local model for the remaining 18-edge case, rebuilds
the twelve branch degree/signature table from the verified joint certificate,
enumerates all 10,395 perfect matchings, and independently derives the
normalized six-vertex boundary profile.

```powershell
python verification/n3-count-bound/verify.py
```

The accompanying human proof establishes why the auxiliary graph has the
properties checked by the script. The resulting `n3 >= 24` is conditional on
the target-specific theorem forcing an `N3`; it is a necessary bound, not a
resolution of Conway-99.

## `N3` side-incidence checkers

`n3-side-incidence/verify.py` checks the Wave 7 active-triangle reduction and
explicitly enumerates the complement-component point patterns forced by
`n3=24` and `n3=27`. `n3-side-incidence/audit_generic.py` is a separate
implementation that generates every clique family, permits unused complement
edges, enforces disjoint intersection resources, and adds singleton fillers.

```powershell
python verification/n3-side-incidence/verify.py
python verification/n3-side-incidence/audit_generic.py
```

Both reproduce support maxima `6`, `9`, and `8`, giving the conditional
necessary bound `n3>=30`. The human proof supplies the upstream graph-theoretic
reduction; neither finite checker is a Conway-99 existence or nonexistence
certificate.

## `N3=30` equality exclusion

`n3-equality/verify.py` checks the exact arithmetic accompanying the Wave 8
classification-free proof: the unique ten-triangle `q=2` equality profile,
the fixed-endpoint count four, the point-size equations, the cubic component
orders, the forbidden internal crossing, and the strengthened global and
branch-local bounds.

```powershell
python verification/n3-equality/verify.py
python -m unittest verification.test_n3_equality -v
```

`n3-equality/audit_exhaustive.py` is an optional slow, solver-free secondary
audit archived verbatim from an independent lane. It generates every
normalized labeled cubic graph on ten vertices, recovers all 21 isomorphism
types, enumerates 674,880 point-clique families, and checks the committed JSON
certificate byte-for-byte. A replay takes about five minutes under the pinned
environment.

```powershell
python verification/n3-equality/audit_exhaustive.py `
  --check verification/n3-equality/n3-30-audit.json
```

The human derivation and adversarial audit establish why these finite
conditions follow from the Wave 6/7 framework. The resulting `n3>=33` is a
conditional necessary bound; it does not resolve Conway-99.

## `N3=33` equality exclusion

`n3-33-equality/verify.py` checks the Wave 9 classification-free proof's
finite steps: both active-`q` profiles, the labeled singleton crossing
obstruction, the point-size equations, the forced local `K5`, every residual
`K6`-minus-matching choice, and the strengthened global and branch bounds.

```powershell
python verification/n3-33-equality/verify.py
python -m unittest verification.test_n3_33_equality -v
```

Two optional standard-library programs give a materially different exhaustive
audit. They enumerate all 266 quartic types on eleven vertices and all 610
admissible point-clique families; the second program independently
canonicalizes the graph types, regenerates the family set with a different
recursion, checks every contradiction witness, and rejects certificate
mutations. The connected catalog is an external House of Graphs/Meringer
input, so it is attributed and hashed rather than redistributed.

```powershell
$wave9Catalog = Join-Path ([System.IO.Path]::GetTempPath()) "11_4_3.g6.gz"
$wave9Certificate = Join-Path ([System.IO.Path]::GetTempPath()) "n3-33-audit.json"
$wave9Replay = Join-Path ([System.IO.Path]::GetTempPath()) "n3-33-replay.json"
Invoke-WebRequest `
  -Uri "https://houseofgraphs.org/data/quartics/11_4_3.g6.gz" `
  -OutFile $wave9Catalog
(Get-FileHash $wave9Catalog -Algorithm SHA256).Hash.ToLower()
python verification/n3-33-equality/audit_exhaustive.py `
  --catalog $wave9Catalog --certificate $wave9Certificate `
  --git-commit 19f27d1ede9cdb0b4110540f52eeb3ad9c94cc94
python verification/n3-33-equality/verify_exhaustive.py `
  --catalog $wave9Catalog --certificate $wave9Certificate `
  --output $wave9Replay
```

The expected compressed catalog hash is
`05ee6bb0c2b40d63d5c44efc8e89ed1c0a381a170d81a3d052749c8edf6b14fd`.
Exact deterministic census digests and the external-source boundary are in
`n3-33-equality/n3-33-census-manifest.json`. The resulting `n3>=36` remains a
conditional necessary bound, not a Conway-99 resolution.

## `N3=36` equality exclusion

`n3-36-equality/verify.py` checks the Wave 10 proof's finite steps: all three
active profiles, singleton forcing, local point types and crossings, the
common-point obstructions, all seventy labeled cubic graphs on six vertices,
the rook-graph parameters, the line-graph-twin endpoint configuration, the
three forced triangle-group pairings, and the strengthened bounds.

```powershell
python verification/n3-36-equality/verify.py
python -m unittest verification.test_n3_36_equality -v
```

The committed support certificate is a separate finite audit of the sole
all-size-two `2K6` branch. The primary program decomposes the degree-two
bipartite supports into two permutation matchings. The independent verifier
constructs the complementary matching recursively and imports no code from
the primary implementation. Both recover exactly 216 masks with SHA-256
`6659fe1972cbacc6980a9792557714730572817b43224b5f1fac24bb0c4ca61a`.
Every abstract mask passes the auxiliary-`H` checks and has eighteen decisive
original-SRG rook-saturation violations.

```powershell
python verification/n3-36-equality/verify_support.py `
  --certificate verification/n3-36-equality/n3-36-support.json
python -m unittest verification.test_n3_36_support -v
```

To regenerate a scratch certificate from the technical commit:

```powershell
$wave10Certificate = Join-Path ([System.IO.Path]::GetTempPath()) "n3-36-support.json"
python verification/n3-36-equality/audit_support.py `
  --certificate $wave10Certificate `
  --git-commit 2194c2b68ebd5c34491d64f15d30f1a3597baa74
python verification/n3-36-equality/verify_support.py `
  --certificate $wave10Certificate
```

The reduction from a putative graph to this finite domain is human-checked and
recorded separately. The census is not a standalone Conway-99 certificate.
The resulting `n3>=39` is a conditional necessary bound, and the target remains
`UNKNOWN`.

## `N3=39` equality exclusion

`n3-39-equality/verify.py` checks the Wave 11 proof's finite steps and exact
semantic witnesses: the four active profiles, singleton forcing, point-size
expansion, all `3^8` rooted size-four petal words, all `2^6` rooted
size-three words, literal forced `K`/`U` edge sets, forbidden point owners,
final parity, and the strengthened global and branch bounds.

```powershell
python verification/n3-39-equality/verify.py
python -m unittest -v verification/test_n3_39_equality.py
```

The committed local replay is a second layer. The primary generator explicitly
constructs canonical point sets, point-clique edges, singleton-forced
complement edges, and owner-intersection witnesses. The independent verifier
imports no primary code, uses integer-coded enumeration and a closed crossing
table, freezes nine stream hashes, and attacks the result with eight mutations.

```powershell
python verification/n3-39-equality/verify_local.py `
  --certificate verification/n3-39-equality/n3-39-local.json
python -m unittest -v verification/test_n3_39_local.py
```

The certificate contains 8,907 records and has combined stream SHA-256
`452850018ad13362694f5bfff2e4beac03288a113a0391c3456a47cd6fbfe9a1`.
Its canonical-LF outer JSON has SHA-256
`4cd23939cfb8ec5080b57fb0626e9579b68250a219ea17876a8e1f4066ad2261`;
the exact detached-clone replay is recorded in
`2026-07-22-wave11-clean-clone.md`.
Its premise stream explicitly binds `K=overline(L)`, 6-regularity, point-clique
membership, linearity, the common-point rule, and the degree-zero-or-two
crossing law. This remains a conditional replay companion to the human proof,
not a standalone Conway-99 nonexistence certificate. The resulting `n3>=42`
is a necessary bound and the target remains `UNKNOWN`.

## `N3=42` equality exclusion

`n3-42-equality/verify_reduction.py` independently checks the proof-side finite
steps: all six active profiles, the degree-three obstruction, both size-four
flower counts, the size-three `t` inequalities, the `(2,3,3)` fixed-point
contradiction, the cubic `K3,3`/open-twin obstruction, and the strengthened
global and branch bounds. Its bound output is guarded by an explicit external
support-exclusion premise.

```powershell
python verification/n3-42-equality/verify_reduction.py
python -m unittest -v verification/test_n3_42_reduction.py
```

The remaining all-size-two branch is checked by a separate proof-producing
support search and a set-based certificate replayer that imports neither the
builder nor the discovery code. The replay requires Meringer's official
`14_3_4.scd` archive, expected SHA-256
`6f3e9cf2b7e0d85c5df59c1638ab9d2fddbfc9905c49b35da01cc892f847e9a0`.
The archive has no stated redistribution license and is intentionally ignored;
download it from the official URL recorded in `REPRODUCING.md`.

```powershell
python verification/n3-42-equality/verify_support_certificate.py `
  --certificate verification/n3-42-equality/n3-42-support-certificate.json `
  --scd verification/n3-42-equality/14_3_4.scd `
  --graph6 attempts/wave12-computation/n3-42-cubic-trianglefree-14.g6 `
  --mutations
```

The certificate has SHA-256
`8115b5f34568a463952afc399bc22db927121f3f1aa28cfc33ae191ea93dc68a`.
The independent catalog bridge checks 110 connected and two disconnected cubic
triangle-free types; four survive the mandatory-degree filter, and all four
support rejection trees replay with zero survivors. The combined adversarial
audit records the conditional strengthening `n3>=45` and
`induced_C6_count>=209331`. It does not resolve Conway-99, and novelty remains
`UNKNOWN`. The detached full-suite replay and byte-identical regeneration are
recorded in `2026-07-22-wave12-clean-clone.md`.

## `N3=45` equality exclusion

`n3-45-equality/verify.py` independently reconstructs the nine active
profiles, mixed order-fourteen reductions, order-fifteen flower census, four
rooted modes, type-`223` parity obstruction, type-`111` saturation
obstruction, and final degree-zero-or-four handshake contradiction. Its
mutation mode attacks the imported premise boundary.

```powershell
python verification/n3-45-equality/verify.py --mutations
python -m unittest -v verification/test_n3_45_audit.py
```

`n3-45-equality-b/audit_semantics.py` is a second semantic reconstruction. It
froze `precomparison-verdict.md` before reading the first audit and then found
no disagreement. Both audits pass only the conditional equality exclusion:

```text
n3 >= 48,
induced_C6_count >= 209334,
Conway-99 = UNKNOWN,
novelty = UNKNOWN.
```

The companion SAT bundle is audited separately. The original bundle retains a
public FAIL report under `2026-07-22-wave13-computation-audit.md`. Its repaired
v2 artifacts pass `n3-45-computation-repair/independent_repair_audit.py` and
six focused regressions:

```powershell
python verification/n3-45-computation-repair/independent_repair_audit.py
python -m unittest discover `
  -s verification/n3-45-computation-repair -p 'test_*.py' -v
```

The repair audit independently reproduces all 17 formula hashes, checks the
1,141,796-clause positive diagnostic, certifies its 18 deliberately omitted
common-point violations, verifies direct artifact provenance, and rejects 31
hostile mutations. The historical 15-test suite now loads the failed baseline
directly from commit `066d9c7fcf593c3b9d35cfef1031dbd9daab4145`, while
the repaired 12-test suite exercises the current files. No negative proof
trace was emitted or checked, so every solver-negative branch remains
`UNSAT_UNVERIFIED`; none is used in the human proof. The detached clean-source
replay at `2026-07-22-wave13-clean-clone.md` records 52 code tests, 12 focused
Wave 13 tests, 104 verification tests, and byte-identical census and positive
diagnostic regeneration.

## `N3=48` frontier reduction

`n3-48-proof/independent_reconstruction.py` independently rebuilds the twelve
active profiles, inherited three-profile filter, order-fourteen and
order-fifteen mixed-profile contradictions, and order-sixteen local-mode
arithmetic. `n3-48-proof/audit_countermodel.py` separately reconstructs the
explicit all-size-two active/local/support object and attacks it with five
semantic mutations.

```powershell
python -B verification/n3-48-proof/independent_reconstruction.py
python -B verification/n3-48-proof/audit_countermodel.py `
  attempts/wave14-proof-a/all2-active-countermodel.json
```

The proof audit passes the scoped reduction to an `r=16`, all-`q=2` residual
with point sizes two or three, eight surviving size-three modes, `H`-degrees
zero or four, and exact twofold support coverage. The positive object shows
that the listed active constraints alone are not contradictory; it is not a
partial or complete Conway graph. Exclusion of `n3=48` remains `UNKNOWN` at
this checkpoint.

The computation lane is audited independently by
`n3-48-computation/independent_audit.py`. It reconstructs all thirteen formula
streams, checks the full positive candidate and two weakened controls, binds
file and semantic provenance, and rejects 29 hostile mutations.

```powershell
python -B verification/n3-48-computation/independent_audit.py
python -B code/wave14_n3_48_test.py -v
```

The archived JSON output is deterministic under replay. The scan status is
`1 SAT_CANDIDATE`, `7 UNSAT_UNVERIFIED`, `1 BUDGET_UNKNOWN`, and
`2 TIMEOUT_UNKNOWN`; negative solver exits are explicitly non-evidentiary.
The literature/status audit also keeps the target and novelty `UNKNOWN`.
The detached clean-source replay, four byte-identical regenerations, and the
pre-release timestamp-determinism repair are recorded in
`2026-07-23-wave14-clean-clone.md`.

## `N3=48` global exclusion

Wave 15 brings the full SRG equations back into the Wave 14 residual. The
active original-vertex set has order at most 24 and induced minimum degree at
least six. The target spectrum gives

```text
2e(X) <= 3|X| + |X|^2/9,
```

so minimum degree six forces `|X|>=27`, a contradiction. An independent
outside-degree second-moment argument reaches the same obstruction.

```powershell
python -B attempts/wave15-global-lift/verify_subset_moment_certificate.py `
  attempts/wave15-global-lift/subset-moment-certificate.json
python -B -m unittest -v `
  attempts/wave15-global-lift/test_subset_moment.py
python -B verification/n3-48-global-lift/independent_check.py

$wave15Python = (Resolve-Path '.venv\Scripts\python.exe').Path
Push-Location verification/n3-48-global-lift
& $wave15Python -B -m unittest -v test_independent_check.py
Pop-Location

python -B attempts/wave15-algebraic/exact_checks.py `
  --output attempts/wave15-algebraic/exact-checks.json
python -B verification/n3-48-algebraic/independent_check.py `
  --artifact attempts/wave15-algebraic/exact-checks.json
python -B -m unittest -v `
  verification/n3-48-algebraic/test_independent_check.py
```

The two discovery lanes and their separate adversarial audits pass 5, 11,
and 7 focused tests. The global certificate and independent regeneration are
byte-identical canonical-LF files. The first CRLF/public-LF mismatch is kept
at baseline commit `522260a` and repaired at `874af27`; the algebraic lane's
ambiguous weighted-moment key is also preserved and re-audited. The verified
conditional consequence is

```text
n3 >= 51,
induced_C6_count >= 209337,
Conway-99 = UNKNOWN,
novelty = UNKNOWN.
```

The detached clean-source replay at
`2026-07-23-wave15-clean-clone.md` records the full historical suites, all 23
focused Wave 15 tests, all 18 frozen file hashes, byte-identical canonical-LF
certificate regeneration, clean detached status, and `git fsck`.

## `N3=51` equality exclusion and active-local archive

Wave 16 independently verifies a shorter global obstruction. Sixteen raw
`sum q=34` profiles reduce to four. Their indexed active original-vertex set
has order at most 25, while exact size-two endpoint crossings and distinct
triangle neighbors force induced minimum degree at least six. The target
spectrum requires order at least 27.

```powershell
python -B attempts/wave16-n3-51-structural/exact_check.py `
  --verify attempts/wave16-n3-51-structural/exact-checks.json
python -B verification/n3-51-structural/independent_check.py
$wave16Python = (Resolve-Path '.venv\Scripts\python.exe').Path
Push-Location verification/n3-51-structural
& $wave16Python -B -m unittest -v test_independent_check.py
Pop-Location
```

The 24-test adversarial suite verifies the endpoint-local scope and contains
countercontrols against a global `H`-degree law, a point-size cap, the old
support-graph identity, reused support indices, and weakened spectral inputs.
It also pins the final Wave 15 public hash while preserving two transient
historical hashes. The verified conditional consequence is

```text
n3 >= 54,
induced_C6_count >= 209340,
Conway-99 = UNKNOWN,
novelty = UNKNOWN.
```

The computational lane is deliberately separate:

```powershell
python -B verification/n3-51-computation/independent_check.py `
  --output verification/n3-51-computation/independent-audit.json
python -B verification/n3-51-computation/test_independent_check.py -v
python -B code/wave16_n3_51_test.py -v
```

It independently rebuilds seven exact DIMACS streams, validates one positive
active-local relaxation candidate, rejects 38 hostile mutations, and passes
4 independent plus 8 submitted tests. Its final bounded status remains
`1 SAT_CANDIDATE / 5 TIMEOUT_UNKNOWN / 1 UNSAT_UNVERIFIED`, with one earlier
`BUDGET_UNKNOWN` retained separately. No solver-negative outcome is used as
mathematical evidence.

The independent literature/status audit is
`2026-07-23-wave16-status-audit.md`. It checks the exact source pages behind
`induced_C6_count=209286+n3`, current target-specific sources, exact-number
searches, corrections, citations, and the June 2026 Shpectorov lecture scope.
It found no target resolution or exact prior Wave 16 bound through 2026-07-23,
but correctly leaves both target status and novelty `UNKNOWN`.

The detached release replay is `2026-07-23-wave16-clean-clone.md`. It records
252 passing tests, six semantic checker entry points, five byte-identical
regenerations, all seven Wave 16 status hashes, every ledger evidence path,
public-hygiene scans, clean detached status, and `git fsck`.

## Wave 27 endpoint lattice and orthogonal-root audits

The Wave 27 verification package has three deliberately separated
mathematical layers.

First, the
[A2-summand-free construction audit](wave27-a2free-construction/2026-07-24T001657Z-audit.md)
independently reconstructs the abstract coupled package

```text
S=E8^4 orthogonal_sum E6^2
```

and passes 16 independent tests plus the submitted 15-test replay. Complete
root enumeration proves that `S` has no orthogonal `A2` direct summand.
Embedded `A2` root subsystems do occur inside its `E6` blocks; the audit
explicitly preserves that distinction. The verified object is still only a
candidate for the arithmetic/lattice relaxation, with no frame, projector,
Schur-square, or graph origin. The submitted account is the
[construction report](../agents/2026-07-23-wave27-a2free-construction.md).

Second, the
[unrestricted E6 trace audit](wave27-h9-classification/2026-07-24T002029Z-audit.md)
proves

```text
E6 Q=I (mod 2), Q symmetric even integral positive definite
  implies tr(E6 Q)>=14,
```

with equality attained by the displayed `Q6`. Its independent suite passes
21 tests and its submitted suite passes 16. The report retains one nonfatal
exposition correction, the missing parity bridge
`tr(C^2)=tr(C) (mod 2)`. This algebraic trace floor is not the later
projector-frame cubic floor: the trace-14 block is a valid hostile control for
the weaker algebraic problem. See the
[trace report](../agents/2026-07-23-wave27-h9-classification.md).

Third, the
[general-root tensor audit](wave27-general-root-tensor/2026-07-24T010548Z-audit.md)
uses an independent affine-CVP enumerator to verify cubic-energy floors 24
for an orthogonal `E6` summand and 66 for an orthogonal `A6` summand. The
`E6` floor contradicts its complement-imposed compression cap 22; the `A6`
floor exceeds the global trace 60. Arbitrary cross-block `Q` entries are
allowed, but every conclusion requires an orthogonal integral summand.

The frozen [core tensor report](../agents/2026-07-23-wave27-general-root-tensor.md)
leaves exactly `A20 orthogonal_sum E8^3` at `h=21` among 17 full rank-44 ADE
decompositions. A later, separately frozen
[A20 addendum](../agents/2026-07-24-wave27-a20-trace-addendum.md) proves a
local trace floor 42; the rank-24 complement raises the total floor to 66 and
excludes that core survivor. The audit verifies the core and addendum
separately, passing 23 independent, 17 submitted-core, and 8
submitted-addendum tests with byte-identical regenerations.

The combined conclusion is conditional on `n3=708`, the full projector/Schur
endpoint identities, and the additional hypothesis that the scaled-dual form
is a full orthogonal sum of irreducible ADE root lattices:

```text
full orthogonal ADE rank-44 endpoint form: impossible
general even rank-44 scaled-dual form: UNKNOWN
n3=708 / Conway-99 / novelty: UNKNOWN
```

## Wave 36 conditional endpoint necessities

- `wave36-modular-reflection/` independently reconstructs the reciprocal
  Smith form, parity and modular-rank restrictions, and the
  characteristic-seven symmetric-cube argument. Its 11 independent tests
  and the submitted 11 tests pass.
- `wave36-ternary-polar-bound/` independently reconstructs both determinant
  classes of the ternary orthogonality graph, including the degenerate
  nonadjacent-span count, and verifies the exact mixing inequalities. Its 12
  independent tests and the submitted 10 tests pass.
- `wave36-block-compatibility/` independently derives all three block
  equations, censuses, component patterns, characteristic transfer,
  connectivity, triangle count, and four-cycle identity. Its 12 independent
  tests and the submitted 10 tests pass.

Together these are 66 passing mathematical tests. They verify only their
conditional scopes: no endpoint graph, contradiction, checked UNSAT proof,
or upper bound below 4158 is promoted.

The fresh
[Wave 36 integration audit](2026-07-26-wave36-integration-audit.md) checks
all six suites and exact regenerations, hashes, evidence paths, local links,
privacy patterns, and status walls. The
[orchestrator decision](2026-07-26-wave36-orchestrator.md) records the
promoted scope, Evans prior-art attribution, and deliberate exclusion of the
still-active rooted SAT scout.

## Wave 37 artifact and structural verification

- `wave37-rooted-branches/` reconstructs the fixed-triangle prism lemma,
  endpoint units, exact parent/refined scope, and all five deterministic
  clause catalogs without importing the discovery implementation. The
  branch-4 `BUDGET_UNKNOWN` record is explicitly assigned no mathematical
  evidentiary value.
- `wave37-polar-strengthen/` independently derives the ternary
  self-orthogonal code consequences, Schur-square rank ceilings, corrected
  signed-degenerate-triple count, oriented ternary controls, and both
  characteristic-seven rank-eleven association schemes. It includes an
  explicit hostile counterexample to the refuted collinearity inference.
- `wave37-proof-producing-endpoint/` independently reconstructs every
  branch-15 OPB constraint byte-for-byte, verifies the metadata and
  deterministic gzip round trip, and records parser acceptance by the pinned
  Exact binary. Its promotion is formula-artifact-only.

The verified scope is deliberately narrow:

```text
fixed-triangle P=0 clause catalogs: VERIFIED scoped
ternary/code/degenerate-space restrictions: VERIFIED scoped
branch-15 OPB bytes and semantics: VERIFIED artifact-only
branch-15 satisfiability: UNKNOWN
other 32 endpoint cases: not represented by that OPB
upper bound below 4158: NOT PROVED
Conway-99: UNKNOWN
```

## Wave 38 queue, complete-prism, and modular verification

The [integration audit](2026-07-27-wave38-integration-audit.md) and
[orchestrator decision](2026-07-27-wave38-orchestrator.md) record the final
promotion boundary.

- `wave38-solver-harvest/` independently reconstructs all 33 endpoint cases,
  orbit weights, and 231 collision-free planned paths. It verifies only the
  queue and null harvest: no output, proof, assignment, or case result exists.
- `wave38-complete-endpoint/` independently reconstructs the 96,215 potential
  triangles, exact residual-only count `60*C(84,6)=24,388,892,640`, all 64
  prism supergraphs under `lambda=1`, the 33-case cover, and the decoded
  oracle on all 32,768 six-vertex graphs. Candidate completeness, pool
  provenance, strict integer schemas, and output containment were hardened
  after the first audit; the final re-audit verifies all five repairs and
  both package manifests.
- `wave38-coclique-rank/` independently proves the 13-coclique, derives
  `N M N^T=27I-9A+J`, and verifies `rank_F7(M)>=13`. With endpoint parity,
  `r3=12` forces even `r7>=14`, leaving 528 arithmetic rank pairs.
- `wave38-higher-order/` independently verifies the signed fourth-order
  imbalance, ternary centering and local-rank bridge, the frozen rank-ten
  control, and the individual-column census. The rank-six statement is for
  the centered Gram; the uncentered seven-row Gram has rank seven.

```text
endpoint proof coverage:        0 / 33
complete all-prism mathematics: VERIFIED construction scope
rank_F7(M)>=13:                 VERIFIED
higher-order bridge:            VERIFIED scoped, wording qualified
upper bound below 4158:         NOT PROVED
n3=4158 / Conway-99:            UNKNOWN
```

## Wave 34 exact encoding and actual-incidence continuation

Wave 34 has separated Stage 1, candidate, Stage 2, and crosscheck packages.

The rooted structural verifier binds the candidate coordinates to the exact
Wave 33 labeling, proves `SNF(P)=diag(1^13,0)`, reconciles the projector
splits, checks the integral rank-16 formulation in both directions, and
independently reproduces the `574,118,037` Pb-only column census. The
pair-census crosscheck derives the nine O-pair states directly and uses
weighted permanents to reproduce the stricter `448,879,368`
duplicate-free necessary-column count.

The rooted encoding verifier independently regenerates all 4,323,943 clauses
of the 1,233,001-variable complete-domain CNF and matches the raw
89,546,779-byte stream. This is encoding verification only. No SAT model,
UNSAT proof, or target graph exists in the package.

The rootless verifier reconstructs the fibre holonomy,
`deg(R2)=3q`, `deg(R3)=12-q`, `|E(R3)|=1150`, the 383-triangle upper cap,
mixed-trace normalization, and the partial control. The separate Stage 1
derivation records at least 6,860 R0-centered wedges, 3,041 four-cycles, and
`tr(A_R3^4)>=67848`. It does not force the forbidden motif.

The consolidated external-source package imports no graph-level theorem:
Kuber's Lean theorem is conditional without the graph bridge; Harrison's
formula identities replay but the theorem proof bodies are missing or
unpulled; Selub supplies historical SAT-framework prior art without a solver
certificate.

Run the 149 current-tree outer tests, the authenticated 11-test structural
chronology replay, the separate source validator, and the eight chronology
protocol tests with the commands in [`REPRODUCING.md`](../REPRODUCING.md).
The 16 publication manifests contain 130 entries. Exact corrections and
nonpromotion walls are in the
[Wave 34 orchestrator ledger](2026-07-24-wave34-orchestrator-corrections.md).
The exact public detached replay is in the
[Wave 34 clean-clone audit](2026-07-24-wave34-clean-clone.md).

```text
rooted structural/encoding facts: VERIFIED scoped
rooted formula SAT/UNSAT:          UNKNOWN
rootless local/global bounds:      VERIFIED or DERIVED scoped
rootless motif forcing/avoidance:  UNKNOWN
n3=708 / Conway-99 / novelty:      UNKNOWN
```

## Wave 35 prism-free upper-endpoint verification

The
[independent spectral audit](wave35-n3-upper-spectral/audit.md)
reconstructs the conditional `n3=4158` signed-projector polynomial, Smith
form, reflection identity, all forty mixed-Schur values, compression and
incidence-scalar calculations, and the 45-principal-minor criterion without
importing discovery-side code or JSON.

Its verdict is `VERIFIED_SCOPED_WITH_WORDING_QUALIFIER`. The support-degree
criterion is `sum_j |S_ij|<=3`, not an absolute algebraic row-sum condition,
and the nonadjacent 7-by-7 object is only a relaxed witness. Ten independent
tests pass and all fourteen submitted tests replay.

```text
conditional spectral and Smith identities: VERIFIED scoped
endpoint matrix or 45-set:                  NOT CONSTRUCTED
upper bound below 4158:                     NOT PROVED
n3=4158 / Conway-99:                        UNKNOWN
```

The combinatorial and construction packages are indexed in `agents/` and
`attempts/`; their focused discovery tests pass, but a separate independent
promotion package has not yet been completed.

## Wave 29 single-lattice endpoint exclusion

The
[Wave 29 independent audit](wave29-s0-frame-exclusion/audit.md) reconstructs
the exact exclusion of only

```text
S0=K12 orthogonal_sum LAMBDA(F)
```

from the frozen full endpoint package. Minimum-four support gives 63 and 168
frame rows in the two blocks. Determinant allocation, the rank-12
even-unimodular veto, row-alphabet trace residues, and exact AM--GM force

```text
det(B_K)=3645,
tr(B_K)=24,
tr(C_K)=6.
```

`C_K` is integral and self-adjoint but is not assumed positive semidefinite.
The verifier checks the logarithmic inequality separately on
`(-1/2,0)` and `(0,infinity)`. Characteristic-pseudodeterminant integrality
then gives `det(B_K)<=729`, contradicting 3645.

The discovery and independent suites pass 18 and 27 tests, respectively.
Both results regenerate byte-identically, and all 14 mathematical manifest
entries validate. The verifier retains stale preinspection commit metadata,
the rejected PSD shortcut, exact determinant rounding, and active
premise-deletion controls.

The proof-separated
[literature audit](wave29-s0-literature-audit/audit.md) logs 81 query strings
in 21 batches, retains 16 primary or authoritative metadata records, and
finds standard ingredients but no exact combined prior result. One Crossref
query was rate-limited, and three major bibliographic services were not
comprehensively machine-audited. Novelty remains `UNKNOWN`.

The [correction ledger](2026-07-24-wave29-orchestrator-corrections.md)
records mathematical acceptance, wording and metadata corrections,
publication-byte normalization, source limits, and the exact scope wall:

```text
S0 full endpoint origin: REFUTED (VERIFIED)
every other h=729 lattice: UNKNOWN
n3=708 / Conway-99 / novelty: UNKNOWN
```

The detached
[clean-clone replay](2026-07-24-wave29-clean-clone.md) passes all 45 tests,
two byte-identical regenerations, three manifests with 19 entries, central
metadata, all-repository local links, exact-blob privacy scans, clean status,
and strict Git object verification at integration commit
`ae8fd70baaeb35302f957653e20ad710e5e77281`.

Glued, non-root, and otherwise nonorthogonal general lattices are not
classified or excluded. The headline conditional bound therefore remains
`n3>=708`.

## Wave 30 decomposable `h=729` reduction and bare construction

The original
[general verifier audit](wave30-general-h729/audit.md) independently
reconstructs the conditional mathematics but records a submitted replay
failure. Discovery commit `091d0a4...` froze a transient Wave 29 audit hash,
so its submitted suite ran zero tests and its generator stopped before
output. Verifier-veto commit `0bc6dc9...` preserves `V30-GEN-001` and blocks
publication of that exact revision.

The provenance-only repair at `a7be6b8...` substitutes the applicable
committed hash and regenerates dependent result and checksum metadata. Its
test source, failed routes, mathematics, surviving type, and limitations are
unchanged. The
[fresh re-verification audit](wave30-general-h729/reverification-audit.md):

- freezes the exact repaired Git object;
- passes the repaired submitted suite `20/20`;
- reproduces its JSON byte for byte;
- reproduces the original zero-test/generator failure;
- passes the unchanged historical independent verifier `32/32` in the
  veto-commit snapshot; and
- reproduces the historical independent JSON byte for byte.

The repaired revision receives
`PASS_SCOPED_CONDITIONAL_THEOREM`; the original revision remains `FAIL`.
Within the full frozen `n3=708` endpoint hypotheses, fourteen of fifteen
aggregate types for a rootless, integrally orthogonally decomposable
rank-44 determinant-729 form are excluded. The unique surviving necessary
type has

```text
block ranks:       20,24
block det(S):      729,1
frame rows:        105,126
block det(Q):      5,1
block det(B):      3645,1
block tr(B):       36,24
B_U:               I24.
```

The local rank-20 block label is not the ADE root lattice `A_20` and is not
proved isometric to the construction below. The 62 surviving row-count
profiles are necessary arithmetic only.

The independent
[construction audit](wave30-h729-construction/audit.md) verifies five exact
2-neighbor steps from `K12 orthogonal_sum E8`, the complete root-count chain
`240 -> 112 -> 48 -> 20 -> 6 -> 0`, and a rootless rank-20 determinant-729
lattice `T20` with minimum four, exact level three, and exactly 5076
norm-four vectors. It also verifies the literal bare direct sum

```text
S44=T20 orthogonal_sum LAMBDA24,
G44=21*S44^(-1),
S44*G44=21*I44.
```

The construction discovery suite passes 16 tests and the independent
verifier passes 24 hostile tests. Both JSON results regenerate
byte-identically. No `Q`, compatible `B`, 105/126 frame, `X`, `M`, `W`,
Schur identity, endpoint, or graph is supplied.

The proof-separated
[literature audit](wave30-literature-audit/audit.md) freezes both exact
signatures, logs 96 query strings in 24 batches, and retains 21 structured
metadata records with no raw source payload. It finds no exact match in the
searched sources, records one Crossref HTTP 429 and incomplete bibliographic
coverage, and leaves novelty, priority, and global status `UNKNOWN`.

The
[orchestrator correction ledger](2026-07-24-wave30-orchestrator-corrections.md)
retains the original veto, repair, fresh verdict, verifier self-corrections,
construction packaging correction, discarded wrapper failures, source
limits, and publication wall:

```text
rootless integrally decomposable h=729 classification: VERIFIED
bare T20 and rank-44 S/G construction:                 VERIFIED
surviving 20+24 type / rooted / indecomposable:        UNKNOWN
h=729 row / n3=708 / Conway-99 / novelty:              UNKNOWN
```

The detached
[Wave 30 clean-clone replay](2026-07-24-wave30-clean-clone.md) freezes
integration commit `0a31b62...` in a no-local, no-hardlink clone. It passes
60 tests in the repaired integration tree and 32 tests in the separately
extracted historical verifier snapshot, reproduces the original expected
zero-test/generator failure, regenerates four accepted JSON files byte for
byte, validates six manifests with 47 entries, and passes central-ledger,
link, exact-blob privacy, clean-status, and strict Git-object gates. Its scope
is reproducibility and publication hygiene for the conditional decomposable
reduction and bare `T20` construction only.

## Wave 31 sign-commutant obstruction and T20 finite boundary

The [primary sign-commutant audit](wave31-sign-commutant/audit.md) freezes
discovery commit `a8b0c34040f6857b3c5ebcc44f108e03a4159088` and independently
reconstructs the complete conditional proof. Under actual target
vertex-triangle incidence, a rootless integral orthogonal split induces a
nonempty proper triangle-coordinate projector block. Its diagonal sign
commutes with the zero-projector; transport by the incidence matrix produces
a symmetric graph operator commuting with the exact `-4` projector.

The full local commutator expansion gives constant signed vertex incidence.
The signed triangle double count forces `33 | b`, while the independent
projector-block trace argument forces `21 | b`. Hence `231 | b`, impossible
for a proper block. The primary verdict is `PASS_SCOPED`: 21 independent
tests pass, the submitted 15-test suite passes, and the submitted JSON
regenerates byte-identically.

The separate
[skeptical audit](wave31-sign-commutant-skeptic/audit.md) returns
`PASS_NO_FATAL_GAP`. It independently checks the contragredient unimodular
basis change, one-block row support, incidence eigenspace transport,
projector normalization, every local summand and sign, multiblock and
complement cases, both divisibility routes, and exact hostile controls.
It corroborates rather than replaces the designated verifier.

The resulting conditional status is:

```text
rootless integrally decomposable actual-incidence endpoint: impossible
Wave 30 20+24 survivor under those premises:                impossible
rooted endpoint forms:                                      UNKNOWN
rootless integrally indecomposable endpoint forms:          UNKNOWN
n3=708 / Conway-99 / novelty:                               UNKNOWN
```

The independent
[T20 finite-evidence audit](wave31-t20-frame/audit.md) freezes construction
commit `67a0e4585c9c378dcd658784a3876564557b70e3`. Its separate
implementation enumerates the complete norm-four shell in two exact bases,
matches all 2,538 ordered antipodal lines, scans all 3,219,453 unordered
pairs, recomputes separate coefficient and augmented GF(2) ranks, verifies
all rational weights and 210 moments, and exhausts the named radius-one/two
domain with a collision-free base-257 encoding. The discovery and verifier
suites pass 10 and 11 tests.

Its verdict is `PASS_SCOPED_FINITE_EVIDENCE`. It verifies the exact
5,076-vector shell, pair geometry, 243-support rational box witness,
cap-one-coordinate exclusion, named radius-two nonhit, and conditional
84-unit `A4` transfer. It does not find or exclude an unrestricted Boolean
or oriented frame. The sign-commutant theorem independently supersedes this
as a rootless decomposable endpoint construction route without changing the
finite result.

The proof-separated
[literature audit](wave31-literature-audit/audit.md) preserves its
pre-verification chronology, logs 80 exact queries in 20 batches, makes four
direct metadata/abstract open attempts, retains 14 metadata records and no
raw source payload, and finds no exact prior result in searched sources.
That is not a novelty or openness certificate.

The
[Wave 31 correction ledger](2026-07-24-wave31-orchestrator-corrections.md)
records the primary-verifier wording correction, discarded wrong-directory
zero-test invocations, secondary-checker status, construction embedded-parent
hash, runtime-field portability caveat, literature chronology, logical
supersession, and unchanged global wall.

Six Wave 31 manifests contain 42 entries:

| package | entries | manifest SHA-256 |
|---|---:|---|
| sign proof discovery | 7 | `c1d3b8d2a2ca25c4dcdb20fbc1d974f1561fa7c110524359443161d79bebd7f6` |
| literature audit | 6 | `ccbc52b0089484b153251fe4c37759d49618c59a78e449c61dde122e64465d25` |
| T20 finite discovery | 8 | `972640b51dd31dc6037ae26b676d1f7c39626f25d038606a71bf18728e9ea3d4` |
| primary sign verifier | 8 | `e91d4ec72d7921688700bdc5e68b1e610db1d031b1ec7ffae9b927ecd4494122` |
| skeptical sign verifier | 5 | `c9dd19b9df24e22bcfff7533bb0251582c737153dbbe9ad28e8ea23f2085c1c0` |
| T20 finite verifier | 8 | `73072c577eff876b4799455a6e0ea0080e54f5370ed8790eda6b85fe3687e1bb` |

The detached
[Wave 31 clean-clone replay](2026-07-24-wave31-clean-clone.md) freezes
integration commit `f591e75...`. It passes 57 unit tests and the skeptical
checker, regenerates five accepted outputs, validates all 42 manifest
entries, checks the complete central ledgers and links, scans exact release
and new-blob bytes with zero privacy findings, and finishes with clean
detached status and strict Git-object integrity.

## Wave 32 rooted and indecomposable endpoint reductions

The corrected
[rooted discovery package](../attempts/wave32-rooted-vector/) proves a
necessary reduction under the full actual vertex-triangle incidence and
frozen `n3=708` endpoint package. Every norm-two root has triangle image

```text
(+1)^21,0^189,(-1)^21
```

transported from a signed seven-plus-seven vertex support whose induced
graph is, up to relabeling, the bipartite complement of the Fano incidence
graph. This reduces
the earlier `46 -> 32` root census to 16 matrix-only patterns and one
actual-incidence pattern. The package does not exclude that last pattern.

The [clean-room rooted audit](wave32-rooted-vector/audit.md) returns a scoped
`VERIFIED` verdict after 19 independent tests. It does not import or execute
discovery code. It reconstructs the primitive-image bridge, incidence
transport, residue elimination, support saturation, outside census, tensor
and fourth-moment constraints, reflection consequences, and hostile premise
deletions. It also preserves and repairs the discovery-v1 residual-degree
error; the corrected remaining degrees are `10,12,14`.

The separate
[indecomposable discovery package](../attempts/wave32-indecomposable/)
proves two necessary rootless reductions. Under minimum four, primitive row
generation makes integral indecomposability equivalent to connected
nonorthogonality support; the Wave 31 actual-incidence theorem supplies that
connectedness. Rootlessness also forbids the unique switched
`{-2,-2,-1}` three-row norm-two motif and forces

```text
tr(A_-1 A_-2^2)=0.
```

The [clean-room indecomposable audit](wave32-indecomposable/audit.md)
returns `PASS_SCOPED_WITH_NONBLOCKING_COVERAGE_GAPS` after 19 tests. It
independently supplies the checks omitted by the candidate suite, verifies
the exact pair census and factor-two trace normalization, and builds
full-size hostile controls. Neither pair counts nor those controls force the
motif under actual incidence.

The corrected [literature package](wave32-literature-audit/audit.md) and
[independent literature audit](wave32-literature-audit-independent/audit.md)
preserve 68 exact queries in 17 batches, eight direct inspections, 15
metadata records with explicit 14-plus-one chronology, three access
failures, and no raw source payload. The independent suite passes 17 tests
and records Petro--Phillips's conditional triangle spectrum as prior art.
No exact endpoint resolution was found in the searched sources; novelty,
priority, openness, and the global target status remain `UNKNOWN`.

Run the five suites from the repository root:

```powershell
python -B -m unittest discover -s attempts\wave32-rooted-vector -p test_exact_check.py -v
python -B -m unittest discover -s verification\wave32-rooted-vector -p test_independent_check.py -v
python -B -m unittest discover -s attempts\wave32-indecomposable -p test_exact_check.py -v
python -B -m unittest discover -s verification\wave32-indecomposable -p test_independent_check.py -v
python -B -m unittest discover -s verification\wave32-literature-audit-independent -p test_independent_check.py -v
```

The exact test breakdown is `14 + 19 + 10 + 19 + 17 = 79`. Five
deterministic JSON outputs regenerate byte-identically. Six Wave 32
manifests contain 42 entries:

| package | entries | manifest SHA-256 |
|---|---:|---|
| rooted discovery | 8 | `ba6c7099e06e24fe2feee4d19021dac9ddf49cbfe99acdd54f905a6c40728b8e` |
| rooted verifier | 7 | `2607c3000944e6d31ab5491a7d959ae4f97f05ac3e0d754baaf2830efcd085df` |
| indecomposable discovery | 7 | `451ca652a83b3a93fd11278c25dafe43bafabc3e06e1cac429064d32211d7138` |
| indecomposable verifier | 8 | `67dd65dd491ef28b4848bbb6c1e0ae47d3814db5b0a466462d7e9f79d5d4d6cd` |
| literature package | 6 | `9bdf458203beb32c76b993af2cb6130641546b5a7816f8bed507661e640173c6` |
| literature verifier | 6 | `b333f77785db6495040e5137b8cc8c9c70f283ed5dfac513ff92f98fd15f6b24` |

The
[Wave 32 orchestrator correction ledger](2026-07-24-wave32-orchestrator-corrections.md)
retains every discovery defect, verifier objection, repair, scope wall, and
the unchanged global `UNKNOWN` status.

The detached
[Wave 32 clean-clone replay](2026-07-24-wave32-clean-clone.md) freezes
integration commit `ad6329f...`. It passes all 79 tests, regenerates five
accepted outputs, validates all 42 manifest entries, checks the complete
central ledgers and links, scans exact release and new-blob bytes with zero
privacy findings, and finishes with clean detached status and strict
Git-object integrity.

## Wave 33 finite rooted extension and rootless contraction wall

The [rooted extension audit](wave33-rooted-extension/comparison-audit.md)
independently verifies the conditional `14+70+15` equitable partition, the
simple `2-(15,3,2)` O-Q design, all six blocks of the exact strongly regular
graph-extension equation, and the forced induced-O spectrum. The criterion
is necessary and sufficient for a graph extension only; it does not certify
the remaining projector, lattice, tensor, or Schur endpoint conditions.
The precomparison and comparison suites pass `18+15=33` tests. No binary
solution and no complete infeasibility certificate is supplied.

The separate
[rooted construction audit](wave33-rooted-construction/audit.md) verifies
one hostile O-Q design, its ten exact `FB=2J` defects, and the precise scope
of a bounded search over all `70!` assignments of that one fixed design.
The package supplies no O-O layer. Its 25-second SciPy/HiGHS timeout has no
primal and carries no positive or negative evidence. The original local
frozen-context verifier recorded 37/37 and regenerated the hostile
certificate byte-identically. Chronology v2 replays 36 unchanged verifier
cases and separately passes the portable source half of the sole omitted
composite test. The
[chronology audit](wave33-rooted-construction-chronology/audit.md) preserves
every original byte, authenticates all eight historical inputs, and replays
the unchanged `14+36=50` portable construction cases in an isolated
temporary root. Its 20 outer hostile chronology tests pass. The portable
source half of the sole omitted composite verifier test passes separately.
The solver-environment half, which depends on ignored local files, is
`NOT_REPLAYED_NONBLOCKING`; v2 opens zero such files and observes zero
environment hashes. The unchanged comparison CLI is `NOT_RUN_BY_DESIGN`.
Direct live-root replay is expected to reject the later integrated
`STRUCTURE.md` byte.

The [rootless motif audit](wave33-rootless-motif/audit.md) returns
`PASS_SCOPED_WITH_NONBLOCKING_WORDING_QUALIFIER` after `21+27=48`
independent tests. At a formally allowed `q(T)=q(U)=2` `R2` pair, every
bilinear `Q[Gamma]` contraction and every `N^T p(A) N` contraction is blind
to the displayed null trade. The two formal nonnegative integral tables
have zero versus one common `R3` triangle. This does not establish global
realizability, occurrence, forcing, or avoidance, and it must not be
generalized to an unqualified statement about all two-leg contractions.
The exact actual-incidence board has four pair-indexed transversal
candidates, hence `4*708=2832` candidates with multiplicity rather than
2,832 distinct realized triangles.

Run the four live-input packages and the construction chronology package
from the integrated repository root:

```powershell
python -B -m unittest discover -s attempts\wave33-rooted-extension -p test_*.py -v
python -B -m unittest discover -s attempts\wave33-rootless-motif -p test_*.py -v
python -B -m unittest discover -s verification\wave33-rooted-extension -p test_*.py -v
python -B -m unittest discover -s verification\wave33-rootless-motif -p test_*.py -v
python -B -m unittest discover -s verification\wave33-rooted-construction-chronology -p "test_*.py" -v
```

The five commands report `15+14+33+48+20=130` outer tests. The chronology
suite performs one embedded `14+36=50` replay and separately passes the
portable source-provenance half of the sole omitted composite test. The
original historical package accounting remains
`15+14+14+33+48+37=161`; the v2 clean-clone-independent procedure reproduces
160 of those cases. The 20 chronology tests and embedded 50 original cases
are separate evidence layers.

The seven original artifact manifests contain 73 entries. The chronology
repair adds a seven-entry eighth manifest, for 80 entries in all:

| package | entries | manifest SHA-256 |
|---|---:|---|
| rooted discovery | 8 | `153860d39fe7274a2f55ee952bcad1135cf4134ccc36d9aec07f6da379c5ca04` |
| rootless discovery | 8 | `384081a967153059399b4e0724e901ef28183cedab8d7e253e45af560e16df95` |
| rooted construction discovery | 16 | `0cd192c0182506b3c901806cc96abb9fe53f04dc906b0b5cd73bc9b602558ff4` |
| rooted precomparison verifier | 8 | `a0cd7d284a23aba5576f2da2a1282c9acb209953c3da5d01e706d793f61d3ea7` |
| rooted comparison verifier | 6 | `50571e1870b7fafb245e2eaf79f8331a3b5d6c7cbd282a8bd2d8937b44898f76` |
| rootless verifier | 13 | `e51811d3dd5a35d21a1e6c7f88625b9dfdabdd1097de1898f988b40747e82822` |
| rooted construction verifier | 14 | `20c27560bdf9720cd1cf043b11c218130cd2891a2d3c874f9dbc9bce2f27fbbf` |
| rooted construction chronology | 7 | `22cbb94ad5a452e9e9c3f38ac35bb31f0b5d2cf81446d0aab5827c3d30b84f69` |

The
[Wave 33 orchestrator correction ledger](2026-07-24-wave33-orchestrator-corrections.md)
retains the discovery-report manifest typo, the construction replay
argument mistake, every verifier objection and checker gap, the mandatory
rootless wording qualifier, and the unchanged publication wall:

```text
rooted graph criterion:                  VERIFIED scoped
binary rooted solution or exclusion:    UNKNOWN
rootless fused-algebra/local reduction:  VERIFIED scoped
global mixed-motif forcing or avoidance: UNKNOWN
rooted/rootless endpoints:               UNKNOWN
n3=708 / Conway-99 / novelty:            UNKNOWN
```

The
[Wave 33 detached clean-clone replay](2026-07-24-wave33-clean-clone.md)
checks exact integration commit `66790bc` with 130 passing outer tests, eight
byte-identical external regenerations, eight manifests with 80 entries,
central-ledger/link/privacy gates, clean status, and strict Git object
verification.

The
[Wave 27 correction ledger](2026-07-24-wave27-orchestrator-corrections.md)
preserves the E6 exposition bridge, the corrected literature-protocol
interpretation, and the later A20-addendum chronology.

The proof-separated
[Wave 27 literature audit](wave27-literature-audit/audit.md) covers 56 frozen
or separately frozen service-query pairs and 303 inspected records through
2026-07-24. It records conceptual component and Cartan-matrix prior art, a
retained protocol correction, and failed-service results without treating
them as nonexistence evidence. No direct match was found within the bounded
search, but novelty and priority remain `UNKNOWN`.

The detached
[Wave 27 clean-source replay](2026-07-24-wave27-clean-clone.md) records 116
passing tests, seven byte-identical regenerations, six exact manifests,
central metadata and link gates, exact-blob privacy scans, clean status, and
strict Git object verification.

## Wave 28 unrestricted-lattice reductions and controls

Wave 28 has four independently separated packages.

The
[glue/discriminant audit](wave28-glue-discriminant/audit.md) reconstructs
the elementary 3- and 7-primary discriminant groups, exact levels, twelve
formal Milgram-compatible quadratic modules, scaled-dual local signs,
single-root complement theorem, primitive root-closure/glue reduction, and
the exact `46 -> 32` root-image pattern census. Its verdict is
`PASS_WITH_CORRECTION`: the frozen discovery report falsely excludes cyclic
order-21 invariant factors. The correct statement permits order 21 while
excluding `p`-primary factors of order `p^2` or higher.

The
[theta/modular audit](wave28-theta-modular/audit.md) independently checks all
eight levels and characters, the Poisson/Weil conventions, Sturm bounds,
modularity vetoes, ADE controls, and the rootless bare lattice

```text
K12 orthogonal_sum LAMBDA(F).
```

A complete fraction-free closed-ellipsoid recursion visits 15,053,011 nodes
and finds all 146,880 norm-four vectors of `LAMBDA(F)`. The resulting
rank-44 control has determinant 729, no roots, 147,636 norm-four vectors, and
exact scaled-dual minimum 28. Its finite discriminant quadratic module is
explicitly isometric to that of the rooted comparator
`E6^6 orthogonal_sum E8`. This verifies that the bare data do not force a
root; it does not construct the endpoint frame.

The
[simultaneous-neighbor audit](wave28-simultaneous-neighbor/2026-07-24-wave28-simultaneous-neighbor-audit.md)
reconstructs two rational basis changes of the Wave 27 paired-form package,
all transformed matrices, both root cosets, ADE components, primitive
closures, and glue indices. The preferred neighbor has root rank 43; the
retained initial neighbor has root rank 44. Both are abstract arithmetic and
lattice controls only.

The proof-separated
[literature audit](wave28-literature-audit/audit.md) executes all 35 frozen
queries, retains 17 metadata-only source records and two explicit access
limitations, and finds no exact target resolution or combined Wave 28
precedent. A 2025 refereed source calls the problem open, and a 2026 SAT
preprint reports no resolution. Non-discovery does not establish novelty,
priority, or openness after the cutoff.

The five mathematical suites pass, in discovery/verification order,

```text
13, 14, 16, 20, 25 tests: 88 total.
```

All 46 entries of the six Wave 28 manifests validate. The
[correction ledger](2026-07-24-wave28-orchestrator-corrections.md) records
the order-21 prose defect, the stale eleven-form count, freeze and mutation
chronology, non-evidentiary direct-enumeration timeout, metadata repair,
theta preprocessing failures, source-retention boundary, and telemetry
packaging repair.

The detached
[clean-clone replay](2026-07-24-wave28-clean-clone.md) passes all 88 tests,
five byte-identical regenerations, six manifests with 46 entries, central
metadata, all-repository local links, exact-blob privacy scans, clean status,
and strict Git object verification at integration commit
`4c4d2cb8dec14c7834984d47a7e5b29991891e60`.

The accepted scope is:

```text
corrected necessary glue/theta restrictions: VERIFIED
rootless bare S/G control: VERIFIED
two abstract simultaneous neighbors: VERIFIED
full X/M/W/Q/B endpoint package: UNKNOWN
n3=708 / Conway-99 / novelty: UNKNOWN
```

## Wave 39 edge-local rank and proof-shard verification

The [integration audit](2026-07-27-wave39-integration-audit.md) and
[orchestrator decision](2026-07-27-wave39-orchestrator.md) record the accepted
scope.

- `wave39-edge-local-rank/` independently enumerates all 10,395 pulled-back
  matchings, reconstructs the eleven positive partitions of six, proves the
  local rank formula, verifies rank transport, and promotes
  `rank_F7(M)>=19`. Fourteen hostile and exact tests pass.
- `wave39-proof-solver/` independently binds the branch-15 source lines, OPB
  bytes, raw/kernel proof hashes, and generalized-unit derivation. Fresh
  VeriPB 3.0.2 runs accept both proofs. Six tests pass. CakePB supplied no
  conclusion.

The cross-base and simultaneous `B/H` packages remain discovery-only
`DERIVED_INCONCLUSIVE` evidence. They are published for reproducibility, not
promoted as verified contradictions.

```text
rank_F7(M)>=19:                 VERIFIED
branch15 AND x187=1:            VERIFIED UNSAT
branch 15 / proof coverage:     UNKNOWN / 0 of 33
upper bound below 4158:         NOT PROVED
n3=4158 / Conway-99 / novelty:  UNKNOWN
```

## Wave 40 rank completion and edge-coupling verification

The clean-room packages are:

- `wave40-rank19-equality/`: independently reconstructs the conditional
  rank-22 stepping stone, including all 144 third-fibre syndromes, 66
  projective lines, 1,923 two-spaces, 25,744 three-spaces, and the positive
  dimension-three boundary.
- `wave40-exact-coupling-model/`: independently rebuilds all eleven
  edge-local forms and the arbitrary-completion rank lemma. It verifies
  `min_f rank(H^T U_f)=e` when the partition has `e` even parts, and therefore
  promotes the universal theorem `rank_F7(M)>=25`.
- `wave40-edge-type-coupling/`: independently reconstructs the global
  face/surface identities, all 4,050 normalized all-`222` quotients, the
  exact 39-block Laplacian identity, and the complete `2^18` lift census for
  one boundary quotient.

The [Wave 40 integration audit](2026-07-27-wave40-integration-audit.md) and
[orchestrator decision](2026-07-27-wave40-orchestrator.md) retain the exact
scope:

```text
rank_F7(M)>=25:                    VERIFIED
endpoint arithmetic rank pairs:    330
one-quotient rank-33 lift census:   VERIFIED SCOPED
endpoint proof coverage:            0 of 33
upper bound below 4158:             NOT PROVED
n3=4158 / Conway-99 / novelty:      UNKNOWN
```

## Wave 43 endpoint-rank and scoped reductions

The Wave 43 clean-room packages are:

- `wave43-rank28/`: independently exhausts every endpoint local rank-27
  mechanism and verifies `n3=4158 => rank_F7(M)>=28`.
- `wave43-all-rank33-lifts/`: independently reconstructs all 264 retained
  masks and every forced-Gram and six-set census record.
- `wave43-branch15-two-triangle/`: independently reconstructs 40,800 raw
  cuts, 34,340 active cuts, and all 64 null probe records.
- `wave43-seven-deck-endpoint/`: independently enumerates the complete
  six- and seven-vertex catalogues and checks the exact unrooted count
  witness.

Each verifier has a protocol freeze, hostile controls, a run report, and a
hash manifest. Only the rank-28 implication is a graph-theoretic theorem;
the other three are scoped reductions or relaxation-feasibility controls.

## Wave 44 aggregate rooted-count control

`wave44-rooted-flags/` independently rebuilds the 170 exact equations and
checks the 91-support integer witness. It also reproduces and explicitly
refutes the free HiGHS false-infeasibility diagnostic by exact substitution
and a fixed-witness solver control. The accepted scope is feasibility of the
aggregate rooted relaxation only.

## Wave 45 rooted flag moments

`wave45-flag-moment/` independently enumerates the four-vertex rooted flags,
constructs every exact overlap coefficient, checks Petersen and Clebsch
controls, refutes the two stored aggregate witnesses, and replays all 17 cuts
and 15 witnesses from immutable checkpoint v1. Fifteen tests and the package
manifest pass. The accepted result is a verified finite obstruction sequence;
the terminal timeout and the full endpoint remain `UNKNOWN`.

## Waves 46--49 alternative-space verification

- `wave46-f7-code/` independently verifies the conditional ordinary
  characteristic-seven code consequences and rebuilds all 17 generic controls
  in ranks 28 through 44. It verifies a scoped null result, not an endpoint
  code or graph.
- `wave47-three-root-moment/` independently reconstructs all eight labelled
  root families, 57,006 coefficient entries, 136 stored-witness matrices,
  2,664 exact negative directions, and 2,657 primitive cuts.
- `wave47-branch15-polynomial/` independently reconstructs the seven
  degree-two Macaulay windows, all 13 XOR relations, and the complete
  34,340-row degree-four partition. It finds no contradiction or new unary
  assignment.
- `wave48-conic-moment/` independently reconstructs the Wave 44 affine rank
  93 and nullity 116, then verifies the complete universal kernels of all
  eleven Wave 45/47 moment families without opening numerical solver output.
- `wave49-five-root-moment/` independently reconstructs the 683 labelled
  five-roots, 21 canonical families, 2,520 `S5` relabellings, 42 controls, and
  all 357 exact stored-witness refutations. The numerical SDP artifact is not
  used as evidence.

Every accepted claim is finite and scoped. Combined real/integer feasibility,
endpoint exclusion, a strict upper bound below 4158, graph construction,
novelty, priority, and Conway-99 remain `UNKNOWN` or `NOT PROVED`.

## Wave 51 alternative-space verification

- `wave51-global-triple-tensor/` independently reconstructs the symmetric
  aggregate tensor, all five integral slices, 125 balance equations, and
  exactly 100 of 625 association-algebra failures.
- `wave51-seidel-smith/` verifies the corrected conditional Smith form,
  mod-seven Jordan type, and `r>=14` symmetric-square bound. It explicitly
  refutes the discovery spectrum's reversed nonprincipal multiplicities.
- `wave51-rankone-cut-relaxation/` is the source-side exact 174-cut probe. Its
  self-assigned verified status is procedurally rejected and treated as
  candidate chronology.
- `wave51-rankone-cut-relaxation-independent/` cleanly reconstructs all 170
  equations, 174 cuts, 5,691 Wave 49 tensor evaluations, and the exact
  rational witness. It verifies feasibility of this fixed bundle only.

The three lanes are null results for endpoint exclusion. Pair-specific
quadruple compatibility, the full PSD region, integer feasibility, a graph,
and any strict upper bound below 4158 remain `UNKNOWN` or `NOT PROVED`.

## Wave 52 coherent-closure verification

- `wave52-coherent-closure/` independently reconstructs the forced one-root
  `3K6` structure, global relation valencies, and `B2/C4/D0` cross-sector
  caps.
- Its clean-room 2-WL implementation reproduces the exact trajectories
  `[6]` and `[26,38,47]`, all 64 canonical cycle profiles, 39 fingerprint
  classes, and all 4,096 fingerprint-equivalence comparisons.
- Five hostile mutations are rejected. Explicit integral local completions
  remain, and completed closures depend on arbitrary `B/C` selections.

The accepted claim is a verified local null result. Multi-root compatibility,
three-tuple refinement, graph realizability, endpoint exclusion, and a strict
upper bound below 4158 remain `UNKNOWN` or `NOT PROVED`.

## Waves 56--59 alternative-space verification

- `wave56-percolation-closure/` independently checks the cited closure
  theorem's scope, the target parameter census, all `n3/P/H/R/S` incidence
  identities, 64 tip graphs, 23 endpoint masks, 35 multicovers, and 11
  formal label-orbits. Discovery and verifier suites each pass 21 tests.
- `wave57-star-complement/` independently reproduces the projector,
  supported-eigenspace, star-set, and moment calculations, then materially
  corrects the discovery using prior verified Wave 36 results and
  `C4(X)<=27`. Its scoped verdict is `REFUTED_IN_PART`.
- `wave58-cross-incidence-rank/` independently reconstructs both Gram
  identities, rank transfer, normalized component censuses, exact local
  four-cycle sets, separate controls, and the restricted Wave 40 replay.
  Fourteen verifier and eleven discovery tests pass.
- `wave59-incidence-spectral-excess/` independently reconstructs the
  incidence and triangle-graph spectra, all rooted layers, the failure of
  distance-biregularity, exact predistance polynomials and defects, the
  pair-neighborhood Gram matrix, Ihara cycle counts, and the cage comparison.
  Fourteen verifier tests, including hostile mutations, pass with zero
  mathematical mismatches.

The [integration audit](2026-07-27-wave59-integration-audit.md) and
[orchestrator decision](2026-07-27-wave59-orchestrator.md) retain the Wave 57
correction and the unresolved simultaneous-incidence boundary. Spectral
excess separates the conditional graphs from distance-regular equality
cases; it does not exclude them.

## Waves 53--55 corrected checkpoint verification

- `wave53-proof-cover/` independently reconstructs all 10,395 normalized
  states, 78 refined orbits, the exact 33-case compatible cover, and the
  exported `branch15 AND x187=0` bytes. Fresh Exact, VeriPB, and CakePB runs
  certify only `UNKNOWN` / `VERIFIED NO CONCLUSION`; complete-case coverage
  remains `0/33`.
- `wave53-multi-root-wl/` independently rebuilds the four finite two-root
  templates, all 72 caps, the unique shared forced-true `B` candidate, exact
  2-WL partitions and intersection tensors, folklore 3-WL counts, and
  structurally different positive controls. No root relation is excluded.
- `wave53-exact-cut-loop/` verifies the four rational witnesses, 170 base
  equations, three retained Wave 49 cuts, and exact 177-cut feasibility. It
  refutes the discovery's `128/128` indefinite claim: the corrected count is
  `120/128`, and all twelve reported Wave 45 direction values are affected by
  doubled off-diagonal coefficients.
- `wave54-centered-enumerator/` independently reconstructs all 232 ordinary
  MacWilliams coefficients and verifies the stated formal enumerator,
  including omitted dual parity and `B_231>=2` checks.

The [Wave 55 integration audit](2026-07-27-wave55-integration-audit.md) and
[orchestrator decision](2026-07-27-wave55-orchestrator.md) retain the material
correction and the status wall. The bounded Wave 55 search needs no verifier
promotion because it asserts no terminal mathematical result.

## Waves 60--63 component, field, SDP, and cone verification

- `wave60-c3-incidence-design/` independently reconstructs the
  `216 -> 50 -> 18` component census, all 1,140 triples, 275 safe coordinate
  orbits, candidate counts, pattern counts, and binary target ranks.
- `wave61-c3-finite-field/` independently replays every finite-field,
  full-pair, and pattern-parity calculation. It records
  `VERIFIED_WITH_CORRECTION` because no nonnegative integral cubic tensor was
  tested.
- `wave62-terwilliger-sdp/` independently reconstructs the signed-edge
  association scheme, all 43 endpoint parameters, and the 23,388 exact Schur
  blocks. It clarifies the deliberate omission of one tautology.
- `wave63-c3-integer-cone/` independently rebuilds all candidate lanes and
  checks 46,620 exact pair equations in 74 rational certificates, including
  coefficient-bound and hostile-mutation tests.

The [integration audit](2026-07-27-wave63-integration-audit.md) and
[orchestrator decision](2026-07-27-wave63-orchestrator.md) retain the
unresolved integer/higher-order boundary. No binary incidence design,
compatible `A_Y`, endpoint exclusion, strict upper bound below 4158, or
Conway-99 resolution follows.

## Waves 64--65 rooted transition and hypergraph verification

- `wave64-rooted-transition-design/` independently reconstructs all 84
  labels, 35,560 candidate blocks, 840 transitions, 6,040 local matchings,
  280 triangle cuts, the explicit 140-block witness, the rational full-linear
  control, and the exact residual-codegree closure. Eight hostile and
  deterministic tests pass.
- `wave65-rooted-hypergraph-algebra/` independently reconstructs
  `D+5I=ZZ^T`, the block graph and its local `3K4` structure, spectral and
  four-cycle restrictions, target and transition moments, scalar coupling,
  all 258 averaged PSD lanes, and the exact local control with moment deltas
  `0,0,0,+5496,-12020,+239772`. Seven clean-room tests pass.

The [integration audit](2026-07-27-wave65-integration-audit.md) and
[orchestrator decision](2026-07-27-wave65-orchestrator.md) promote only the
scoped finite results. Integral transition/design compatibility, full
codegrees, the global prism-free endpoint, a strict upper bound below 4158,
and Conway-99 remain unresolved.

## Wave 66 spherical-code and lattice verification

- `wave66-spherical-code-shift/` independently reconstructs the two spherical
  embeddings, the 99-line equiangular lift, centering, lattice saturation,
  determinant and local Smith calculations, exact dual denominator, low-norm
  exclusions, finite Gauss sums, Milgram phase, and Blichfeldt cross-check.
- The verdict is `VERIFIED_WITH_CORRECTION`. Fourteen verifier tests and ten
  discovery tests pass. The corrected universal conclusion is
  `rank_F7(2A-J+I) in {28,30,32,34,36,38,40,42}`.
- The exact conditional lattice data are `63 M* subset M`,
  `det(M)=9*7^(44-r)`,
  `M*/M = Z/9 direct_sum (Z/7)^(44-r)`, and `min(M*)>=2`.

The [Wave 66 integration audit](2026-07-27-wave66-integration-audit.md) and
[orchestrator decision](2026-07-27-wave66-orchestrator.md) preserve all three
corrections and the unresolved status wall. No graph or lattice realization,
endpoint exclusion, strict upper bound below 4158, Conway-99 resolution, or
novelty result follows.

## Waves 69 and 72 order-11 symmetry verification

- `wave72-order11-automorphism/` independently proves that every exact
  order-11 automorphism is fixed-point-free. Fourteen verifier tests and nine
  discovery tests pass, with six compared fields and zero mismatches.
- `wave69-cyclic-cover-shift/` independently reconstructs all seven quotient
  row shapes and three diagonal cases, then exhausts 1,108,533
  label-complete nodes and 8,980 canonical nodes with zero quotient. All six
  transcript hashes and eleven comparison fields match; thirteen verifier
  tests pass.
- Combining the two verified theorems excludes every order-11 automorphism
  and hence every vertex-transitive realization. The independent Fourier
  lane also excludes Cayley realizations on every group of order 99.

The [integration audit](2026-07-27-wave72-integration-audit.md) and
[orchestrator decision](2026-07-27-wave72-orchestrator.md) retain the
restricted scope. Asymmetric targets, the endpoint, a strict upper-bound
improvement, Conway-99, and literature novelty remain `UNKNOWN`.

## Waves 71, 74, and 78 modular-theta verification

- `wave71-modular-theta-extension/` independently verifies the order-nine
  marked class, the index-three even overlattice, the exact level-seven
  scaled dual, Skoruppa weights `154-3q`, every finite-field theta gap, and
  `N14+N16+N18=2 mod 14` in the `q=16` row. Its verdict is
  `VERIFIED_WITH_CORRECTION`: norm-18 `h=2` is impossible, leaving `h=0,1`.
- `wave74-short-vector-closure/` independently checks both `h=2`
  contradictions and all `4/20/6` aggregate histograms. Its audit retains a
  harmless dead-lane bookkeeping clarification.
- `wave78-short-vector-packing/` independently checks the four-subset
  packing bounds and the exact reduced histogram counts `1/7/4`. Its
  multiplicity-aware proof strengthens the discovery wording without
  changing the theorem.

The [integration audit](2026-07-27-wave78-integration-audit.md) and
[orchestrator decision](2026-07-27-wave78-orchestrator.md) retain live
norm-14, norm-16, and norm-18 structures. No lattice realization, graph,
endpoint exclusion, strict upper bound, Conway-99 resolution, or novelty
claim follows.

## Waves 80--82 and 86 alternative-space verification

- `wave80-f7-overlattice-code/` independently verifies the injective
  `[99,44]_7` code, exact hull, rank-28 orthogonal quotient, complete
  support-five dual exclusion, and balanced short-vector images. Ten
  verifier tests and eight discovery tests pass.
- `wave81-norm16-labeled-design/` independently reproduces the full
  1,800-support and 4,985-coupling census. Its stricter graphicality
  extension is separately checked by
  `wave81-norm16-graphical-refinement/`, leaving 40 degree rows at `t=0`
  and seven at `t=1`.
- `wave82-seidel-orthogonal/` independently proves both directions of the
  integral-orthogonal equivalence and the complete Smith form. All eight
  imported rank rows pass the exact arithmetic checks.
- `wave86-level7-exact/` independently reconstructs the full modular-form
  basis, Fricke matrix, Poisson transfer, positive coefficient identity,
  and modulo-14 rounding to `N14+N16+N18>=5868`. Its verdict is
  `VERIFIED_WITH_LITERATURE_CORRECTION` because the printed source formula
  omits a normalization ratio; the discovery's actual factors follow from
  the source's preceding equations.

Wave 84 is published separately as an `UNKNOWN` bounded-search report and
receives no verifier promotion. The
[integration audit](2026-07-28-wave86-integration-audit.md) and
[orchestrator decision](2026-07-28-wave86-orchestrator.md) preserve the
status wall: no rank row, endpoint, or target graph is excluded.

## Waves 90, 94, 99, and 100 norm-14 verification

- `wave90-short-vector-count-upper/` independently verifies the endpoint
  seed injection and `N14<=5544`. Six verifier and seven discovery tests
  pass.
- `wave94-general-n3-norm14-bound/` independently verifies the rooted-prism
  multiplicity, every compatible identity row, and
  `N14<=floor((55440-4*n3)/7)`. Twelve verifier and seven discovery tests
  pass.
- `wave99-transition-pair-moment/` independently verifies the
  transition-pair cap 18, `N14<=4950` at `P=0`, and the rank-28 corollary
  `407*N16+43*N18>=2165002`. Seventeen verifier and eight discovery tests
  pass.
- `wave100-general-pair-moment/` independently verifies the general
  second-moment inequality
  `N14<=2*floor((55440-5*n3)/14)` for all 1,387 compatible rows. Eighteen
  verifier and six discovery tests pass.

These are scoped shell-count theorems. They neither upper-bound `n3` nor
control `N16` or `N18`. The
[integration audit](2026-07-28-wave100-integration-audit.md) and
[orchestrator decision](2026-07-28-wave100-orchestrator.md) retain that
boundary.

## Waves 97 and 98 alternative-space verification

- `wave97-f7-exterior-matroid/` independently verifies the Schur-cube,
  second-compound code, complete Smith, generalized-weight, and finite
  orthogonal-orbit formulas. Its verdict is
  `VERIFIED_WITH_PROVENANCE_CORRECTION`: Wave 51 already implied
  `R*R=1_perp` and the quadratic circuit. Fifteen verifier and fourteen
  discovery tests pass.
- Wave 98 has no verifier promotion. Its three tests reproduce only a finite
  degree-1,000 positivity probe of a formal scalar theta pair, retained as
  `UNKNOWN`.

Neither lane excludes rank 28, constructs a graph, or resolves Conway-99.

## Waves 101--102 all-rank theta and prism-code verification

- `wave101-all-rank-level7-lp/` independently reconstructs all seven
  modular spaces, Fricke transfers, rational LP certificates, parity
  rounding, and scalar null controls. Its scoped verdict is
  `VERIFIED_WITH_SHARPENING`: the triangular mod-two upper estimate improves
  from `704(2^44-1)` to `88(2^44-1)`, but no rank row is excluded. Fourteen
  verifier and eight discovery tests pass.
- `wave102-prism-incidence-code/` independently verifies the parity-defect
  bound, incidence-code factorization, binary ranks, prism-overlap cap, and
  local null motifs. Its verdict is `VERIFIED_WITH_CORRECTIONS`: in
  particular `P=3 => O>=4`, and the possible nonzero `ker(B^T)` weights
  narrow to `{36,40,44,48,52,56,60}`. Ten verifier and fourteen discovery
  tests pass.

The scalar modular cone still permits `N14=N16=N18=0` in every new row, and
the parity-null motif is not certified to extend to 99 vertices. Neither
package supplies a graph, exclusion, strict `n3` upper bound, or novelty
claim.

## Wave 105 motif-extension verification

- `wave105-c4boxk3-extension/` independently reconstructs the forced
  `3,48,36` outside-incidence multiset, all block equations, the exact
  `18,11,5,1` moment census, and the `18,11,4,1` graphical census.
- The verifier supplies the missing triangle-free support proof, checks the
  archived 549-edge linear witness and its hash, and confirms that it fails
  2,525 of 3,741 nonlinear pair rows.
- The complete SAT encoding and four `X0` symmetry branches are audited.
  Preserved raw logs are byte-identical and all remain `UNKNOWN_TIMEOUT`.

The verdict is `VERIFIED_WITH_CLARIFICATIONS`. Eight verifier and eight
discovery tests pass. The [integration audit](2026-07-28-wave105-integration-audit.md)
and [orchestrator decision](2026-07-28-wave105-orchestrator.md) retain the
conditional scope and unresolved full extension.

## Waves 96 and 112 C4-incidence verification

- `wave112-c4-short-vector-incidence/` independently verifies the 2,079
  target cycles, the four alternating-cycle minima `21,20,18,26`, the
  evenness correction from raw ceiling 51 to 52 oriented occurrences, and
  the exact `51,20,20,4` fixed-cycle partition. Eleven verifier and eight
  discovery tests pass.
- `wave96-norm16-norm18-upper/` independently verifies the weighted cap-25
  implication, the fixed-cycle projector, the 80-point cross-polytope null
  control, the norm-20 `10+10` classification, the `h<=3` and 15-cycle
  bounds, and the rank-30 cap-24 implication. Its verdict is
  `VERIFIED_WITH_CLARIFICATION`; thirteen verifier and nine discovery tests
  pass.

Neither cap is proved. No general `N16/N18` upper bound or rank exclusion
follows.

## Waves 107--110 conditional motif verification

- `wave107-c4boxk3-spectrum/` independently reconstructs the conditional
  outside characteristic polynomial, correcting the tentative quadratic
  factor to `x^2-9x-46`. Ten verifier and seven discovery tests pass.
- `wave109-c4boxk3-local-projector/` independently reconstructs the
  primitive incidence kernel, its `O^-(74,7)` type, local projector, rank
  transfer, and Smith/index formulas. Nine verifier and nine discovery tests
  pass.
- `wave110-c4boxk3-symmetry-sat/` independently verifies the lex CNF, the
  simultaneous shared-potential theorem, all four invariant branch covers,
  and the exact encoding counts. Its verdict is
  `VERIFIED_WITH_EVIDENCE_BOUNDARY`; seven verifier and eight discovery tests
  pass.

The fresh Wave 110 runs remain `UNKNOWN_TIMEOUT`. No graph, UNSAT proof,
motif exclusion, or rank exclusion is promoted.

## Wave 116 C4 Jacobi/theta verification

- `wave116-c4-jacobi-theta/` independently verifies the restricted
  projector, the valid `K/L` marking scalings, the nondegenerate
  `(Z/7)^4` sector and retained complement, the Poisson/Fricke factors, and
  the exact antipodal coefficient convention.
- The verifier sharpens the main correction: `u_i/sqrt(7)` is definitively
  outside `K*`, so the proposed small index is invalid.
- Rank 28 forces 52,812 antipodal incidences; the desired cap-25 upper is
  51,975, leaving an exact gap of 837.
- Eleven verifier and eight discovery tests pass. The verdict is
  `VERIFIED_WITH_CLARIFICATIONS`.

No Jacobi upper certificate or rank exclusion is present. Wave 118 is
published separately as a sealed subjective estimate and receives no
mathematical verifier promotion.

The [integration audit](2026-07-28-wave116-integration-audit.md) and
[orchestrator decision](2026-07-28-wave116-orchestrator.md) preserve all
conditional and `UNKNOWN` boundaries.

## Waves 123 and 127--131 alternative-space verification

- `wave123-fixedc4-threepoint/` independently reconstructs every exact span
  projector, all 4,851 graph-valued pair rows, and 2,340 rooted
  feature-Gram blocks.  Six verifier tests pass.  The nonexhaustive search
  proves no local cap.
- `wave127-wave129-jacobi-audit/` independently rebuilds the modular
  dimensions, Fricke factor, cache consistency, and all 5,874 original
  candidate rows.  Cutoffs `10--20` are exact finite feasible; cutoff 28 was
  still `UNKNOWN` at that checkpoint and is resolved as finite-feasible by
  Wave 130 below.  Six verifier tests pass.
- `wave128-alternative-spaces/` independently reconstructs the finite Smith
  split, exact quadratic Gauss phases, seven-adic gluing, both rootlessness
  arguments, and survival of every imported row.  Eight verifier tests
  pass.
- `wave131-binary-lcd-enumerator/` independently checks the LCD/symplectic
  derivation, every subset type through size three, all 200 MacWilliams
  rows, and the nonintegral rational witness.  Six verifier tests pass; the
  integral scout remains non-evidentiary `UNKNOWN`.

The [integration audit](2026-07-28-wave131-integration-audit.md) and
[orchestrator decision](2026-07-28-wave131-orchestrator.md) preserve the
status wall.  No code, lattice, graph, rank exclusion, strict `n3` upper
bound, Conway-99 resolution, or novelty claim follows.

## Waves 130 and 132--134 verification

- `wave130-cdd-exact-lp/` independently regenerates all 239 Jacobi columns
  without discovery imports or serialized caches.  It verifies the
  cutoff-28 rational point against 454 equalities and 1,686 inequalities,
  with zero failures and 506 tight rows.  Three verifier tests pass.
- `wave132-distinguished-biweight/` independently verifies all 200
  MacWilliams rows, all four split systems, the pair tables, the
  `A94=A96=A98=0` cut, and the surviving stronger rational witness.
- `wave133-triangle-holonomy-topology/` independently reconstructs both
  opposite-sign local controls and the full cover, balanced quotient, link
  normalization, Euler characteristic, and nonorientable endpoint-scale
  surface control.
- `wave134-z4-symmetrized-enumerator/` independently derives the quaternary
  code types, residue/torsion restrictions, complete size-three forced-word
  tables, sparse transform coefficients, and corrected 1,119/1,114/161 orbit
  partition.  Its two prepublication vetoes are retained.  Corrected
  rational and integral feasibility remain `UNKNOWN_NOT_RUN`.

The [integration audit](2026-07-28-wave133-integration-audit.md) and
[orchestrator decision](2026-07-28-wave133-orchestrator.md), followed by the
[Wave 134 audit](2026-07-28-wave134-integration-audit.md) and
[decision](2026-07-28-wave134-orchestrator.md), preserve the finite and
conditional scope.  Rank 28, the prism-free endpoint, the strict `n3`
upper-bound question, code realization, and Conway-99 remain `UNKNOWN`.

## Waves 135--142 alternative-space verification

- `wave135-z4-exact-face/` independently verifies the corrected orbit
  partition, zero-row rank 143, affine rank 145, torsion-tightened rank 146,
  and both `UNKNOWN_WALL` records.  Thirteen hostile tests pass.
- `wave136-alternative-spaces/` independently reconstructs the Arf/Gauss
  branches, additive-`GF(4)` graph-state self-duality, character transform,
  parity-zero states, and all support-at-most-three rows.  Its verdict is
  `PASS_WITH_SCOPE_CORRECTION`; quantum-shadow inequalities were not promoted.
- `wave137-arf-krawtchouk/` independently replays all fourteen rational
  witnesses, all ordinary/split rows, the cumulative signed ranks, and every
  terminal shadow inequality.  Integral realization remains `UNKNOWN`.
- `wave140-arf-sign-lattice/` independently verifies the determinant bridge
  and opposite-sign controls.  Its verdict is
  `PASS_WITH_SCOPE_CORRECTION` because the controls are not integral
  zero-one SRG adjacency matrices.
- `wave141-bivariate-graph-code/` independently reconstructs two transform
  controls, the `D8` dimensions/ranks, all 62 six-set classes, the
  `S0`--`S6` identities, and `B[6,56]>=n3`.  Eleven hostile tests pass.
- `wave142-interlace-isotropic/` independently verifies the local interlace
  rows, kernel moment, all isotropic diagonal toggles, and the
  support-intersection refinement.  Its verdict is
  `PARTIAL_PASS_WITH_TOP_BAND_VETO`: minimum image weight 14 is unsupported,
  so sizes 86--91 are rejected and only 92--99 remain forced.

No verifier promotes a rational enumerator to a code, a local profile to a
graph, a numerical timeout to infeasibility, a strict upper bound below
4,158, or a Conway-99 resolution.

## Waves 143--146 projection and rooted-overlap verification

- `wave143-binary-s6-projection/` independently replays eight rational
  endpoint/Arf witnesses, all ordinary and split rows, the exact `S6`
  identity, and the full HNF reconstruction.  Its verdict is
  `PASS_WITH_SCOPE_CORRECTION`: the target proves binary minimum eight, not
  the formal dual minimum fifteen used by the rational slice.
- `wave144-sixset-odd-profile-cleanroom/` independently rebuilds the
  four-/five-/six-class alignment, all 62 supports, 66 local profiles, and
  the 65-cell endpoint aggregate.  Its verdict is `PASS_NULL_BOUNDARY`;
  overlap consistency is absent.
- `wave139-gf4-lower-aggregation/` refutes the Wave 139 `max` merge, verifies
  the five corrected sums, vetoes pure-`Y` zeros 8, 10, and 12, and
  independently calibrates the Rains shadow formula on 1,099 small graphs.
  Corrected feasibility remains `UNKNOWN`.
- `wave146-six-seven-coupling/` independently reconstructs the rooted
  pattern filter, automorphism-orbit/deletion coefficients, and exact
  rational endpoint replay.  Its scope ends at one-root aggregate
  compatibility; it does not promote the witness to a graph.
- `wave147-pair-root-order8/` independently reconstructs the two rooted flag
  bases, complete order-eight class stream, full deletion layer, 24
  representative matrices, target `n3`/prism matrices, artifact counts, and
  rook-graph positive control.  It does not independently recompute all
  272,054 stored coefficients.  It verifies a finite model only; no numerical
  or exact endpoint SDP result is present.

The rigorous interval remains `708<=n3<=4158`.

## Waves 148--152 order-eight and triangle-root verification

- `wave148-marked-order8/` independently reconstructs every marked row by
  semantic key, all 28,654 coefficients, zero-capacity rows, column
  identities, and rook/micro controls.  Verdict: `PASS_WITH_SCOPE`.
- `wave150-exact-rank1-witness/` independently rebuilds all Wave147
  coefficient matrices and Wave148 rows, replays all 10,310 equations,
  verifies both zero centered covariance blocks, and reproduces modular rank
  874 over `F_1000003`.  The vector is a finite-relaxation witness, not a
  graph.
- `wave149-terwilliger-triple/` independently derives the triangle partition,
  prism trace, Gram matrix, exact character spectrum, and rank 32.  This
  verifies a null first projection only.
- `wave151-triangle-root-factor/` independently reconstructs the binary
  24-by-60 factor and all four relevant Gram blocks.  It explicitly demotes
  the proofless fixed-branch `UNSAT` status and leaves the full factor and
  residual graph unknown.
- `wave154-triangle-factor-portfolio/` independently reconstructs both
  24-by-60 factors, the full 384-element centralizer, disjoint size-384
  factor orbits, all 69,270 allowed triples, the 292-orbit histogram, 612
  rows, and 1,039,050 nonzeros.  Every solver-negative status remains
  diagnostic; the full factor and residual graph are unknown.
- `wave152-four-root-order8/` independently rebuilds all nine flag universes
  and order-6/7/8 products.  Exact integer quadratic values for masks 3 and
  12 are strictly negative, so the stored Wave150 pseudowitness is
  `VERIFIED` refuted in the stronger space.  This does not refute every
  endpoint count vector.
- `wave155-four-root-feedback/` independently reconstructs the first four
  primitive covariance cuts and the exact replacement witnesses.  The
  two-cut vector passes 10,311 equations with modular rank 885; the four-cut
  vector passes 10,312 with rank 886.  Both finite systems remain exactly
  rational feasible.  Later mask-13 and simplified-cut artifacts are outside
  this verifier's pre-inspection freeze.
- `wave156-four-root-late-feedback/` independently reconstructs the mask-13
  principal cut, the later mask-3/12/13 directions, and both simplified
  mask-12 inequalities.  The five- and eight-cut witnesses each pass 10,312
  exact rows with rank 886.  The first simplified cut is positive, proving
  retained nine-cut finite feasibility; the sparse
  `18711+6*N_cube-2*N_Wagner>=0` cut rejects that witness, so ten-cut
  feasibility remains unknown.
- `wave153-alternative-compatibility/` independently rebuilds all 18
  component graphs, six coordinate actions, and 275 orbits covering 1,140
  triples.  It replays 173,250 pair equations and 9,900 row margins exactly.
  Its verdict is `VERIFIED_WITH_SCOPE`: every complete bounded rational
  pair-correlation projection survives, but no binary design or residual
  graph is supplied.
- `wave158-general-cube-wagner/` independently reconstructs the full symbolic
  mask-12 covariance expansion, root count `1,014,552`, union classes and
  coefficients, cube/Wagner isomorphisms, `N9=41580-n3`, and both primitive
  gcd reductions.  It verifies
  `41580-n3+12*N_cube-4*N_Wagner>=0` for every hypothetical target graph.
  The theorem alone allows the endpoint.
- `wave161-four-root-cut-loop/` independently rebuilds the two fresh Wave159
  cuts and replays the exact fifteen-cut pseudowitness: support `204/887`,
  10,313 exact rows, 10,274 restricted rows, modular rank `887/887`, all
  fifteen cuts nonnegative, and three active.  It independently recovers
  strict negative four-root directions at masks 3 and 12.  This verifies
  finite-relaxation feasibility and the recurring obstruction, not a graph
  or endpoint feasibility.
- `wave165-general-cube-upper/` independently reconstructs the fixed-C4
  partition, exact boundary matching sizes, marked-square/prism bijection,
  and cube-face multiplicities.  Verdict: `VERIFIED_WITH_SCOPE` for
  `12*N_cube<=37422+3*P=41580-n3`, with endpoint consequence
  `N_cube<=3118`.  It does not prove a Wagner lower bound or exclude the
  endpoint.
- `wave166-rooted-wagner-spaces/` independently verifies the fixed-square
  degree identity and null shell, the exact 40 marked five-cycles per
  nonedge, eight five-cycles per Wagner, and the conditional endpoint
  arithmetic.  It explicitly leaves
  `P=0 => at most four failed marks per nonedge` `UNPROVED`; no Wagner lower
  bound is promoted.
- `wave167-nonedge-core-fringe/` independently reconstructs the 22-edge
  nonedge cross graph, exact 18-core/four-fringe split, four mandatory
  failures, completion uniqueness, and the global defect identity
  `E=8*(18711-N_Wagner)`.  It verifies that the endpoint requires `E>=16`
  and that `E<=8` would exclude it, while an explicit local shell shows the
  current one-root equations do not prove that bound.
- `wave168-incidence-minor-energy/` independently derives the 231-block
  triangle incidence geometry, all point-block and block-intersection
  spectra, and the equivalence between `P=0` and block codegree at most two.
  It verifies cube/Wagner determinant energies 4,423,680 and 4,439,040, the
  global Cauchy-Binet coefficient identity, and
  `T*T^T=816I+10K` for the rectangular neighborhood-triple matrix.  No bound
  on the remaining eight-point types is promoted.
- `wave169-failure-hypergraph/` uses two hostile paper audits to verify the
  exact threshold equivalences and a five-failure local relaxation model.
  The supported conclusion is only that current pairwise/root-local clauses
  cannot prove the pointwise four-failure upper bound; the gadget is not an
  SRG candidate.
- `wave170-block-profile-ternary-code/` independently verifies the exact
  pointwise/global block profiles, maximum clique size seven, ternary Gram
  rank 55, and incidence rank interval 55 through 98.  These add exact
  structure but no strict `n3` bound.
- `wave171-pq-centered-code/` independently verifies the square-zero
  polynomial `X=K-K^2`, its exact weight-198 row profiles, point-star kernel,
  intrinsic recovery of the incidence geometry, and
  `rank_F3(X)=rank_F3(C)-1`.  It also verifies that `X=2(C+J)` without the
  endpoint hypothesis, so the code is exactly the earlier centered code and
  supplies no new obstruction.
- `wave172-weight3-dual-rigidity/` independently verifies, by a different
  integer-lift and row-distance argument, that endpoint weight-three dual
  words can only have equal coefficients and the joint distribution
  `000^15,111^144,222^18,(012 permutations)^54`.  The result needs `P=0`
  but not `r3=12`; it is a marked constraint, not an endpoint exclusion.
- `wave173-complete-enumerator-lift/` independently reconstructs the
  complete Krawtchouk moments and verifies that the Wave54 distribution has
  no lift compatible with the 231 distinguished weight-198 compositions and
  Wave172.  It also independently verifies the exact general six-cell
  rational control, preserving the boundary that other ordinary
  distributions remain unclassified.
- `wave174-no-weight3-dual/` independently reconstructs the point--triangle
  line-sum coloring, five-cell edge equations, spectral quotient,
  common-neighbor convexity, and final prism.  The verifier caught the
  degenerate `c=18` case omitted from the first draft and supplied the
  separate exact exclusion `v^T(3I-A)v=-1152`.  With that repair it verifies
  `d(W^perp)>=4` at `P=0`, without assuming `r3=12`.
- `wave175-polar-cap-boundary/` independently reconstructs the
  `Q(10,3)` polar graph, both selected-set spectral energies, outside-point
  moments and mod-three slack, and the quadratic-Veronese rank caps
  `65/66`.  It also checks the primary polar-cap definition and confirms that
  its no-two-collinear hypothesis fails for the 3,696 selected orthogonal
  pairs.  Verdict: `VERIFIED_WITH_SCOPE`; rank 11 and the endpoint survive.
- `wave176-star-projector-circuits/` independently reconstructs the
  six-dimensional star projectors, the trace-zero symmetric-square rank
  cap, all four adjacent 2-regular cycle types, and their ternary Gram ranks
  `10,10,8,9`.  A separate periodic-second-difference derivation verifies
  the ranks, and the radical inequality is used to distinguish true column
  relations from extra Gram-kernel vectors.  Exact minimum non-star supports
  8 and 4 are promoted only for the two rank-10 types.  Verdict:
  `VERIFIED_WITH_SCOPE`; global circuit compatibility and the endpoint
  remain `UNKNOWN`.
- `wave177-relation-averaging-conic/` independently verifies the
  full-support relation-code averages 8 and `28/3`, hence true cross-star
  support ranges `4..8` on edges and `4..9` on nonedges.  It also verifies
  the edge coefficient-sum lift and reconstructs the type `4+2` word as the
  complete `Q(2,3)` conic with frame `-I`, canceled by the nine-point
  complement frame `+I`.  Verdict: `VERIFIED_WITH_SCOPE`; 693 edges index
  choices but do not yet force 693 distinct words, and the endpoint survives.
- `wave178-edge-circuit-injection/` independently verifies the shared- and
  disjoint-endpoint multiplicity proof, the projective factor two, and all
  four local Gram-kernel profiles using a periodic-recurrence reconstruction.
  Verdict: `VERIFIED_WITH_SCOPE`; 693 distinct balanced projective circuits
  of sizes `4,6,8` force `B_4+B_6+B_8>=1386`, but do not exclude rank 11.
- `wave179-global-transversal-circuits/` independently verifies nonedge
  cross-circuit extraction, the exact-two-transversal multiplicity bound,
  all third-vertex collision cases, and balanced-edge global isolation.
  Verdict: `VERIFIED_WITH_SCOPE`; at least 2,079 projective circuits of
  sizes `4..9` force `B_4+...+B_9>=4158`.  The endpoint and strict `n3`
  improvement remain `UNKNOWN`.
- `wave180-capacity3-companion/` independently reconstructs the
  multiplicity-three support shape, seven-entry cross-edge profile,
  projector residue, duplicate-vector exclusion, and the complete
  weight-four/weight-five conic-companion relation space.  It then checks
  the fixed-point-free same-label involution and inclusion-minimal-cover
  count.  Verdict: `VERIFIED_WITH_SCOPE`; at least 2,079 nonedge-realizing
  and 2,772 total projective circuits force `B_4+...+B_9>=5544`.
  Rank 11, the endpoint, and a strict `n3` improvement remain `UNKNOWN`.
- `wave181-c4-conic-equality/` independently confirms that the baseline
  edge in the shared-center star profile must be retained, excluding that
  multiplicity-two case by projector singularity.  It reconstructs the
  canonical nonedge involution, checkerboard four-block Gram and conic, the
  `Q=2079` equality implications, and
  `R_square^T R_square=36I-4K+L`. Verdict:
  `VERIFIED_WITH_SCOPE`; at that checkpoint equality, the needed rank-221
  lower bound, rank 11, and the endpoint remained `UNKNOWN`. Wave186 later
  excludes the equality face independently.
- `wave182-a6-root-gluing-verifier/` independently verifies exact nonedge
  root intersections, 4-regular complement color classes, the support
  bounds `5..10`, the global root interval `231..415`, and the rigid
  231-root incidence boundary with spectrum `189^1,35^54,0^44`.  Verdict:
  `VERIFIED_WITH_SCOPE`; the extremal design survives both the incidence
  spectrum and characteristic-three frame test.
- `wave183-root-support-girth-verifier/` independently verifies the
  canonical-4-cycle common-neighbor obstruction, unordered two-path
  injection, cubic support contradiction, and the resulting support
  classification `5K1,3K2,C7`.  It sharpens the conditional projective-root
  interval to `297..415` and verifies
  `7R-2079=2n5+n6` plus the characteristic-three split frame.  Verdict:
  `VERIFIED_WITH_SCOPE`; the split frame gives no contradiction within its
  conditional scope. Wave186 later excludes that equality regime; rank 11
  and the endpoint remain `UNKNOWN`.
- `wave184-root-support-intersections-verifier/` independently verifies
  that distinct root supports meet in at most a graph edge and that every
  internal support-edge/root incidence gives a new, globally injective
  projective weight-four circuit.  Exact counting gives
  `E=3n6+7n7>=12`, hence at least 2,091 projective weight-four circuits and
  `B4>=4182`.  Verdict: `VERIFIED_WITH_SCOPE`; the scalar equality witness
  is not geometric and no incompatible `B4` upper bound is known. Wave186
  later excludes the equality regime by a different invariant; rank 11 and
  the endpoint remain `UNKNOWN`.
- `wave185-local-a6-transition-collapse-verifier/` independently rebuilds
  the local negative-`A6` cell geometry, excludes same-endpoint internal
  edges, derives `n7=0`, and verifies the type-5/type-6 transition profiles,
  `n5>=15`, the conditional root interval `349..415`, and the lower bound
  94,264 on rainbow complement triangles. Verdict:
  `VERIFIED_WITH_SCOPE`; it is a correct theorem on the former `Q=2079`
  equality face.
- `wave186-star-translation-cover-verifier/` freezes the source inputs but
  imports none of its proof code. It independently reconstructs the
  endpoint-star and private-leaf-star translations, distinctness from
  dual distance four, minimum-cover private-label count, external-circuit
  capacities, and the final linear combination
  `9Q>=8*4158`. Verdict: `VERIFIED_WITH_SCOPE`; `Q>=3696`, at least 4,389
  projective circuits of weights four through nine, and
  `B4+B5+B6+B7+B8+B9>=8778`. This excludes `Q=2079`, but does not exclude
  rank 11 or the endpoint.
- `wave188-affine-star-word-amplification-verifier/` independently
  reconstructs the precise 438-profile affine-orbit census, projective
  distinctness, support capacities, one-block projector collapse, all
  type-one/type-two/type-three private-label words, and ten cross-family
  collision checks. It imports and executes no discovery code. Verdict:
  `VERIFIED_WITH_SCOPE`; at least 8,316 nonedge-realizing and 9,009 total
  projective short-word classes force
  `B4+B5+B6+B7+B8+B9>=18018`. These are dual words, including a necessary
  weight-eight noncircuit, so the result is not a circuit bound
  `Q>=8316`. Rank 11 and the endpoint remain `UNKNOWN`.
- `wave187-code-geometry-proof-b-verifier/` independently reconstructs the
  exact rational hostile control without importing or executing its
  discovery checker. It verifies all 232 ordinary MacWilliams rows,
  complete ternary nonnegativity through total degree six, the quadratic
  type moments and integral three-point Gram census, and the first negative
  complete cells
  `B70=B07=-10151603437954385741/508426957500` at degree seven. Verdict:
  `VERIFIED_RELAXATION_BOUNDARY`; this is a rational relaxation witness, not
  a code, point set, endpoint graph, or existence result.
- `wave189-degree7-star-orbit-verifier/` independently verifies two
  disjoint claims. The displayed rational control is feasible for the
  one-star polygon, all complete rows through degree seven with
  `B70=B07=99`, the degree-12--14 star-pair rows, ordinary rows, and typed
  moments; this is `VERIFIED_RELAXATION_FEASIBILITY`, not code existence.
  Separately, clean-room reconstruction of singleton translation, orbit
  closure, center orientation, and checkerboard equality exclusion gives
  the conditional theorem `Q>=4852`. Overall verdict:
  `VERIFIED_WITH_SCOPE`.
- `wave190-residual-stability-verifier/` reconstructs exact-one slack,
  raw-versus-residual label exclusivity, all collision capacities, and the
  five-slack identity
  `delta+3h+3Y>=p3`. The exact coefficient row
  `6Q>=4I+n1+2(p2-n2)>=8*4158` gives the conditional theorem `Q>=5544`,
  hence 6,237 projective short circuits and the circuit-only scalar bound
  `B4+...+B9>=12474`. Verdict: `VERIFIED_WITH_SCOPE`; the sharp row is
  arithmetic only and no endpoint is constructed or excluded.
- `wave191-exact-three-residual-verifier/` independently verifies the
  exact-three raw exclusion, orbit-closed residual capacity, and conditional
  bound `Q>=6237`. Verdict: `VERIFIED_WITH_SCOPE`.
- `wave192-equality-face-verifier/` independently reconstructs the Wave 191
  equality face and excludes it by canonical-square cohomology and
  checkerboard translations. Verdict: `VERIFIED_WITH_SCOPE`; `Q>=6238`.
- `wave193-global-low-target-verifier/` checks the full split accounting and
  both collision rows behind `117Q>=177C`. Verdict:
  `VERIFIED_WITH_SCOPE`; `Q>=6291`.
- `wave194-five-thirds-verifier/` freezes its result before source inspection
  and verifies the doubled type-two residual, joint leaf capacity, and
  `3Q>=5C`. Verdict: `VERIFIED_WITH_SCOPE`; `Q>=6930`.
- `wave195-hilton-milner-verifier/` verifies the simple intersecting local
  3-subset family, the exact Hilton--Milner specialization, the common-star
  case, and the certificate `Q>=6980`. Verdict: `VERIFIED_WITH_SCOPE`.
- `wave196-four-fiber-hilton-milner-verifier/` independently verifies the
  21 four-point fibers, both equality templates, `c_x<=13`, `j_x<=36`, and
  `Q>=7029`. Verdict: `VERIFIED_WITH_SCOPE`.
- `wave197-degree10-flag-cap-verifier/` independently verifies five flags per
  orientation, ten per unordered selected label, private degree one, and the
  exact target `70323/10`. Verdict: `VERIFIED_WITH_SCOPE`; `Q>=7033`.
- `wave198-orientation-lift-verifier/` verifies orientation multiplicities,
  selected/full-pool separation, the weighted `S5` row, and target
  `281457/40`. Verdict: `VERIFIED_WITH_SCOPE`; `Q>=7037`.
- `wave200-two-face-gluing-verifier/` verifies additive saturated-fiber loss
  and explicitly repairs the source wording by using simple-family pair
  degree at most five. Verdict: `VERIFIED_WITH_SCOPE`; `Q>=7039`.
- `wave201-multiplicity-weighted-fiber-loss-verifier/` independently handles
  multiple selected values in one fiber, multiplicity one, deficient
  centers, and exactly three tight Hilton--Milner baselines. It verifies
  `delta>=3q-epsilon` and the exact target `70587/10`. Verdict:
  `VERIFIED_WITH_SCOPE`; `Q>=7059`, 7,752 projective and 15,504 scalar short
  circuits after adjoining the edge-isolated family.
- `wave202-three-unit-equality-face-verifier/` verifies the complete
  three-unit partition at `Q0=7059`, the raw-variable formulas, local
  equality conditions, `c_x in {12,13}`, and the cap of three
  multiplicity-one nonprivate orientations. Verdict:
  `VERIFIED_FACE_CHARACTERIZATION_NO_EXCLUSION`; an alternate local
  multiplicity control survives, so `Q>=7059` is unchanged.
- `wave203-two-center-incidence-verifier/` independently verifies the shared
  five-slot geometry, reverse matched-block implication, normalized
  all-equal relation, and canonical-quadrilateral Gram obstruction. Verdict:
  `VERIFIED_TWO_CENTER_CAPACITY_NO_BOUND_PROMOTION`;
  `m_(x->y)+m_(y->x)<=5`,
  `3n3+4p3<=5|U|`, and `epsilon>=5b`. A `b=0` accounting/local control
  survives, so `Q>=7059` remains the honest bound.

No verifier promotes a pseudowitness refutation to endpoint infeasibility, a
partial binary factor to a graph, or a numerical solver status to a proof.
The rigorous interval remains `708<=n3<=4158`.

## Wave 204 global-compatibility verifier

`wave204-global-compatibility-verifier/` froze an independent protocol,
checker, 11 hostile tests, result, and hashes before source exposure. After
unsealing, a second checker imported no discovery Python and directly
validated the stronger submitted JSON semantics. Results:

```text
submitted manifest entries:       32/32 match
submitted tests:                  8/8 + 10/10 + 10/10 pass
source-blind tests:               11/11 pass
post-source semantic tests:        5/5 pass
```

Promoted labels:

- relaxed 99-center certificate `VERIFIED`; local interface forces `b>0`
  `REFUTED_WITH_SCOPE`;
- true block gain is a coboundary `VERIFIED`; center chaining and determined
  total `S_5` `REFUTED_WITH_SCOPE`;
- conditional adjacent fourth-order detector `VERIFIED`; pair trace plus
  intersection dimension determines `h` `REFUTED_WITH_SCOPE`.

The optional repeated-direction 99-projector controls remain
`SOURCE_REPLAYED_SCOPED_RELAXED`, not independently promoted. No rank-11 or
endpoint exclusion, `Q>=7060`, strict `n3` improvement, graph/code,
Conway-99 resolution, novelty, or priority claim follows.

## Wave 205 fourth-trace globalization verifier

`wave205-fourth-trace-globalization-verifier/` froze an independent algebra,
finite checker, radical guard, nine tests, result, and hashes before opening
any Wave 205 discovery package. After source exposure, a second checker
imported no discovery Python and independently reconstructed the normalized
census and submitted JSON certificates.

```text
source-blind tests:             9/9 PASS
post-source independent tests:  8/8 PASS
Proof-A submitted tests:       13/13 PASS
Proof-B submitted tests:       12/12 PASS
hostile submitted tests:         6/6 PASS
mathematical/scope findings:      NONE
```

Verdict: `VERIFIED_WITH_SCOPE_NO_FINDING`. Promoted claims are limited to
the exact nonedge pair-local constraints and censuses, scoped refutations,
the full crossing factorization/localizers, and the relaxed-control
predicates. Actual endpoint nonedge traces, rank 11, `n3=4158`, and
Conway-99 remain `UNKNOWN`.
