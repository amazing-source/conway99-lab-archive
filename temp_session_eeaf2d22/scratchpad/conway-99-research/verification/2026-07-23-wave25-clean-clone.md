# Wave 25 detached clean-source replay

```yaml
role: verifier
date_utc: 2026-07-23T22:24:46Z
git_commit: 156756d4ef98dc7233e29a7f8c9feeb143548197
branch: codex/first-research-wave
claim_label: VERIFIED
scope: detached replay of the committed Wave 25 tests, exact generators, manifests, central metadata, privacy gates, and Git integrity
inputs:
  repository_tree: git commit 156756d4ef98dc7233e29a7f8c9feeb143548197
  public_history_baseline: git commit 7103ddfe755a8c3430ef79e9a76e3323f1e00e1d
  verifier_manifest:
    path: verification/wave25-n3-708-strictness/artifact-manifest.sha256
    sha256: 473601e70d6c873e1b691d8fcf7c769d907ae2a9eadff198d72e0936e9fcc1ce
  literature_manifest:
    path: verification/wave25-literature-audit/publication-hashes.sha256
    sha256: df3621eefa727aac0a75e8562b31dcfda0c4eec313dcdb0bd5e2f3704941d395
method: fresh no-local detached clone, independent test suites, byte-exact regeneration, metadata and privacy gates, and Git integrity checks
command: exact command families are recorded below
outputs:
  persistent_output: this report, whose committed SHA-256 is recorded in STATUS.yaml
  scratch_outputs: two regenerated JSON files in a temporary directory outside the clone
limitations: verifies the scoped conditional Wave 25 refinement and repository integrity, not target existence, nonexistence, novelty, or realization of the abstract endpoint survivor
platform: Microsoft Windows NT 10.0.26200.0
python: 3.13.14
git: 2.51.0.windows.1
verdict: PASS
target_result: UNKNOWN
novelty: UNKNOWN
```

The repository was cloned with `--no-local` into a fresh uniquely named
temporary directory and checked out detached at the commit above. No
untracked or ignored workspace file was copied into the clone. Both generated
artifacts were written to a separate temporary output directory.

## Test and regeneration results

Both committed suites passed:

| Package | Tests |
|---|---:|
| Wave 25 discovery checker | 21/21 |
| Wave 25 independent verifier | 18/18 |

They were invoked in path-stable discovery mode:

```powershell
python -B -m unittest discover `
  -s attempts\wave25-n3-708-strictness `
  -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave25-n3-708-strictness `
  -p test_independent_check.py -v
```

The two exact generators were then invoked with `--output` paths outside the
clone. Their scratch files matched the committed results byte-for-byte:

```text
submitted    6da9200adf19a5305913178c271ac584e9825aa4f3594fad20717f9418d2b40e
independent  8c147d7b9da422c9d9b3d646015d95d737efc57d81964fabb3b33574a1d69f77
```

Both publication manifests were independently parsed and checked:

```text
verification/wave25-n3-708-strictness/artifact-manifest.sha256  6/6
verification/wave25-literature-audit/publication-hashes.sha256  4/4
```

## Publication-integrity gates

The strict-YAML and metadata replay returned:

```text
claims: 57, all IDs unique, all evidence paths present
obligations: 51, all IDs unique, all evidence paths present
STATUS path/SHA-256 pairs: 129/129
Wave 25 recorded commits: 3/3 resolve
scoped root-document local Markdown links: 165/165
Wave 25 and central publication files with LF-only bytes: 26/26
BibTeX keys: 42, all unique, braces balanced
```

The status assertions also confirmed that the verifier verdict is
`PASS_SCOPED_STRICTNESS`, target and novelty are `UNKNOWN`, the headline bound
did not change, `n3=708` is not excluded, the combined determinant cap is
6525, and the exact factor-pair count is 323.

A payload-aware scanner read exact Git blobs. Its positive controls detect
provider-shaped tokens, private-key headers, authorization values, credential
assignments, credential-bearing URLs, and raw user-profile paths. Negative
controls reject documentation-only regular expressions and explicit redaction
placeholders. Matched values are never printed.

```text
HEAD tree:
  643 tree entries
  606 unique blobs
  8,545,408 blob bytes
  findings: 0

four commits after public baseline 7103ddf:
  2,551 tree entries
  650 unique path/blob pairs
  613 unique blobs
  8,891,656 blob bytes
  findings: 0
```

The history-range scan prevents a later deletion from hiding a value that
would remain reachable in an earlier unpublished commit.

The final repository gates returned:

```text
tracked files: 643
largest tracked file: 510,490 bytes
tracked files larger than 1 MiB: 0
git diff --exit-code: PASS
git diff --cached --exit-code: PASS
git status --porcelain: clean
git fsck --full --strict: PASS
```

## Retained wrapper failures and corrections

No failed wrapper was promoted to a pass.

The first all-tracked-Markdown link wrapper treated PowerShell type casts such
as `[int64](...)` in an older audit as Markdown links. It stopped before
acceptance. The corrected gate was scoped to the five root publication
documents, including every newly added Wave 25 link, and all 165 local links
resolved.

The privacy scanner's first negative self-test classified an explicit
`REDACTED` credential-URL placeholder as a credential. It stopped before
scanning or acceptance. The corrected scanner exempts only a short fixed set
of explicit placeholder values while its positive credential-URL control
still fires. All eight positive and six negative controls then passed before
the full exact-blob scans returned zero findings.

Neither wrapper correction changed a repository byte. The final diff, index,
status, and object-integrity checks prove that the accepted clone remained
clean.

## Scope

The replay supports the conditional Wave 25 consequences at the first
surviving endpoint:

```text
n3 = 708
tr(C^2) >= 10
tr(B^2) >= 116
det(B) <= 6525
```

The determinant line is the complete combined arithmetic cap after the
strict logarithmic bound, congruences, and exact index enumeration. It is not
a graph construction or a standalone improvement of the pointwise analytic
inequality.

The exact abstract `h=9`, `det(B)=81` coordinate-lattice package survives.
It is not a primitive sublattice of `Z^231`, a 231-column projector Gram
realization, a Hadamard/Schur-square realization, or a graph. Therefore this
replay does not exclude `n3=708`; the project bound remains `n3>=708`.
Conway-99 existence and novelty remain `UNKNOWN`.
