# Wave 33 detached clean-clone replay

Date: 2026-07-24

Verdict: **PASS**

Exact detached integration commit:
`66790bc326a6a8161567a2c2b5c32ed3cbffd279`

Integration tree:
`487a777bddadf29ecd60b89e631df5c713087e83`

Public Wave 32 baseline:
`b2595baa40d50e9c259051751fe27090bee6a449`

Wave 33 discovery commit:
`69916bc75b0ffd35948bc1e874e6a8aa554e40f1`

Independent-verification commit:
`c79d8442266ca66e167112d38050b3c3521825b5`

Clone-independent chronology repair:
`d3780b1c15c1ffbfb3cae8a7f1190325be8620a7`

The replay used a new clone with local-clone optimization and hardlinks
disabled. The exact integration commit was checked out in detached-HEAD
state. The source and clone `README.md` bytes had identical SHA-256
`53e657397ec7f0339191a5563f7640a8151b783605b63d4ba3ca4327b954e849`,
distinct NTFS file identifiers, and one hardlink path each. The clone had no
object alternates and no `.venv`. All regenerated outputs were written
outside the checkout.

Runtime:

```text
Python 3.13.14
Windows PowerShell 5.1.26100.8875
Git 2.51.0.windows.1
```

## Retained first-clone failure and v2 boundary

Chronology v1 at integration `74c3725a4c18e11a37e3f4bd56b82d47b09dc167`
incorrectly required six ignored local solver-environment files. Its first
detached clone failed on the absent `.venv/Lib/site-packages/pysat/card.py`
after the other 110 live-input tests had passed. The exact path and count are
documentary because the original console transcript is not bundled.

V2 bundles no solver file, opens no local environment file, and observes no
environment hash. It runs all 14 unchanged construction discovery tests and
36 of the 37 unchanged construction verifier tests. The sole omitted
composite test is named exactly; its portable standard-library source half
passes separately, while its solver-environment half is
`NOT_REPLAYED_NONBLOCKING`. The unchanged comparison CLI is
`NOT_RUN_BY_DESIGN`.

## Mathematical suites

The exact integration tree passed:

| package | outer tests |
|---|---:|
| rooted discovery | 15 |
| rootless discovery | 14 |
| independent rooted verifier | 33 |
| independent rootless verifier | 48 |
| construction chronology v2 | 20 |
| **outer total** | **130** |

The chronology run separately executes 50 unchanged original construction
cases: 14 discovery plus 36 verifier. The portable source-provenance gate
also passes. Thus the clean-clone-independent procedure reproduces 160 of the
161 tests recorded across the original historical package runs; only the
nonportable solver-environment composite is not rerun as a whole. The outer
20 and embedded 50 are distinct accounting layers.

## Deterministic regeneration

Eight externally written outputs matched the committed accepted bytes:

| result | SHA-256 |
|---|---|
| rooted discovery | `193db8ee0c155cc3a97489b4471c4a82ae09823dd9344d043a81778e1a6ba5a1` |
| rootless discovery | `2cfb576f2deba7bb82c60eb27c72a62c913d06f2d86f3eb626dcddd6ac75afeb` |
| hostile partial O-Q design | `340e5df716ad63bceba25c745ab04c22ea1a3dca01e939072f09775a5fc5f634` |
| rooted independent reconstruction | `66cef570dbbb4a86e2a35f780edcfc1873d0ac2c5266f1c2065c902a8f91e778` |
| rooted static comparison | `2e36ecade28bca12d35a963a8c6b52777ac7d766a3c4b3267774000fe2e929fd` |
| rootless independent reconstruction | `68911c124a039b32b2eb5fe4c1f9886c033e17129b8b97d7a428c4bda7968253` |
| rootless static comparison | `8b7b27fd67f12bb82cb6eebf645d0c46324d7227e51bdeb0093fbcdf9d753872` |
| construction chronology v2 | `b2f0b872221a3fd9f41d6a88637be21034b70e8c8129fe57617115548b425957` |

The chronology additionally authenticates the historical-input archive at
`d62fc4311577d56cbf34f8bd4e63aefb3b796457b3d020f4322324073d82f7dd`
and the clean comparison projection at
`446beb4ddd2a51194315954d7005cb01d90ff8643a64c78801d93524d65e7818`.

## Manifest and central-ledger gates

All 80 entries in the eight Wave 33 manifests validated:

