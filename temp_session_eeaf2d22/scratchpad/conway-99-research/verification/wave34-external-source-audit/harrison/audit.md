# Wave 34 Lane E2 audit: Harrison rooted-fiber repository

Date: 2026-07-24

Role: verifier

Pinned repository: `https://github.com/harrisonpedrero/conway-99-graph`

Pinned commit: `26b36c540611fa02c95a5a4bd78cd4a582257195`

## Verdict

The mathematical bridge into the repository's **honest rooted counting
model is valid for an arbitrary root of an unrestricted
`srg(99,14,1,2)`**, and the tracked SAT-ladder builder does not import the
earlier retracted forced-edge assumption. The exact orbit partitions, the
leaf-stripping/coordinate-balance forcing layer, and every tracked CNF recipe
hash were independently reconstructed.

The exclusion theorem itself is **not independently verified from the pinned
source package**:

- all 830 k>=14 ladder CNF bodies and all corresponding proof bodies are
  absent from the Git tree;
- the 14 claimed exact-rational Gram certificates and their checker are in an
  ignored working directory and are absent from the pinned tree;
- the six non-Gram residuals have only author logs or prose verdicts at this
  pin, not proof bodies;
- the R230 cap has 24 CNFs and 24 DRATs only as unpulled Git LFS pointers in
  this clean clone; and
- k=13 `res1` remains a disclosed cloud-verdict-only gap.

Therefore:

| statement | audit label |
|---|---|
| arbitrary rooted SRG implies the honest equations | `VERIFIED` |
| honest SAT builder avoids the retracted forced-edge routine | `VERIFIED` |
| all-21-C4 condition implies the R204 table used at the R230 cap | `VERIFIED` |
| S7 orbit coverage for k20 through k13 | `VERIFIED` |
| exact leaf-stripping forcing layer | `VERIFIED` |
| 830 k>=14 and 472 k=13 CNF recipe hashes | `VERIFIED` (formula identity only) |
| exact Gram spectral base identities | `VERIFIED` |
| any dense-residual UNSAT claim | `UNKNOWN` |
| R230 Paley-perfect cap UNSAT | `UNKNOWN` |
| author's no-root-with-k>=14-C4 claim | `UNKNOWN` |
| author's k=13 extension | `UNKNOWN` |
| Conway-99 existence/nonexistence | `UNKNOWN` |
| `n3=708` | `UNKNOWN` |
| external result imported | `NONE` |

This is narrower than the author's "k>=14 fully proof-checked and
reproducible from this tree" statement. The formulas are reproducible from
this tree; the ladder proofs are not retained in it.

## Input and pin checks

The audit used a clean external clone with LFS smudging disabled. `HEAD`
equalled the pinned commit and `git status --porcelain` was empty. All six
frozen discovery inputs matched the SHA-256 values in
`verification/wave34-external-source-audit-protocol.md`.

The machine-readable checks are in
[`results.json`](results.json). The exact 1,302-row certificate inventory is
in [`certificate-ledger.json`](certificate-ledger.json).

## Exact honest rooted model

Let `r` be any vertex of a hypothetical `srg(99,14,1,2)`.

1. `N(r)` has 14 vertices. For each `x in N(r)`, its degree inside `N(r)` is
   the number of common neighbors of `r,x`, namely `lambda=1`. Hence `N(r)` is
   a perfect matching `7K2`.
2. There are `99-1-14=84` far vertices. Each has exactly `mu=2` local
   neighbors. Those two locals cannot be a matched pair, because a matched
   local pair already has `r` as its unique common neighbor.
3. Conversely, every unmatched local pair has exactly two common neighbors:
   `r` and one far vertex. Thus the 84 far vertices are in bijection with the
   `C(14,2)-7=84` unmatched local pairs.
4. Grouping a far label by the two matched-pair indices it meets gives
   `C(7,2)=21` fibers of four vertices.

Writing `L_i` for the two-local label of far vertex `i`, the honest model is:

```text
far degree:
  sum_{j != i} e_ij = 12

P2, local-far lambda/mu:
  sum_{j != i, x in L_j} e_ij
    = 2 - 1[x in L_i] - 1[mate(x) in L_i]

P3, far-far lambda/mu:
  sum_{z != i,j} e_iz e_jz + e_ij
    = 2 - |L_i intersect L_j|
```

These are exactly the remaining SRG degree/common-neighbor equations after
the root, local matching, and local-incidence labels are fixed. They do not
assume an automorphism or a forced far-edge table.

The tracked `honest_flip_cnf.py` creates an unrestricted Boolean variable for
all `C(84,2)=3486` far pairs and imports only
`local_mate`, `make_labels`, and `overlap` from `root_cell_cpsat.py`.
`forced_free_edge_value` is defined in the helper module but is neither
imported nor called by the honest builder.

