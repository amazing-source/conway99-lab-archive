# Wave 27 detached clean-clone replay

Date: 2026-07-24

Verdict: **PASS**

Integration commit:
`4a2f65d20f8fa403a3a245815799070cf126173f`

Public baseline:
`2ac11809fafee7ab752965ae49a96e922859b5ee`

The replay used a new no-hardlink clone of the local repository, checked out
the integration commit in detached-HEAD state, and wrote all regenerated
artifacts outside the clone. No dependency, solver, network, or mutable cache
was used by the mathematical checkers.

## Mathematical suites

All seven Wave 27 suites passed:

| package | tests |
|---|---:|
| submitted A2-direct-summand-free construction | 15 |
| independent A2-direct-summand-free verifier | 16 |
| submitted unrestricted E6 trace theorem | 16 |
| independent unrestricted E6 trace verifier | 21 |
| submitted general-root tensor screen | 17 |
| submitted A20 trace addendum | 8 |
| independent tensor/A20 verifier | 23 |
| **total** | **116** |

The detached replay independently reached the already frozen scope:

```text
abstract E8^4 orthogonal-sum E6^2 arithmetic package: exact
unrestricted local E6 trace minimum: 14
orthogonal E6 frame/Schur cubic floor: 24 > complement cap 22
orthogonal A6 frame/Schur cubic floor: 66 > global trace 60
core full-ADE survivor: A20 orthogonal-sum E8^3
later A20 floor: 42 + complement 24 = 66 > 60
full orthogonal ADE endpoint form: conditionally impossible
general even rank-44 form / n3=708 / Conway-99 / novelty: UNKNOWN
```

## Deterministic regeneration

Seven checker entry points wrote fresh JSON files to a unique system-temporary
directory. Each output was compared byte for byte with its tracked
counterpart:

```text
attempts/wave27-a2free-construction/exact-results.json
verification/wave27-a2free-construction/independent-results.json
attempts/wave27-h9-classification/exact-results.json
verification/wave27-h9-classification/independent-results.json
attempts/wave27-general-root-tensor/exact-results.json
attempts/wave27-a20-trace-addendum/exact-results.json
verification/wave27-general-root-tensor/independent-results.json
```

All seven comparisons passed.

## Manifest and central-ledger gates

The replay verified all 51 entries in these six manifests:

```text
attempts/wave27-general-root-tensor/artifact-manifest.sha256
attempts/wave27-a20-trace-addendum/artifact-manifest.sha256
verification/wave27-a2free-construction/artifact-manifest.sha256
verification/wave27-h9-classification/artifact-manifest.sha256
verification/wave27-general-root-tensor/artifact-manifest.sha256
verification/wave27-literature-audit/artifact-manifest.sha256
```

The central metadata checks also passed:

```text
claims:                         65 unique
obligations:                    59 unique
status path/SHA-256 pairs:     211 matching
scoped local Markdown links:   205 resolving
central BibTeX keys:            52 unique
Wave 27 and central LF files:   81 with no CR byte
missing ledger evidence paths:   0
```

The status wall remained exact:

```text
project_status: EXPLORATORY
resolution_claim: NONE
target_result: UNKNOWN
conditional_n3_lower_bound: 708
n3_708_excluded: false
novelty_status: UNKNOWN
```

## Exact-blob privacy gate

The privacy check inspected archive bytes rather than only worktree text.
It scanned:

```text
HEAD release tree:       761 files, 11,937,434 bytes
unpublished range:         7 commits
range object census:     110 objects
new blob census:          77 blobs, 1,644,740 bytes
```

The scan searched for OpenAI and GitHub credential shapes, GitHub fine-grained
tokens, AWS access-key shapes, private-key headers, the local Windows user
path, and the local OneDrive workspace path. It found zero matches in both
the exact release archive and every new blob reachable from
`2ac11809fafee7ab752965ae49a96e922859b5ee..4a2f65d20f8fa403a3a245815799070cf126173f`.

## Repository integrity

`git status --porcelain=v1` was empty after all tests and regenerations.
`git fsck --full --strict` returned exit code zero. Because the source clone
copied the source object's unreachable history, `git fsck` listed pre-existing
dangling objects; it reported no corrupt, missing, or invalid reachable
object.

## Retained release-check correction

The first metadata-gate script was too narrow about manifest syntax and too
broad about file selection:

1. it accepted only the local two-space SHA-256 format, while four already
   frozen manifests use repository-relative paths and two discovery manifests
   use the standard binary `*path` marker;
2. it tested whether the absolute path contained `wave27`, which selected the
   entire clone because the temporary clone directory itself contained that
   string; and
3. its whole-repository Markdown regex mistook two historical parenthesized
   formulas for links.

That invocation failed closed and promoted no result. The corrected checker
accepts both manifest encodings, resolves a member first from the repository
root and then from the manifest directory, selects LF files by repository-
relative path, and scopes link checks to the changed central/Wave 27
documents. The corrected invocation produced the passing counts above.

## Scope

This replay verifies reproducibility and publication hygiene for the scoped
Wave 27 claims. It does not broaden them. In particular, the full-ADE
conclusion requires `n3=708`, the full projector/Schur endpoint identities,
and the additional hypothesis that the entire scaled-dual form is an
orthogonal sum of irreducible ADE root lattices. General glued, non-root, and
otherwise nonorthogonal rank-44 lattices remain unclassified. The endpoint,
Conway-99 existence, and novelty remain `UNKNOWN`.
