# Wave 31 detached clean-clone replay

Date: 2026-07-24

Verdict: **PASS**

Integration commit:
`f591e756ca8cca179ee35b511bb61d720dcbc42d`

Public Wave 30 baseline:
`5652578111999645a9d5427d0716053de79e0902`

Integration tree:
`9db5a8df2fde0aa011812a96de976f9ef56e2b61`

The replay used a new clone with local-clone optimization and hardlinks
disabled. The exact integration commit was checked in detached-HEAD state.
The source and clone `README.md` bytes had identical SHA-256 values, distinct
NTFS file identifiers, and one hardlink path each. All regenerated outputs
were written outside the clone checkout.

Runtime:

```text
Python 3.13.14
Windows PowerShell 5.1.26100.8875
Git 2.51.0.windows.1
```

## Mathematical suites

The exact integration tree passed:

| package | tests |
|---|---:|
| sign-commutant proof discovery | 15 |
| primary independent sign verifier | 21 |
| T20 finite-search discovery | 10 |
| independent T20 finite verifier | 11 |
| **total** | **57** |

The separate skeptical sign checker also returned
`PASS_NO_FATAL_GAP`. It is not counted as a unit-test suite and does not
replace the designated verifier.

No zero-test invocation was accepted. The historically retained
wrong-directory harness failures are documented in the Wave 31 correction
ledger and were not repeated as evidence.

## Deterministic regeneration

Five independently invoked generators matched the committed accepted bytes:

| result | SHA-256 |
|---|---|
| sign proof discovery | `e5155e67a59168767639273ee70fc6d63e81b104e9b415e228ca09a0f9317587` |
| primary sign verifier | `7143c403172403b21ea2cdc2851851a3a13cb08b0dd14e5d68432aafd25fc5c0` |
| skeptical sign checker | `0dd057b903da3092528f4e0bc2b9283e8ee6fa3222553b24b219dda732d35007` |
| T20 finite-search discovery | `d2592a71e8600a894aa7d87e6ed1c8230010b919488b10f9854710bb77944152` |
| independent T20 verifier | `ac6c34e1f8c1ba98d12d5d01e9d8b05e7a60a51a76b5701c528912f94ab3bede` |

The proof output also matched
`verification/wave31-sign-commutant/submitted-regenerated.json` byte for
byte. The skeptical generator was run twice and produced the same digest.

The proof, primary-sign, T20-discovery, and T20-verifier JSON files contain
dynamic runtime metadata. Literal byte identity is certified for the pinned
replay environment above. A replay on another OS or Python build must compare
the exact mathematical fields separately from those runtime fields.

## Manifest and central-ledger gates

All 42 entries in the six Wave 31 manifests validated:

| package | entries | manifest SHA-256 |
|---|---:|---|
| sign proof discovery | 7 | `c1d3b8d2a2ca25c4dcdb20fbc1d974f1561fa7c110524359443161d79bebd7f6` |
| literature audit | 6 | `ccbc52b0089484b153251fe4c37759d49618c59a78e449c61dde122e64465d25` |
| T20 finite discovery | 8 | `972640b51dd31dc6037ae26b676d1f7c39626f25d038606a71bf18728e9ea3d4` |
| primary sign verifier | 8 | `e91d4ec72d7921688700bdc5e68b1e610db1d031b1ec7ffae9b927ecd4494122` |
| skeptical sign verifier | 5 | `c9dd19b9df24e22bcfff7533bb0251582c737153dbbe9ad28e8ea23f2085c1c0` |
| independent T20 verifier | 8 | `73072c577eff876b4799455a6e0ea0080e54f5370ed8790eda6b85fe3687e1bb` |

The central and repository checks passed:

```text
claims:                              77 unique
obligations:                         71 unique
claim/obligation evidence refs:   1,331 resolving
status path/SHA-256 pairs:          360 matching
Wave 31 status path/hash pairs:      50 matching
SOURCES.bib intrinsic digest:         1 matching
central BibTeX keys:                 87 unique
retained Wave 31 source records:     14 covered
tracked Markdown files:             308 checked
local Markdown links:               312 resolving with exact case
Wave 31 release-diff files:          59 UTF-8, LF-only, NUL-free
```

All YAML used a duplicate-key-rejecting loader. Every evidence path existed.
Every changed text file had a terminal LF and no CR, NUL, invalid UTF-8,
trailing whitespace, or `git diff --check` finding.

The status wall remained:

```text
project_status: EXPLORATORY
resolution_claim: NONE
target_result: UNKNOWN
conditional_n3_lower_bound: 708
n3_708_excluded: false
determinant_rows_excluded: 0
rootless integrally decomposable actual-incidence endpoint:
  VERIFIED_IMPOSSIBLE
T20 matrix-only coupled frame/Schur package: UNKNOWN
rooted endpoint forms: UNKNOWN
rootless integrally indecomposable endpoint forms: UNKNOWN
Conway-99 and novelty: UNKNOWN
```

## Exact-blob privacy gate

The privacy gate read exact tracked and Git-object bytes. It scanned:

```text
integration release tree:   938 files, 15,181,325 bytes
unpublished range:            6 commits
range object census:         86 objects
  commits:                    6
  trees:                     22
  blobs:                     58
new blob census:             58 blobs, 1,737,482 bytes
```

The unpublished range was
`5652578111999645a9d5427d0716053de79e0902..f591e756ca8cca179ee35b511bb61d720dcbc42d`.
The scan checked the complete integration tree, every new blob, and all six
commit messages for GitHub and OpenAI token shapes, AWS access-key shapes,
private-key headers, credential assignments, and local Windows or Unix user
paths. It found zero matches.

No tracked PDF, HTML, archive, or office-document payload was present. No
blob exceeded 5 MiB. The largest tracked file was the pre-existing structured
Wave 28 simultaneous-neighbor result at 654,824 bytes.

## Repository integrity

The detached clone had a clean status. Both worktree/index diff checks and
the full unpublished-range `git diff --check` returned success.
`git fsck --full --strict` returned exit code zero with no output. The
checked tree object was
`9db5a8df2fde0aa011812a96de976f9ef56e2b61`.

## Operational corrections

One source-checkout preflight left `HEAD^{tree}` unquoted. Windows
PowerShell mangled only that tree-peel argument after clean status and the
head commit had already been printed. The failed wrapper was discarded; a
quoted rerun returned the tree object above.

An earlier temporary-directory setup used an unsupported `New-Item
-LiteralPath` option and created no directory. The setup was rerun with the
supported `-Path` option before any generator or test. Neither wrapper error
produced evidence or changed a tracked file.

## Scope

This replay verifies reproducibility and publication hygiene for:

1. the scoped conditional theorem excluding every nontrivial rootless
   integral orthogonal decomposition under actual target incidence;
2. the independently verified exact T20 finite shell, rational relaxation,
   cap-one restriction, named radius-two nonhit, and conditional trace
   transfer; and
3. the bounded Wave 31 source/status audit.

It does not classify rooted or rootless integrally indecomposable endpoint
forms, exclude a determinant row or `n3=708`, improve `n3>=708`, construct or
exclude the target graph, resolve Conway-99, or establish novelty or
priority. All broader statuses remain `UNKNOWN`.
