# Wave 26 detached clean-source replay

```yaml
role: verifier
date_utc: 2026-07-23T23:38:47Z
git_commit: 4f1f3be35e712789dcba10fda5ec8d2bc569bc17
branch: codex/first-research-wave
claim_label: VERIFIED
scope: detached replay of the committed Wave 26 tests, exact generators, manifests, central metadata, privacy gates, and Git integrity
inputs:
  repository_tree: git commit 4f1f3be35e712789dcba10fda5ec8d2bc569bc17
  public_history_baseline: git commit 930cb99e28d2461fbdec378318efc911f8e36a82
  frame_verifier_manifest:
    path: verification/wave26-a2-frame-obstruction/artifact-manifest.sha256
    sha256: dc12aeacd906d5b7f54fca3de796ca95d829385ac3a901dbf9760ee4aed3550c
  cubic_verifier_manifest:
    path: verification/wave26-a2-cubic-obstruction/artifact-manifest.sha256
    sha256: 75572e7f356312e2f4aee94ecaa5032f7d2bfdfd530f989a9e36fd39da63f842
  literature_manifest:
    path: verification/wave26-literature-audit/manifest.sha256
    sha256: 0d9381d47a33fa376c53510cae2a57dfd419a41bb96658b56ce7cb624d953816
method: fresh no-local detached clone, four independent test suites, byte-exact regeneration, metadata and privacy gates, and Git integrity checks
command: exact command families are recorded below
outputs:
  persistent_output: this report, whose committed SHA-256 is recorded in STATUS.yaml
  scratch_outputs: four regenerated JSON files in a temporary directory outside the clone
limitations: verifies the scoped Wave 26 A2 obstructions and repository integrity, not all h=9 forms, n3=708, target existence, nonexistence, or novelty
platform: Microsoft Windows NT 10.0.26200.0
python: 3.13.14
git: 2.51.0.windows.1
verdict: PASS
target_result: UNKNOWN
novelty: UNKNOWN
```

The repository was cloned with `--no-local` into a fresh uniquely named
temporary directory and checked out detached at the integration commit. No
untracked or ignored workspace file was copied into the clone. All four
generated artifacts were written to a separate temporary output directory.

## Test and regeneration results

All committed suites passed:

| Package | Tests |
|---|---:|
| Wave 26 frame discovery checker | 15/15 |
| Wave 26 frame independent verifier | 14/14 |
| Wave 26 cubic discovery checker | 19/19 |
| Wave 26 cubic independent verifier | 17/17 |

They were invoked in path-stable discovery mode:

```powershell
python -B -m unittest discover `
  -s attempts\wave26-a2-frame-obstruction -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave26-a2-frame-obstruction `
  -p test_independent_check.py -v
python -B -m unittest discover `
  -s attempts\wave26-a2-cubic-obstruction -p test_exact_check.py -v
python -B -m unittest discover `
  -s verification\wave26-a2-cubic-obstruction `
  -p test_independent_check.py -v
```

The four exact generators were then invoked with `--output` paths outside the
clone. Their scratch files matched the committed results byte-for-byte:

```text
frame submitted      bb2b2ffe33d0ca6a0a1f18be8b36c48060d40aef2fc6e0857fd1d23c18e84bb9
frame independent    b664844d65ab553cfd2277e925f5596193c586378d880dc1a29242cb9ac8f03b
cubic submitted      acc3ce7298c164bdee1fe32766bf18437fe79770ee69090b759d3dc774640f33
cubic independent    658b7eb7eec64a4560d20e9c7b272c428168876c43910d9af6e44035dde12352
```

All publication manifests were independently parsed and checked:

```text
verification/wave26-a2-frame-obstruction/artifact-manifest.sha256  8/8
verification/wave26-a2-cubic-obstruction/artifact-manifest.sha256  9/9
verification/wave26-literature-audit/manifest.sha256                9/9
```

## Publication-integrity gates

Strict YAML, path, hash, link, line-ending, and bibliography replay returned:

```text
claims: 60, all IDs unique, all evidence paths present
obligations: 54, all IDs unique, all evidence paths present
STATUS path/SHA-256 pairs: 151/151
recorded commit objects: 109/109 resolve
root-document local Markdown links: 172/172
Wave 26 and central publication files with LF-only bytes: 50/50
BibTeX keys: 47, all unique, braces balanced
```

The status assertions also confirmed:

```text
frame verifier verdict: PASS_SCOPED_A2_FRAME_OBSTRUCTION
cubic verifier verdict: PASS_SCOPED_A2_CUBIC_OBSTRUCTION
explicit survivor projector-frame origin: REFUTED
explicit survivor full Schur origin: REFUTED
abstract coordinate-lattice survivor: PRESERVED
all h=9 forms excluded: false
n3=708 excluded: false
target and novelty: UNKNOWN
```

A payload-aware scanner read exact Git blobs. Its positive controls detect
provider-shaped tokens, private-key headers, authorization values,
credential assignments, credential-bearing URLs, and raw user-profile paths.
Negative controls reject explicit redaction and placeholder values. Matched
secret values are never printed.

```text
integration tree:
  687 tree entries
  649 unique blobs
  8,980,520 blob bytes
  findings: 0

three commits after public baseline 930cb99:
  694 unique path/blob pairs
  656 unique blobs
  9,349,272 blob bytes
  findings: 0
```

The history-range scan prevents a later deletion from hiding a value that
would remain reachable in an earlier unpublished commit.

The final repository gates returned:

```text
tracked files: 687
largest tracked file: 510,490 bytes
tracked files larger than 1 MiB: 0
git diff --exit-code: PASS
git diff --cached --exit-code: PASS
git status --porcelain: clean
git fsck --full --strict: PASS
```

## Retained wrapper failures and corrections

No failed wrapper was promoted to a pass.

The first manifest wrapper assumed every entry was relative to its manifest
directory. The frame manifest intentionally stores repository-relative paths,
so that wrapper doubled the prefix and stopped with missing-file errors. The
corrected resolver accepts an entry only if it exists either at repository
scope or relative to the manifest directory. All three manifests then passed.

The privacy scanner's first negative self-test classified an explicit
`REDACTED` credential URL as a credential. It stopped before scanning or
acceptance. The corrected scanner makes authorization values, credential
assignments, and credential-bearing URLs placeholder-aware while all nine
positive controls still fire. All nine positive and six negative controls
then passed before both exact-blob scans returned zero findings.

Neither wrapper correction changed a repository byte. The final diff, index,
status, and object-integrity checks prove that the accepted clone remained
clean.

## Scope

The frame route proves that a required projector frame cannot have a
scaled-dual form with an orthogonal `A2` summand:

```text
forced A2-root rows: 21
oriented-root capacity: 18
```

The separate cubic route proves:

```text
required tr(A2 Q_AA): at least 18
explicit survivor block trace: 10
```

Together they refute the projector-frame and full Schur-square origins of the
one explicit Wave 24 `E8^5 orthogonal-sum A2^2` hostile control. Its abstract
coordinate matrices remain exact. No classification of all determinant-nine
forms or other surviving index rows is proved, and the proposed stronger
determinant cap `det(B)<=3645` remains `UNKNOWN`. Therefore this replay does
not exclude `n3=708`; the project bound remains `n3>=708`. Conway-99
existence and novelty remain `UNKNOWN`.
