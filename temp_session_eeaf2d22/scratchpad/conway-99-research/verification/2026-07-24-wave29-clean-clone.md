# Wave 29 detached clean-clone replay

Date: 2026-07-24

Verdict: **PASS**

Integration commit:
`ae8fd70baaeb35302f957653e20ad710e5e77281`

Public baseline:
`aadc0dafce387233fc16406cc9822f069becd645`

The replay used a new `--no-hardlinks` local clone, checked out the
integration commit in detached-HEAD state, and wrote regenerated results
outside the clone. The source and clone copies of the integration-commit
object had identical SHA-256 content hashes but different NTFS file
identifiers, and each hardlink list contained only its own path. The
mathematical replay was offline.

Runtime:

```text
Python 3.13.14
Windows PowerShell 5.1.26100.8875
```

## Mathematical suites

Both Wave 29 suites passed:

| package | tests |
|---|---:|
| submitted single-lattice endpoint exclusion | 18 |
| independent hostile verifier | 27 |
| **total** | **45** |

The replay retained the exact scope wall:

```text
S0=K12 orthogonal_sum LAMBDA(F) full endpoint origin: REFUTED (VERIFIED)
every other determinant-729 lattice: UNKNOWN
h=729 row / n3=708 / Conway-99 / novelty: UNKNOWN
```

## Deterministic regeneration

Both entry points wrote fresh JSON files outside the clone. Each result was
compared byte for byte with its tracked counterpart:

| tracked result | SHA-256 |
|---|---|
| `attempts/wave29-s0-frame-exclusion/exact-results.json` | `7a85c5321b5e91365c246dff7bae9264cc82494da5c866b1b351511099f6638c` |
| `verification/wave29-s0-frame-exclusion/independent-results.json` | `c0418cec88915089d6cc2e29735ca3e7bc425cfcd2b3ce09a78a707e36e0aa04` |

Both comparisons passed.

## Manifest and central-ledger gates

All 19 entries in the three Wave 29 manifests validated:

```text
attempts/wave29-s0-frame-exclusion/artifact-manifest.sha256
verification/wave29-s0-frame-exclusion/artifact-manifest.sha256
verification/wave29-s0-literature-audit/artifact-manifest.sha256
```

The central and repository checks also passed:

```text
claims:                              71 unique
obligations:                         65 unique
claim/obligation evidence paths:      0 missing
status path/SHA-256 pairs:           263 matching
central BibTeX keys:                  73 unique
retained Wave 29 source records:      16 covered
tracked Markdown files:              275 checked
local Markdown links:                263 resolving
Wave 29 release-diff files:           32 UTF-8, LF-only, NUL-free
```

The status wall remained exact:

```text
project_status: EXPLORATORY
resolution_claim: NONE
target_result: UNKNOWN
conditional_n3_lower_bound: 708
n3_708_excluded: false
determinant_rows_excluded: 0
novelty_status: UNKNOWN
```

## Exact-blob privacy gate

The privacy check read Git blob bytes, not only worktree text. It scanned:

```text
integration release tree:  841 files, 13,396,726 bytes
unpublished range:           4 commits
range object census:        49 objects
new blob census:            32 blobs, 739,355 bytes
```

The unpublished range was
`aadc0dafce387233fc16406cc9822f069becd645..ae8fd70baaeb35302f957653e20ad710e5e77281`.
The scan checked both the full release tree and every new blob in the range
for OpenAI and GitHub token shapes, AWS access-key shapes, private-key
headers, credentialed URLs, and local Windows or Unix user paths. It also
scanned the four commit messages. It found zero matches.

No tracked PDF, HTML, archive, or office-document payload was present. No
blob exceeded 5 MiB. The largest release blob was the pre-existing structured
Wave 28 simultaneous-neighbor result at 654,824 bytes.

## Repository integrity

`git status --porcelain=v1`, `git diff --check`, and the full unpublished
range `git diff --check` were empty after the replay. `git fsck --full
--strict` returned exit code zero. Because the no-hardlink clone copied the
source object's unreachable local history, `git fsck` listed pre-existing
dangling objects; it reported no corrupt, missing, or invalid reachable
object.

One preliminary exact-blob wrapper timed out because its output pipe filled.
It supplied no evidence and was discarded. The buffered batch implementation
was then run over the complete release tree and unpublished range and produced
the reported passing result.

## Scope

This replay verifies reproducibility and publication hygiene for the scoped
Wave 29 claim. It does not classify other even positive-definite rank-44
lattices satisfying the scaled-dual condition, exclude the determinant-729
row or `n3=708`, improve `n3>=708`, construct a marked 231-vector endpoint
frame or graph, resolve Conway-99, or establish novelty. All broader statuses
remain `UNKNOWN`.
