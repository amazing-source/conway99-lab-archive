# Wave 28 detached clean-clone replay

Date: 2026-07-24

Verdict: **PASS**

Integration commit:
`4c4d2cb8dec14c7834984d47a7e5b29991891e60`

Public baseline:
`d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b`

The replay used a new `--no-hardlinks` local clone, checked out the
integration commit in detached-HEAD state, and wrote every regenerated result
outside the clone. The copied integration-commit object had a different file
identifier from the source object, and its hardlink list contained only the
clone path. The mathematical replay was offline.

Runtime:

```text
Python 3.13.14
Windows PowerShell 5.1.26100.8875
```

## Mathematical suites

All five Wave 28 suites passed:

| package | tests |
|---|---:|
| submitted glue/discriminant reduction | 13 |
| submitted theta/modular reduction | 14 |
| independent glue/discriminant verifier | 16 |
| independent theta/modular verifier | 20 |
| independent simultaneous-neighbor verifier | 25 |
| **total** | **88** |

The replay retained the exact scope wall:

```text
corrected necessary glue/theta restrictions: VERIFIED
rootless bare S/G control: VERIFIED
two abstract simultaneous-neighbor controls: VERIFIED
full X/M/W/Q/B endpoint package: UNKNOWN
n3=708 / Conway-99 / novelty: UNKNOWN
```

## Deterministic regeneration

Five entry points wrote fresh JSON files to a unique system-temporary
directory. Each result was compared byte for byte with its tracked
counterpart:

| tracked result | SHA-256 |
|---|---|
| `attempts/wave28-glue-discriminant/exact-results.json` | `13a3bb8f83c56ff899991362736089b772114cff840a2cb20d68845e231b3cf1` |
| `attempts/wave28-theta-modular/exact-results.json` | `9d7b1ffcc0cef2441aa6dd381228abaa1018f721594e930cdd7227c0647470d6` |
| `verification/wave28-glue-discriminant/independent-results.json` | `0d15724c772300072c565030e88080c05333af8f75241b633d5801e5c4ac83fe` |
| `verification/wave28-theta-modular/independent-results.json` | `24298ae282c7baa252a39ffe96fc37b7c696cb51f14b9ddea2318a59b4335b7f` |
| `verification/wave28-simultaneous-neighbor/independent-results.json` | `d9f6829dc967fb3777f541b4fd16cd27acb3478d96479b8ad9c3e9fbad2afedd` |

All five comparisons passed. The independent theta replay again visited
15,053,011 closed-ellipsoid nodes and returned
`K12_r4=756`, `LAMBDA(F)_r4=146880`, and `S0_r4=147636`.

## Manifest and central-ledger gates

All 46 entries in the six Wave 28 manifests validated:

```text
attempts/wave28-glue-discriminant/artifact-manifest.sha256
attempts/wave28-theta-modular/artifact-manifest.sha256
verification/wave28-glue-discriminant/artifact-manifest.sha256
verification/wave28-theta-modular/artifact-manifest.sha256
verification/wave28-simultaneous-neighbor/artifact-manifest.sha256
verification/wave28-literature-audit/artifact-manifest.sha256
```

The central and repository checks also passed:

```text
claims:                              69 unique
obligations:                         63 unique
claim/obligation evidence paths:      0 missing
status path/SHA-256 pairs:           245 matching
central BibTeX keys:                  69 unique
retained Wave 28 source records:      17 covered
tracked Markdown files:              266 checked
local Markdown links:                246 resolving
Wave 28 and central LF files:          64 LF-only and NUL-free
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
HEAD release tree:       817 files, 13,189,442 bytes
unpublished range:         7 commits
range object census:     100 objects
new blob census:          66 blobs, 1,733,924 bytes
```

The unpublished range was
`d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b..4c4d2cb8dec14c7834984d47a7e5b29991891e60`.
The scan checked both the full release tree and every new blob, including
transient or later-replaced blobs in the range, for OpenAI and GitHub token
shapes, AWS access-key shapes, private-key headers, credentialed URLs, and
local Windows or Unix user paths. It also scanned the seven commit messages.
It found zero matches.

No tracked PDF, HTML, archive, or office-document payload was present. No blob
exceeded 5 MB. The largest release blob was the structured exact numeric
neighbor result at 654,824 bytes.

## Repository integrity

`git status --porcelain=v1` and `git diff --check` were empty after all tests
and out-of-tree regenerations. `git fsck --full --strict` returned exit code
zero. Because the no-hardlink clone copied the source object's unreachable
history, `git fsck` listed pre-existing dangling objects; it reported no
corrupt, missing, or invalid reachable object.

## Retained publication-gate corrections

Three failed-closed packaging defects were corrected before this replay:

1. the first documented byte comparison used the PowerShell-invalid generic
   call `SequenceEqual[byte](...)`; the PowerShell 5.1-compatible overload
   call now parses and detects both equality and an intentional mismatch;
2. the first central bibliography pass omitted six retained Wave 28 records;
   all 17 audit records are now represented, with the missing primary and
   nearby sources added; and
3. the first manifest validator treated every slash-containing member as
   repository-relative, while the literature manifest contains
   manifest-relative `sources/...` members. The corrected gate tests the
   repository root and then the manifest directory; and
4. the final unpublished-range `git diff --check` found three Markdown
   hard-break spaces in the literature audit. They were normalized, and the
   dependent audit, run-report, manifest, reproduction, and status hashes were
   repaired without changing any source or mathematical conclusion.

One preliminary asynchronous generator wrapper completed the exact theta
enumeration but exited without its orchestration sentinel before the neighbor
generator. Those temporary outputs were discarded and were not used as
evidence. The detached replay above reran all five generators and passed.

## Scope

This replay verifies reproducibility and publication hygiene for the scoped
Wave 28 claims. It does not classify all even positive-definite rank-44
lattices satisfying the scaled-dual condition, construct the marked
231-vector endpoint frame, prove the full projector/Schur origin for any
control, exclude a determinant row or `n3=708`, improve `n3>=708`, construct a
graph, resolve Conway-99, or establish novelty. All of those broader statuses
remain `UNKNOWN`.
