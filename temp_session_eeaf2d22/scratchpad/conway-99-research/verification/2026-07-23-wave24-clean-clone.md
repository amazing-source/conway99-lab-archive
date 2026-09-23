# Waves 21-24 detached clean-clone replay

```yaml
role: verifier
date_utc: 2026-07-23T21:42:15Z
git_commit: 4111abeea284d218af31cfb7d37ec8a697400998
branch: codex/first-research-wave
claim_label: VERIFIED
scope: detached replay of the committed Waves 21-24 tests, exact generators, manifests, and publication metadata
inputs:
  repository_tree: git commit 4111abeea284d218af31cfb7d37ec8a697400998
  frozen_artifact_manifests: seven committed SHA-256 manifests
method: fresh no-local detached clone, independent test suites, byte-exact regeneration, metadata and privacy gates, and Git integrity checks
command: exact command families are recorded below
outputs:
  persistent_output: this report, whose committed SHA-256 is recorded in STATUS.yaml
  scratch_outputs: 15 regenerated files in a temporary directory outside the clone
limitations: verifies the stated conditional results and repository integrity, not target existence, nonexistence, novelty, or realization of the abstract endpoint survivor
platform: Microsoft Windows NT 10.0.26200.0
python: 3.13.14
git: 2.51.0.windows.1
verdict: PASS
target_result: UNKNOWN
novelty: UNKNOWN
```

The repository was cloned with `--no-local` into a fresh uniquely named
temporary directory and checked out detached. The clone resolved exactly to
the commit above. The Python executable came from the orchestrator workspace's
ignored virtual environment; no workspace-only source or untracked file was
copied into the clone. Every regenerated artifact was written to a separate
temporary output directory.

## Test suites

All 278 tests completed successfully:

| Package | Submitted | Independent |
|---|---:|---:|
| Wave 21 local diagonal | 15/15 | 18/18 |
| Wave 21 lattice extension | 12/12 | 16/16 |
| Wave 22 full order-seven deck | 15/15 | 26/26 |
| Wave 23 primary index proof | 15/15 | 14/14 |
| Wave 23 endpoint cross-check | 25/25 | 17/17 |
| Wave 23 weighted extension | 18/18 | 20/20 |
| Wave 24 `n3=708` index boundary | 15/15 | 17/17 |

Every suite was invoked in path-stable discovery mode:

```powershell
python -B -m unittest discover `
  -s <submitted-or-verification-package> `
  -p <test-module> -v
```

The tests include hostile mutations for dimensional assumptions, modular
residues, rank and trace premises, schema and type errors, hidden fields,
private paths, endpoint arithmetic, and the semantic distinction between an
abstract lattice survivor and a graph.

## Deterministic regeneration

Fourteen generator invocations produced 15 scratch files because the Wave 24
independent command emits both a result and a complete matrix certificate.
Every file matched its committed frozen SHA-256 exactly:

```text
Wave 21 local submitted       2d51c827f822183c7c3cfea60e429ae550c2d95270c76f2a5f469371e71b4ce8
Wave 21 local independent     5150e0047e09cca5b09c15eb7d5a740ff6e0f1bf4291a7a4de0db61120da25af
Wave 21 lattice submitted     18235cf32229bcdf1616a7560aa2389c830e7e23fa25f0a0fc02377c174dc53b
Wave 21 lattice independent   735ff677e7837f14ec2a52cbccd827d30abc5eee68ee5e4f8e2bd6a9e5bd21b1
Wave 22 submitted             ca5d9d116f6a9d6e355600429652e2bf4474b73dcf281bbcb564420d820acbd2
Wave 22 independent           54a02ffda9fe13293d6732fc6bf51f47e28a876a92ebdece10dea187ae0d020c
Wave 23 primary submitted     64bf8192018376961ec88562d64928f73514697000c73cbf79a4a2a2def923b5
Wave 23 primary independent   5ddcc8f5dec1b9923e4c28d60fb998858f33a99e659b451632641f6cea62701b
Wave 23 cross-check submitted 1b31074d0fe4872c14caf1e25842377e4ddab9860f241d87d2814a350ac100a4
Wave 23 cross-check independent
                              69fc4ee307e45f2f4a4ccf1d41817636d38c92d5094080e938ecad66d7d24693
Wave 23 weighted submitted    83a41b78eac02d845650ccdcb5b9782aba80caff9bdb7be983ec3f9e91c65b4c
Wave 23 weighted independent  fecd813402ddb3aabd2434833f020edaf11e82c4392fc6ecc7d1f300b7d97eb4
Wave 24 submitted             a4241cdeea64a8f6073037d564e72fb7ef545287d45aca4759cec6c31d26a463
Wave 24 independent           726807402388c02909171a689f3a7fe2d8d1b74307c24e322ae013d0a9cd486a
Wave 24 survivor certificate  a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2
```