| package | entries | manifest SHA-256 |
|---|---:|---|
| rooted discovery | 8 | `153860d39fe7274a2f55ee952bcad1135cf4134ccc36d9aec07f6da379c5ca04` |
| rootless discovery | 8 | `384081a967153059399b4e0724e901ef28183cedab8d7e253e45af560e16df95` |
| rooted construction discovery | 16 | `0cd192c0182506b3c901806cc96abb9fe53f04dc906b0b5cd73bc9b602558ff4` |
| rooted precomparison verifier | 8 | `a0cd7d284a23aba5576f2da2a1282c9acb209953c3da5d01e706d793f61d3ea7` |
| rooted comparison verifier | 6 | `50571e1870b7fafb245e2eaf79f8331a3b5d6c7cbd282a8bd2d8937b44898f76` |
| rootless verifier | 13 | `e51811d3dd5a35d21a1e6c7f88625b9dfdabdd1097de1898f988b40747e82822` |
| rooted construction verifier | 14 | `20c27560bdf9720cd1cf043b11c218130cd2891a2d3c874f9dbc9bce2f27fbbf` |
| construction chronology v2 | 7 | `22cbb94ad5a452e9e9c3f38ac35bb31f0b5d2cf81446d0aab5827c3d30b84f69` |

The central and repository checks passed:

```text
claims:                              84 unique
obligations:                         79 unique
claim evidence references:         758 resolving
obligation evidence references:    764 resolving
status path/SHA-256 pairs:          401 matching
Wave 33 status path/hash pairs:      24 matching
tracked Markdown files:             351 checked
local Markdown links:               358 resolving
strict Wave 33 JSON files:           15 checked
Wave 33 release-diff files:         102 UTF-8, LF-only, NUL-free
```

All YAML used a safe duplicate-key-rejecting loader. Every evidence path
existed. Every changed text file had a terminal LF and no CR, NUL, invalid
UTF-8, trailing whitespace, or `git diff --check` finding.

The status wall remained:

```text
project status: EXPLORATORY
resolution claim: NONE
target result: UNKNOWN
conditional n3 lower bound: 708
n3=708 excluded: false
rooted graph-extension criterion: VERIFIED scoped
binary rooted criterion solution or exclusion: UNKNOWN
rooted full endpoint: UNKNOWN
rootless formal contraction boundary: VERIFIED scoped
rootless global motif forcing or avoidance: UNKNOWN
rootless indecomposable endpoint: UNKNOWN
Conway-99 and novelty: UNKNOWN
```

## Exact-blob privacy gate

The privacy gate read the exact tracked archive and every new blob in the
unpublished range:

```text
integration release tree:  1,083 files, 16,556,943 bytes
Wave 33 release diff:         102 files,  1,566,649 current bytes
unpublished range:              5 commits
range object census:          146 objects
  commits:                       5
  trees:                        23
  blobs:                       118
new blob census:              118 blobs, 2,341,793 bytes
largest new blob:             144,762 bytes
largest tracked blob:         654,824 bytes
```

The scan checked the complete integration tree, all 118 new blobs, and all
five commit messages for OpenAI and GitHub token shapes, AWS access-key
shapes, private-key headers, bearer-token shapes, and local user paths.
It found zero actionable matches.

Four exact-object matches were known hostile privacy fixtures: three
tree/history occurrences of `C:\Users\RESEARCHER\STRUCTURE.md` in the Wave 33
chronology tests and one pre-existing split `/home/researcher fixture in a Wave 23
privacy test. No real user path or credential was present. No tracked PDF,
HTML, archive, executable, shared-library, or office-document payload was
present.

## Repository integrity

The detached clone had a clean status and no `__pycache__`. The full
unpublished-range `git diff --check` returned success.
`git fsck --full --strict` returned exit code zero with no output. The checked
tree object was `487a777bddadf29ecd60b89e631df5c713087e83`.

## Scope

This replay verifies reproducibility and publication hygiene for the scoped
Wave 33 rooted graph-extension criterion, its forced finite invariants, the
hostile one-design O-Q certificate, the formal rootless contraction null
trade, and the actual R2 incidence board.

It does not provide a binary rooted solution or exclusion, an O-O layer, a
complete-domain UNSAT certificate, global rootless motif forcing or
avoidance, an endpoint realization, an `n3=708` exclusion, a stronger bound,
a construction or nonexistence proof for the target graph, a Conway-99
resolution, or a novelty result. All broader statuses remain `UNKNOWN` or
`NONE`.