Canonical Git-blob hashes:

```text
theorem_k19/scripts/honest_flip_cnf.py
  076a6745c3774ce348307ca9ee6b937687eaaf7908b7cd13d361eea199780411

source/root_cell_cpsat.py
  ca6ecd40b211a9cb39868afb5752f678cbe4a409acc231f674cff82916380f1a
```

These match the hashes embedded in the k20 manifests. A raw Windows checkout
hash differs because Git converts LF to CRLF; the canonical blob does not.

The rebuilt base has:

```text
84 far vertices
3,486 far-edge variables
285,852 product variables
1,375,458 total CNF variables
3,109,092 base clauses
```

The three Tseitin clauses per product encode
`p <-> (e_iz and e_jz)`. PySAT's sequential exact-cardinality encoder was
executed in the isolated audit environment. This audit did not formally
verify the PySAT library itself.

## Retraction boundary and cap bridge

The source correctly retracts the old unconditional claim that the R204
forced-edge table follows at every root. In particular, the cross-fiber
"kernel" was previously an unproved load-bearing assumption.

The surviving SAT ladder does not import that routine. At the **all-21-C4
cap only**, however, the table follows:

- a C4 side edge saturates the relevant P2 quota `=1`, blocking all
  cross-fiber pairs that use the same matched-pair coordinate; and
- if a same-fiber diagonal were present, the other two corners would give it
  two common far neighbors, contradicting P3 for an adjacent pair.

The verifier exhaustively checked all 3,360 ordered cross-intersecting pairs
and all 42 same-fiber diagonals. There were no witness failures. The resulting
far-pair classification is:

```text
84 forced C4 side edges
1,722 forced nonedges
1,680 free disjoint-fiber pairs
```

Thus invoking the conditional R230 cap after the honest ladder has forced all
21 fibers to C4 is a valid bridge. It does **not** restore the retracted global
kernel.

The Gram report says its implementation also avoids R204. Its implementation
and dependency closure are absent from Git, so that code-level claim could not
be independently checked.

## Exact structural replay

### Orbit coverage

For each representative, the verifier generated its complete S7 orbit,
checked that representative orbits were distinct, and summed the orbit sizes.

| rung | exceptional edges | representatives | recomputed total | expected |
|---|---:|---:|---:|---:|
| k20 | 1 | 1 | 21 | `C(21,1)=21` |
| k19 | 2 | 2 | 210 | `C(21,2)=210` |
| k18 | 3 | 5 | 1,330 | `C(21,3)=1,330` |
| k17 | 4 | 10 | 5,985 | `C(21,4)=5,985` |
| k16 | 5 | 21 | 20,349 | `C(21,5)=20,349` |
| k15 | 6 | 41 | 54,264 | `C(21,6)=54,264` |
| k14 | 7 | 65 | 116,280 | `C(21,7)=116,280` |
| k13 | 8 | 97 | 203,490 | `C(21,8)=203,490` |

### Leaf-stripping propagation

For a local vertex `x`, its 12 far neighbors form six pairs inside `N(x)`.
If five incident fibers are already C4, they pair ten of those far vertices,
forcing the remaining two to be adjacent. Repeating this for all four local
coordinates supplies the target fiber's four side edges; P3 then forbids its
two diagonals.

On the exceptional-index graph this is exact leaf stripping. The verifier
replayed it without SAT:

| rung | forcing orbit types | designated targets checked | result |
|---|---:|---:|---|
| k20 | 1 | 1 | all forced |
| k19 | 2 | 4 | all forced |
| k18 | 4 | 12 | all forced |
| k17 | 9 | 9 | all forced |
| k16 | 19 | 19 | all forced |
| k15 | 35 | 35 | all forced |
| k14 | 55 | 55 | all forced |
| k13 | 75 | 75 | all forced |

This verifies the exact Part-A implications. It does not close any Part-B
dense core.

### Exact Gram base

From

```text
A^2 = 12 I - A + 2 J
```

the nonprincipal adjacency eigenvalues are `3,-4`, with multiplicities
`54,44`. The normalized `-4` projector is

```text
G = (27 I - 9 A + J) / 28,
```

so its diagonal, edge, and nonedge inner products are exactly

```text
w0=1, w1=-2/7, w2=1/28.
```

These rational identities were independently re-derived with
`fractions.Fraction`.

## CNF recipe replay versus proof replay

The pinned manifests contain every CNF SHA-256 but not the CNF bodies. Using
the pinned builder and independently assembled unit/non-C4 recipes:

```text
k>=14: 830 / 830 CNF SHA-256 values matched
k=13:  472 / 472 CNF SHA-256 values matched
```

