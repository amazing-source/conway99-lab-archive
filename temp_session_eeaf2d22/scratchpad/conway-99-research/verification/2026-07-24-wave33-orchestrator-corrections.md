# Wave 33 orchestrator corrections and scope ledger

Date: 2026-07-24

Frozen public base:
`b2595baa40d50e9c259051751fe27090bee6a449`

## Status wall

Wave 33 verifies two conditional structural reductions and one finite
construction/search record.  It does not construct or exclude an
`srg(99,14,1,2)`, close either endpoint branch, exclude `n3=708`, improve
the conditional bound `n3>=708`, resolve Conway-99, or establish novelty.

```text
rooted finite graph-extension criterion:                 VERIFIED scoped
binary solution or exclusion of that criterion:          UNKNOWN
rootless local fused-algebra and R2-board reductions:     VERIFIED scoped
actual global mixed-motif forcing or avoidance:           UNKNOWN
restricted one-design MILP timeout:                       NO EVIDENCE
hostile O-Q partial object:                               VERIFIED finite
rooted endpoint / rootless endpoint / n3=708:             UNKNOWN
Conway-99 existence/nonexistence / novelty:               UNKNOWN
```

## Rooted discovery release corrections

The rooted discovery agent first reported a mistyped manifest SHA-256
beginning `17f9...`.  No file byte changed.  The validated manifest is:

```text
153860d39fe7274a2f55ee952bcad1135cf4134ccc36d9aec07f6da379c5ca04
```

The release count was also clarified without changing bytes.  There are
nine candidate paths: one agent report and eight files under
`attempts/wave33-rooted-extension/`.  The inner artifact manifest contains
eight entries because it cannot include its own hash.

The candidate inventory at
`verification/wave33-rooted-extension-candidate-freeze.sha256` contains all
nine paths and has SHA-256
`f10119fecdbd226ca5a89180e2c8663b88c8f7d929ed8a619015070e0f637566`.

The clean-room verifier preserved its eight precomparison files before
candidate release, then used a separate static comparison package.  It found
no material mathematical defect and independently verified the quotient,
simple `2-(15,3,2)` design, all six graph-extension blocks, necessity and
sufficiency, exact induced-70 spectrum, 56 triangles, 294 four-cycles,
determinant `2^32 3^29`, and the hostile `PG(3,2)` design.  No binary
criterion solution or exclusion was obtained.

## Rootless wording qualifier

The literal discovery headline

```text
all two-leg spectral/incidence contractions are locally blind
```

is broader than the checked theorem.  The publication-safe replacement is:

> At a formally allowed `q(T)=q(U)=2` `R2` pair, every bilinear
> `Q[Gamma]` contraction and every contraction of the form
> `N^T p(A) N` is blind to the displayed local null trade.

The candidate already states that its tables are formal local controls, not
a global relation tensor, and excludes uncontracted vertex labels,
three-leg incidence, projector/Schur compatibility, and global overlap from
its conclusion.  The verifier therefore returns
`PASS_SCOPED_WITH_NONBLOCKING_WORDING_QUALIFIER`, not a veto.

The exact actual-incidence statement that survives without qualification is
that every actual `R2` pair has the eight-vertex multiplicity board

```text
[[1,0,1],
 [0,1,1],
 [1,1,2]]
```

and exactly four pair-indexed transversal candidates.  Candidate does not
mean realized triangle.  Whether any candidate must close globally remains
`UNKNOWN`.

## Construction scope and checker coverage

The reproducible MILP encodes all `70!` bijections of one fixed simple
`2-(15,3,2)` design to the 70 labeled support-adjacent outside vertices.
It does not range over all nonisomorphic designs.  Its 25-second
SciPy/HiGHS run returned status 1, no primal, no objective, node count, or
gap, created no output, and never entered the O-O phase.  This timeout has
no positive or negative mathematical status.

The exact hostile certificate supplies only the O-Q layer.  It has:

```text
O row degrees:                    3^70
Q column degrees:                14^15
Q-pair intersections:            2^105
support-point counts:             1^5,2^200,3^5
support/O-Q coupling violations:  10
squared coupling defect:          10
O-O layer:                        UNSUPPLIED
```

Here the discovery construction package writes its fixed `14 x 70`
support incidence as `B` and its `70 x 15` O-Q incidence as `F`, so its
formula is `B F=2J`.  The central exposition uses `F` and `B` respectively,
so the same equation is written `F B=2J`.  No matrix product is being
reversed.

An empty O-O matrix is a verifier hostile control only; it is not a search
restriction and not a claim about the certificate.

The frozen discovery checker validates the arithmetic and rejects top-level
status promotion, but it uses ordinary `json.loads` and does not bind every
scope, evidence-kind, restriction, limitation, and discovery-status field.
The frozen bytes are honestly scoped, and the clean-room verifier supplies
strict duplicate-key rejection and exact metadata/status gates.  These are
recorded nonblocking coverage gaps.

The construction protocol's phrase "complete finite labeled domain" is read
with its pre-search correction ledger: the three block equations are
complete for the labeled graph extension, not for the full rooted endpoint
with projector, lattice, tensor, and Schur conditions.

## Orchestrator replay mistakes