Seven publication manifests were independently parsed. Both supported formats,
`hash path` and `hash byte-count path`, were checked; the byte count was also
verified whenever present:

```text
verification/wave21-lattice-extension/artifact-manifest.sha256       19/19
verification/wave23-index-pranks/artifact-manifest.sha256            20/20
verification/wave23-endpoint-crosscheck/correction-artifact-manifest.sha256
                                                                      13/13
verification/wave23-weighted-extensions/artifact-manifest.sha256       9/9
verification/wave24-n3-708-index/artifact-manifest.sha256             10/10
verification/wave23-literature-audit/publication-hashes.sha256         4/4
verification/wave24-literature-audit/publication-hashes.sha256         6/6
```

## Publication-integrity gates

The integration metadata gate returned:

```text
claims: 55, all IDs unique
obligations: 49, all IDs unique
STATUS path/SHA-256 pairs: 108/108
scoped local Markdown links: 160/160
Waves 21-24 and central release files with LF-only bytes: 177/177
```

A payload-aware privacy scanner read exact Git blobs rather than checkout
text. It includes hostile self-tests that must reject the historical
documentation-only regex while detecting provider-shaped tokens, credential
assignments, private keys, authorization values, credential-bearing URLs, and
raw or JSON-escaped user-profile paths.

```text
HEAD tree:
  623 tree entries
  586 unique blobs
  9,648,491 blob bytes
  findings: 0

25 unpublished commits relative to the public branch head:
  13,721 tree entries
  648 unique path/blob pairs
  610 unique blobs
  10,304,929 blob bytes
  findings: 0
```

The history-range scan matters because deleting a value in a later commit
would not remove it from already reachable Git history.

The remaining release checks returned:

```text
tracked files: 623
largest tracked file: 510,490 bytes
tracked files larger than 1 MiB: 0
git diff --exit-code: PASS
git diff --cached --exit-code: PASS
git status --porcelain: clean
git fsck --full --strict: PASS
```

## Retained gate failures and repairs

No failed wrapper was promoted to a pass.

The first complete detached replay passed all tests, regenerations, and
manifests, but its inline metadata command was mangled by Windows quoting and
raised a Python syntax error. No repository byte changed. That clone was not
accepted.

The second complete detached replay passed its tests, regenerations, manifests,
and metadata, but a broad privacy regex matched the literal scanner command
quoted in a Wave 17 audit. Inspection showed no credential payload and no
username-bearing absolute path. That gate was still treated as failed. The
replacement scanner requires credential-shaped payloads or a real user-profile
component, contains negative and positive self-tests, withholds any matched
value, and scans exact Git blobs.

The accepted detached clone was run in bounded stages. Its first direct-file
`unittest` wrapper could not import a sibling module; discovery mode corrected
the invocation without changing repository bytes. Two one-letter PowerShell
helper names also collided with built-in history aliases, and the first
manifest wrapper assumed only the newer two-field format. Each wrapper stopped
before accepting the affected check. The corrected commands were rerun, all
expected outputs matched, and the final diff, index, porcelain-status, and
object-integrity gates proved that the reused clone remained unchanged.

An earlier monolithic launch also hit the command runner's one-second launch
limit before its test phase; its partial temporary clone was discarded.

## Scope

This replay supports the internally verified conditional necessary bound

```text
n3 >= 708
induced_C6_count >= 209994
```

Wave 23 excludes `n3=705` by two structurally different exact arguments. The
weighted extension verifies feasibility only for its encoded necessary count
relaxation. At `n3=708`, Wave 24 restricts the index to eight arithmetic values
and supplies a complete abstract `h=9` coordinate-lattice survivor. That
survivor is not a primitive embedding in the ambient 231-dimensional lattice,
a 231-vector projector Gram, or a graph.

Accordingly this replay is not a construction, a nonexistence proof, a
formal-kernel proof, peer review, or a novelty certificate. Conway-99 and
novelty remain `UNKNOWN`.
