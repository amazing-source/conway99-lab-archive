# Wave 32 detached clean-clone replay

Date: 2026-07-24

Verdict: **PASS**

Integration commit:
`ad6329f80acb4a1cb6214a7ac2923f8436256b58`

Discovery commit:
`dd3f3fcf692741b51a496233911f46a09cc400e3`

Independent-verification commit:
`a88cfd38805f420bf1717a9513d9c47e12686b19`

Public Wave 31 baseline:
`f0783b82d9b0260f5461cd68c647f62f646cdd81`

Integration tree:
`12fabdda1adc156dcbbc4eb6813a793c9c08f04a`

The replay used a new clone with local-clone optimization and hardlinks
disabled. The exact integration commit was checked in detached-HEAD state.
The source and clone `README.md` bytes had identical SHA-256
`693aac5df77c558f5ad483599bcc691852d2e364ffc1968d240997a0e1454323`,
distinct NTFS file identifiers, and one hardlink path each. The clone had no
object alternates. All regenerated outputs were written outside the checkout.

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
| rooted discovery | 14 |
| independent rooted verifier | 19 |
| indecomposable discovery | 10 |
| independent indecomposable verifier | 19 |
| corrected-byte literature verifier | 17 |
| **total** | **79** |

The rooted and indecomposable verifiers are clean-room implementations. They
do not import or execute the corresponding discovery checker. The literature
verifier freezes and checks the corrected candidate and supporting inputs
byte for byte.

## Deterministic regeneration

Five independently invoked generators matched the committed accepted bytes:

| result | SHA-256 |
|---|---|
| rooted discovery | `9fa31703b5c4721476b1b88f217d7455615c0d92c0d6db7f150abadfc069c2a0` |
| rooted verifier | `4ed239e997e4485abdab4e26a2e28e2a981b6fff069c4d926ccff3d2241dbe6f` |
| indecomposable discovery | `bccde9635d973e030e004800abc08c37089e036faca1edc2bb85ed70ee731472` |
| indecomposable verifier | `4b90ef54358a14abc92c925c8e0f94ed9510b4f80857fde5aa4e2abf4ba89e2a` |
| literature verifier | `f884699b464a8b1b46b63cc15546f01b72c492ae54530750fcf00226b13d913b` |

Every regenerated file was written to a separate temporary directory and
compared byte for byte with its accepted JSON.

## Manifest and central-ledger gates

All 42 entries in the six Wave 32 manifests validated:

| package | entries | manifest SHA-256 |
|---|---:|---|
| rooted discovery | 8 | `ba6c7099e06e24fe2feee4d19021dac9ddf49cbfe99acdd54f905a6c40728b8e` |
| rooted verifier | 7 | `2607c3000944e6d31ab5491a7d959ae4f97f05ac3e0d754baaf2830efcd085df` |
| indecomposable discovery | 7 | `451ca652a83b3a93fd11278c25dafe43bafabc3e06e1cac429064d32211d7138` |
| indecomposable verifier | 8 | `67dd65dd491ef28b4848bbb6c1e0ae47d3814db5b0a466462d7e9f79d5d4d6cd` |
| literature package | 6 | `9bdf458203beb32c76b993af2cb6130641546b5a7816f8bed507661e640173c6` |
| literature verifier | 6 | `b333f77785db6495040e5137b8cc8c9c70f283ed5dfac513ff92f98fd15f6b24` |

The central and repository checks passed:

```text
claims:                              80 unique
obligations:                         75 unique
claim/obligation evidence refs:   1,430 resolving
status path/SHA-256 pairs:          376 matching
Wave 32 status path/hash pairs:      15 matching
central BibTeX keys:                 87 unique
tracked Markdown files:             324 checked
local Markdown links:               337 resolving
Wave 32 release-diff files:          57 UTF-8, LF-only, NUL-free
```

All YAML used a safe loader, and every evidence path existed. Every changed
text file had a terminal LF and no CR, NUL, invalid UTF-8, trailing
whitespace, or `git diff --check` finding.

The status wall remained:

```text
project_status: EXPLORATORY
resolution_claim: NONE
target_result: UNKNOWN
conditional_n3_lower_bound: 708
n3_708_excluded: false
determinant_rows_excluded: 0
rooted necessary Fano-support pattern: VERIFIED scoped
rooted endpoint: UNKNOWN
rootless decomposable actual-incidence endpoint: VERIFIED impossible
rootless indecomposable necessary reductions: VERIFIED scoped
actual incidence forces the forbidden motif: UNKNOWN
rootless indecomposable endpoint: UNKNOWN
Conway-99 and novelty: UNKNOWN
```

## Exact-blob privacy gate

The privacy gate read exact tracked archive bytes and the complete
unpublished object census. It scanned:

```text
integration release tree:   989 files, 15,646,391 bytes
unpublished range:            3 commits
range object census:         74 objects
  commits:                    3
  trees:                     14
  blobs:                     57
new blob census:             57 blobs, 1,076,850 bytes
```

The unpublished range was
`f0783b82d9b0260f5461cd68c647f62f646cdd81..ad6329f80acb4a1cb6214a7ac2923f8436256b58`.
The scan checked the complete integration tree and all three commit messages
for GitHub and OpenAI token shapes, AWS access-key shapes, private-key
headers, bearer-token shapes, and local Windows or Unix user paths. It found
zero matches.

No tracked PDF, HTML, archive, or office-document payload was present. No new
blob exceeded 5 MiB; the largest new blob was 134,661 bytes. The largest
tracked file remained the pre-existing Wave 28 simultaneous-neighbor result
at 654,824 bytes.

## Repository integrity

The detached clone had a clean status. The full unpublished-range
`git diff --check` returned success. `git fsck --full --strict` returned exit
code zero with no output. The checked tree object was
`12fabdda1adc156dcbbc4eb6813a793c9c08f04a`.

## Operational correction

The first combined metadata/privacy wrapper invoked `git cat-file` once for
each tracked object and exceeded its 124-second process timeout before
returning a result. That invocation was discarded and produced no accepted
evidence or tracked changes. The rerun used one archive read plus a batched
object-type query, completed successfully, and supplied all counts above.

## Scope

This replay verifies reproducibility and publication hygiene for:

1. the scoped necessary rooted Fano-support and `21/189/21` root-image
   reduction under actual target incidence;
2. the scoped actual-incidence rootless indecomposability and forbidden
   three-row motif reductions; and
3. the corrected bounded Wave 32 literature audit.

It does not exclude the rooted endpoint, prove that actual incidence forces
the forbidden rootless motif, classify the surviving rootless
indecomposable endpoint, exclude a determinant row or `n3=708`, improve
`n3>=708`, construct or exclude the target graph, resolve Conway-99, or
establish novelty or priority. All broader statuses remain `UNKNOWN`.