This proves byte-level formula reproducibility. It does not prove that any
formula is UNSAT. The source's aggregate `solve_*_results.txt` and
`residual_verdict.txt` files are author logs, not certificates.

Rung totals and artifact states are in
[`rung-ledger.csv`](rung-ledger.csv):

| rung | part | instances | CNF recipe hashes | CNF bodies | proof bodies | independent UNSAT |
|---|---|---:|---:|---:|---:|---|
| k20 | completion | 6 | 6 matched | 0 | 0 | `UNKNOWN` |
| k19 | completion | 24 | 24 matched | 0 | 0 | `UNKNOWN` |
| k18 | A / B | 72 / 1 | 73 matched | 0 | 0 | `UNKNOWN` |
| k17 | A / B | 54 / 1 | 55 matched | 0 | 0 | `UNKNOWN` |
| k16 | A / B | 114 / 2 | 116 matched | 0 | 0 | `UNKNOWN` |
| k15 | A / B | 210 / 6 | 216 matched | 0 | 0 | `UNKNOWN` |
| k14 | A / B | 330 / 10 | 340 matched | 0 | 0 | `UNKNOWN` |
| k13 | A / B | 450 / 22 | 472 matched | 0 | 0 | `UNKNOWN` |

The precise per-instance hash, claimed format/checker, evidence path, and body
state are in [`certificate-ledger.json`](certificate-ledger.json).

## R230 cap artifacts

R230 is represented by:

```text
24 CNFs:  273,647,640 claimed body bytes
24 DRATs: 986,182,510 claimed body bytes
```

All 48 checkout files are Git LFS pointers. Every pointer OID and declared
size matches `artifacts/large_artifacts_manifest.csv`; all 24 copied solve
logs contain `s UNSATISFIABLE`, and all 24 copied checker logs contain
`s VERIFIED`. Those checks validate metadata and log consistency only.

The bodies were not pulled and no DRAT was checked. R230 UNSAT is therefore
`UNKNOWN` in this audit. Exact per-file sizes and hashes are in
[`r230-lfs-ledger.csv`](r230-lfs-ledger.csv).

## Gram/Euclidean certificate availability

The report claims exact-rational certificates for 14 of the 20 historical
dense residuals:

```text
k18: triangle
k16: C5, K4-e
k15: res0, res2, res4
k14: res0, res2, res3, res4, res5, res7, res8, res9
```

It places the certificates, generator, and standalone checker under ignored
`scratchpad/ladder/psd_screen/`. That directory has no tracked files at the
pinned commit. The report provides neither certificate filenames nor
certificate SHA-256 values. Consequently:

```text
claimed:  14
available: 0
replayed:  0
status:    UNKNOWN
```

See [`gram-certificate-ledger.json`](gram-certificate-ledger.json).

## Six non-Gram cores

These are the six cases for which the report retains only the SAT proof route.
The CNF recipe hash was reconstructed in every case, but the CNF and proof
bodies are absent. None of these six is an LFS pointer and none was checked in
this audit.

| rung/core | CNF SHA-256 | claimed proof/checker | body at pin | evidence seen | status |
|---|---|---|---|---|---|
| k17 C4-cycle | `360c3c52beb74b3a22d08f1e9855831e117d693fb9019ab103934fc211532605` | 524 MB DRAT / `drat-trim` | missing | author prose log | `UNKNOWN` |
| k15 K4 | `f8f45562c5f622a4b6f81d1d0257fa2192688bc90b287aee11c1c7ca6028e3ba` | DRAT / `drat-trim` | missing | author prose log | `UNKNOWN` |
| k15 K2,3 | `360b9405427ed8c00c6f8c654c2b009cf586753627879ed52c844f5460ac1e12` | 22.4 GB LRAT / `cake_lpr` | missing | author prose log | `UNKNOWN` |
| k15 C6 | `cc7af9fcd3631ae5b652bea715a8525c571b8cf0eb34dd1254453d0df8d0d4a0` | DRAT / `drat-trim` | missing | author prose log | `UNKNOWN` |
| k14 res1 | `f9aa0084680978b2e62f98960286c97169b9de1e6d644359143acdbf7029960f` | approx. 28 GB LRAT / `cake_lpr` | missing | author prose log | `UNKNOWN` |
| k14 res6 | `25824aa8c44331283bbd574b68d614740388248379102bab0f7bb24541ebc62b` | LRAT / `cake_lpr` | missing | author prose log | `UNKNOWN` |

The source also retracts earlier corroboration by its bundled `lrat-check`,
which it found unsound. This audit does not use that checker.

See [`six-non-gram-cores.json`](six-non-gram-cores.json).

## k=13 kept separate

