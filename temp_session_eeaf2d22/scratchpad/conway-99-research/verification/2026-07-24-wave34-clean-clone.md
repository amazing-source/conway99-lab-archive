# Wave 34 detached clean-clone replay

Date: 2026-07-24

Verdict: **PASS**

Exact detached integration commit:
`9cbc9d5f92490c4be972c7f4b69683a6015ae62e`

Integration tree:
`6a3a565a60bd7e70099c43124455118a0d6fd792`

Authenticated chronology integration commit:
`0e11485de2ccdf0c1f2aa1c3e2d53a3413d9b6ea`

Continuation base:
`0fa5b8161baf8b2a5404a67051b7d61cbc906da3`

The replay used a new public-remote clone with local-clone optimization and
hardlinks disabled. The exact integration commit was checked out in detached
state. The clone had no object alternates, `.venv`, or `__pycache__`.
Regenerated outputs were written outside the checkout.

Runtime:

```text
Python 3.13.14
Windows PowerShell 5.1.26100.8875
Git 2.51.0.windows.1
```

## Mathematical and protocol suites

The exact integration tree passed:

| package | outer tests |
|---|---:|
| rooted structural, excluding frozen-status comparison | 44 |
| rooted encoding | 28 |
| rootless | 63 |
| Kuber/Selub source audit | 6 |
| integration-chronology protocol | 8 |
| **direct outer total** | **149** |

The separate status/design validator also passed. The authenticated chronology
wrapper exported exact commit `0e11485`, replaced only `STATUS.yaml` with the
verified continuation-base blob, enabled the full census, and passed the
unchanged 11-test rooted structural comparison suite. The accepted chronology
JSON reproduced SHA-256
`b18a3e402a23f39924dd282482a64404443b8aaa2f1fbfcfb32cec09a2d59cb4`.

Thus Wave 34 executes 160 checks across the current and authenticated
historical-input contexts: 149 direct cases plus 11 isolated comparison cases.

## Complete rooted CNF reconstruction

The clean clone contained the tracked deterministic gzip:

```text
bytes:   17,402,973
SHA-256: 6b6beb5d49c7fe75b9b475162cc4bd97de2793389df150dfab9765ba497305f0
```

It decompressed to the ignored expected raw path:

```text
bytes:   89,546,779
SHA-256: 2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3
```

The independent comparison checked every one of the 4,323,943 clauses and
reported 1,233,001 variables. The generated raw CNF was removed after the
replay, leaving the checkout clean.

## Deterministic regeneration

Six compact machine results regenerated outside the checkout and matched the
accepted bytes:

| result | SHA-256 |
|---|---|
| rooted structural Stage 1 | `9b4c2e00d50e142b4ae551741b8b5b9afda8ecaad0a3085c3cd549c07975ca60` |
| rooted structural Stage 2, isolated historical input | `d73e302d6af8bbd3df28c80ded5dc922e4e6ea5084234ed15531330646fc26d8` |
| rooted pair-census crosscheck | `9165ea2dedcc0f263245335440dcb9dae3a9d1b42425ffbbef3fe4090666f85b` |
| rooted encoding comparison | `05bfd6d0d7e5971c8d8ee15bc5f5b2d88260a2288a00963125ae8b1e2f300015` |
| rootless Stage 1 | `450f01d15b8eaaad2ca7e9f8114c028b96f06bdf4b3944dc69e70525931ec8f9` |
| rootless Stage 2 | `0ba02392424f1fb8507c18c253d423834cb27e6ff945b258d15e757037e1561a` |

The isolated Stage 2 run verified the frozen `STATUS.yaml` SHA-256
`feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864`
before executing.

## Publication manifests

All 130 entries in the 16 nonoverlapping Wave 34 publication manifests
validated:

| package | entries | manifest SHA-256 |
|---|---:|---|
| current literature | 5 | `496085f741e2cda7904e23888f3723b3d51544af6ba5393a35f47c81ecda6766` |
| rooted structural candidate | 5 | `fd1372a3e0013eec265f828a33249f5bb0872e505f7e8479d2946a0e917f32de` |
| rooted structural Stage 1 | 8 | `233a32ac6cb67bcb23b7b269cc6f3f889d943bd5d0714c4f54ead9cbf28c7681` |
| rooted structural Stage 2 | 7 | `ce4bb77f33e919c3086b09521acd80297a9dcfffbc6bb2b72b331c2ee650ae3c` |
| rooted pair-census crosscheck | 7 | `de3152c245367bdc8907983e9d0d3528d153a184d9690ed45e94e2b56b5b0891` |
| rooted encoding publication | 16 | `7cba8a082545cbfcbf01785e6e15a0198bd1cf2357ed0a2b3f353b564a1433e7` |
| rooted encoding Stage 1 | 11 | `3f1bdcb0ca2d08ee0380cd1435673fddb499db8c3a8273f6676c18f17ad3550c` |
| rooted encoding Stage 2 | 8 | `f76ae0aeac6c06ca5a0de1171b619664f558710dfe060cc1c41590b697098acd` |
| rootless candidate | 5 | `bda35ed81dcca9918cff3c544956039b8949a61bfa8a232e4e2d40edcd8d5af2` |
| rootless Stage 1 | 7 | `27c13fb233af677c1619d571bf73820cddd4451172fdd749ace1c9f65f8f3c8d` |
| rootless Stage 2 | 7 | `74d1aa2a95b3ce13a47a19fddafd6e78fec193a20fd92c035e2c872345c795bc` |
| status/design sources | 5 | `1af4bad56405fb24128285fa586e2d1e2b80c82f1bdffdafa7cbdb6053cd6812` |
| Harrison source audit | 11 | `6052d3114a89af378cf412cc3126b60bab9dc9fe249a673188d3369a681db386` |
| Kuber/Selub source audit | 14 | `5053217d6432365b903b787cb53e923996e96feef404904caad89dd7ebd686bc` |
| consolidated external audit | 7 | `f21ec00738093ac6579654c88bff3a0c9b35665c2dee83cd5cd9422b9eab483c` |
| integration chronology | 7 | `3faa49fef4f49471425e830c60caccac0779542e84fd8f6dca6f34d82b6c0de3` |

The overlapping 18-entry complete local encoding manifest also validated but
is not double-counted in the publication total.

## Central metadata gates

```text
tracked JSON files:                  234 strict parses
tracked YAML files:                   94 duplicate-key-rejecting parses
claims:                               89 unique
obligations:                          84 unique
claim evidence references:           794 resolving
obligation evidence references:      796 resolving
STATUS path/SHA-256 pairs:            439 matching
Wave 34 status path/SHA-256 pairs:     37 matching
publication manifests:                16
publication manifest entries:        130
tracked Markdown files:              392 parsed
local Markdown links:                392 exact-case resolving
BibTeX keys:                           92 unique
```

## Exact-blob privacy gate

The privacy scan read the exact release archive, every blob introduced from
the continuation base through the integration commit, and every intervening
commit message:

```text
release tree:  1,235 files, 36,494,551 bytes
range objects:   346
  commits:        25
  trees:         102
  blobs:         219, totaling 22,459,745 bytes
```

It checked for real local-user and temporary paths, OpenAI and GitHub token
shapes, AWS access-key shapes, private-key headers, and bearer-token shapes.
It found zero matches. No private Codex capture ref was present on the public
remote.

## Retained finalization corrections

The first full-range hygiene pass found Markdown hard-break spaces in three
source audits and one terminal blank line in a failed-routes ledger. A first
attempt to classify them through `.gitattributes` was rejected because that
file is a frozen rooted-encoding input. The prose bytes were normalized
instead, and every affected run report and manifest was rebuilt. The complete
mathematical suite then passed with the original `.gitattributes` freeze.

A later chronology replay correctly passed all 11 mathematical tests but
revealed that a JSON field used the caller worktree's status hash instead of
the requested commit's blob. That draft was rejected. The wrapper now hashes
the exact requested Git blob, cross-checks the archive, passes an eighth
protocol test, and reproduces the accepted result byte-identically.

All retained failures and repairs are detailed in
`verification/2026-07-24-wave34-orchestrator-corrections.md`.

## Repository integrity and scope

The full Wave 34 range passed `git diff --check`.
`git fsck --full --strict` returned success with no output. The detached clone
had a clean status after raw-CNF cleanup, no object alternates, no local
environment, and no Python bytecode cache. The public branch resolved to the
exact audited commit.

This replay verifies reproducibility and publication hygiene for the scoped
rooted encoding, rooted structural reparameterization and necessary
single-column census, rootless actual-incidence lemmas and moment bounds, and
bounded external-source characterizations.

It supplies no graph, no complete-domain SAT or UNSAT result, no compatible
15-column rooted design, no rootless global motif-forcing theorem, no
endpoint resolution, no `n3=708` exclusion, no Conway-99 resolution, and no
novelty or priority result. All broader statuses remain `UNKNOWN` or `NONE`.