The orchestrator first invoked the construction checker without
`--partial-certificate`.  That valid but wrong command generated the
base-only result in a temporary path with SHA-256
`97f30719cc41bb48c3b562faf5bc7037112cd8cf35c737b3717614217a9c1ea1`.
It did not alter repository bytes.  The correct frozen command regenerated
`exact-results.json` byte-identically at
`ba6640eacd041bc8349024a1d3f13e3d74bd67cdad64d2d78c9a94927319c496`.

The orchestrator later tried the construction-verifier CLIs with an
unsupported `--output` option and, for the precomparison checker, without
its required `--input`.  Both commands exited at argument parsing and
produced no evidence.  In the original live environment only, the documented
invocations then passed:

```text
python -B verification/wave33-rooted-construction/independent_check.py
  --input verification/wave33-rooted-construction/precomparison-fixture.json

python -B verification/wave33-rooted-construction/candidate_comparison.py
  --reproduce-search
```

These are historical commands, not v2 replay commands.  The candidate
comparison CLI is `NOT_RUN_BY_DESIGN` in v2 because it opens ignored local
solver-environment files.

The first replay mistake is also retained in the independent verifier's
`replay-ledger.md`; the second is recorded here because it occurred after
that verifier package was frozen.

## Integrated-root chronology and clean-clone repair

The construction discovery and comparison programs deliberately checked
their frozen input ledgers against live paths.  Their historical
`STRUCTURE.md` input has SHA-256

```text
45640fecaa5834b24063c682c7edd0898f2746253a7708a2c70c3610e4bcb99a.
```

Adding the initial Wave 33 exposition to that mutable central file changed
its then-live hash at defect detection to

```text
bfbdb3db713dd160c1941fd52033aac1d5fe182463b23f5bc47ac7d382393aef.
```

Later central edits may change the live hash again; the historical
`45640f...` input is the invariant.

Direct integrated-root replay then failed closed at the historical hash
gate: the discovery suite reported 12/14 and the comparison verifier 36/37.
Those expected live-path failures are not mathematical failures and are not
accepted reproduction evidence.

No candidate, discovery, precomparison, comparison, or original verifier
byte was changed.  The separate
[construction chronology package](wave33-rooted-construction-chronology/audit.md)
stores and authenticates all eight historical inputs, materializes them with
the hash-pinned original packages in a temporary root.

Chronology v1 passed locally but incorrectly treated six ignored `.venv`
solver-environment files as portable inputs.  The first detached clone of
integration `74c3725`, after 110 live-input tests had passed, failed on the
missing `.venv/Lib/site-packages/pysat/card.py`.  That was a genuine
reproducibility blocker.  The original console transcript is not bundled, so
the exact failure path and count remain documentary audit records.

Chronology v2 bundles no third-party solver files and opens no local
environment paths.  It authenticates the exact original test-ID sets, replays
all 14 discovery tests and 36 of 37 verifier tests, and names the sole omitted
composite case.  Its portable standard-library source-audit half passes
separately.  The solver-environment half depends on ignored local files and
is `NOT_REPLAYED_NONBLOCKING`; v2 opens zero such files and observes zero
environment hashes.  The unchanged comparison CLI is `NOT_RUN_BY_DESIGN`;
chronology-owned code calls only hash-pinned portable functions, core-binds
the accepted summary, and reproduces the hostile certificate byte-for-byte.

Twenty outer hostile tests check archive mutation, duplicate keys and paths,
absolute and parent escapes, symlinks, source mutations, exact test identity,
environment isolation, forbidden entrypoints, status promotion, output
placement, and no-write discipline.  The 20 outer cases and 50 embedded
original cases are separate evidence layers.

```text
historical-input archive:
d62fc4311577d56cbf34f8bd4e63aefb3b796457b3d020f4322324073d82f7dd

chronology result:
b2f0b872221a3fd9f41d6a88637be21034b70e8c8129fe57617115548b425957

chronology comparison projection:
446beb4ddd2a51194315954d7005cb01d90ff8643a64c78801d93524d65e7818

chronology manifest:
22cbb94ad5a452e9e9c3f38ac35bb31f0b5d2cf81446d0aab5827c3d30b84f69
```

Canonical v2 commands:

```powershell
python -B -m unittest discover `
  -s verification/wave33-rooted-construction-chronology `
  -p "test_*.py" -v
python -B verification/wave33-rooted-construction-chronology/chronology_replay.py `
  --output <scratch>/chronology-results.json
```

This is a chronology and reproducibility repair only.  It does not improve
the hostile object or search and changes no mathematical status.

## Manifest and test summary before integration

The three discovery suites pass `15+14+14=43` tests.  The independent
rooted, rootless, and construction verifier stages pass `33+48+37=118`
tests in their historical environments.  Wave 33 therefore recorded 161
passing package tests before repository-wide integration.  The current
cross-run aggregate reproduces 160 portable original cases: 110 live-input
cases plus the v2 minimal-clean-source embedded `14+36=50` replay.  V2 also
passes the portable source half of the omitted composite test.  The
integrated current-tree commands report 130 outer tests: 110 live-input tests
plus 20 chronology tests.  The chronology suite performs the embedded
50-case replay.

Original publication manifests plus the chronology repair:

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

All statements above remain conditional on the independently verified
Wave 32 premises and retain the global `UNKNOWN` wall.