The k=13 orbit split and all 472 formula hashes reconstruct exactly, and all
75 Part-A targets pass exact leaf stripping.

The 22 Part-B UNSAT claims do not replay from this pin. The source describes:

- 13 residuals with a retained `cake_lpr` log in an ignored working area;
- 8 residuals with a retained multi-GB LRAT body in an ignored working area;
  and
- `res1` with only a cloud verdict and no retained body.

None of those proof bodies is in the pinned Git tree. In particular:

```text
k13_res1.cnf SHA-256:
27d2372bce1f5f9d1a932d86969ab81e7b101df3969872cfc3ac8ce8d85cfe22

recipe reconstruction: VERIFIED
UNSAT proof replay:    UNKNOWN
```

The k=13 theorem remains `UNKNOWN`.

## Environment and exact commands

Environment:

```text
OS:          Microsoft Windows 10.0.26200, x64
Python:      3.13.14
python-sat:  1.9.dev7
OR-Tools:    9.15.6755
Git:         2.51.0.windows.1
Git LFS:     3.7.0
CaDiCaL:     not on PATH
drat-trim:   not on PATH
cake_lpr:    not on PATH
lrat-check:  not on PATH
```

External clone:

```powershell
$auditClone = Join-Path $env:TEMP "wave34-harrison-e2"
$auditVenv = Join-Path $env:TEMP "wave34-harrison-e2-venv"
$repoRoot = (Get-Location).Path
$env:GIT_LFS_SKIP_SMUDGE='1'
git clone --no-checkout `
  https://github.com/harrisonpedrero/conway-99-graph.git `
  $auditClone
git -C $auditClone `
  checkout --detach 26b36c540611fa02c95a5a4bd78cd4a582257195
git -C $auditClone `
  rev-parse HEAD
git -C $auditClone `
  lfs ls-files -l
```

Isolated dependencies and source-provided checks:

```powershell
python -m venv $auditVenv
& (Join-Path $auditVenv "Scripts\python.exe") `
  -m pip install python-sat ortools

python scripts/verify_bundle_metadata.py

& (Join-Path $auditVenv "Scripts\python.exe") `
  theorem_k19\scripts\rebuild_and_verify.py
```

The metadata check printed `ok=true`, `reps=24`, `unsatCount=24`,
`verifiedCount=24`. The source reproducer printed:

```text
MATCH=830 MISMATCH=0 SKIPPED=0
PASS
```

Verifier-owned replay:

```powershell
& (Join-Path $auditVenv "Scripts\python.exe") `
  (Join-Path $repoRoot "verification\wave34-external-source-audit\harrison\verify_harrison_source.py") `
  --clone $auditClone `
  --workspace $repoRoot
```

It returned `ok=true` for the pin, inputs, bridge, exact structural replay,
and recipe hashes while preserving R230, k>=14, and k=13 as `UNKNOWN`.

The first audit release serialized the replay wall-clock duration in
`results.json`, so an orchestrator rerun changed its SHA-256 despite identical
mathematical fields. The public
[`reproducibility correction`](reproducibility-correction.md) preserves that
failure. After removing only the nondeterministic timing field, two exact
isolated-venv reruns both returned `ok=true` and produced identical
`results.json` SHA-256
`0d9ea150bb86e33c00f46e72620dec61e0a2b84c130597596299d80ab8e8baf2`.

## Failed or unavailable commands

The tracked builder is not directly runnable as documented:

```powershell
& (Join-Path $auditVenv "Scripts\python.exe") `
  theorem_k19\scripts\honest_flip_cnf.py
```

It fails with:

```text
ModuleNotFoundError: No module named 'source'
```

`honest_flip_cnf.py` inserts `theorem_k19` rather than the bundle root in
`sys.path`. `rebuild_and_verify.py` repairs that path before importing it, so
the 830-recipe replay still succeeds. This is a standalone-entry-point defect,
not formula drift.

The exact-rational certificate replay was unavailable because the
certificates and checker are absent. SAT/DRAT/LRAT replay was not attempted
because the ladder proof bodies are absent, the R230 bodies are unpulled LFS
pointers, and the protocol forbids acquiring very large bodies merely to turn
an honest `UNKNOWN` into a local check.

## Strongest independently replayed statement

For any arbitrary root of any `srg(99,14,1,2)`, the honest rooted equations,
the 21-fiber representation, the S7 orbit partitions, and the exact
leaf-stripping implications used in every Part-A case through k=13 are valid.
If all 21 fibers are C4, the conditional R204 table used by R230 follows.

No complete exclusion rung is independently replayed from retained proof
bodies at the pinned commit. Nothing here changes the status of Conway-99,
`n3=708`, or any unrestricted Wave 34 track.
