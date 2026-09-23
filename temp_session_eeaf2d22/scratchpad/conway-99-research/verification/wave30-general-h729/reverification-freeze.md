# Wave 30 repaired general-`h=729` re-verification freeze

```yaml
role: verifier
date_utc: 2026-07-24T05:23:50Z
git_commit: a7be6b8ae70d8b44e88db8dfd6804f8d946ca382
claim_label: DERIVED
scope: >-
  Exact-byte freeze of the repaired Wave 30 discovery revision before
  independently replaying its submitted package and the preserved historical
  verifier. This freeze does not itself promote the repaired theorem.
inputs:
  repaired_commit: a7be6b8ae70d8b44e88db8dfd6804f8d946ca382
  original_discovery_commit: 091d0a458ab1f96e3b3f491b677c84824bbf8f44
  original_verifier_veto_commit: 0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321
method: >-
  Resolve all three Git commit objects and ancestry; compare each checked-out
  repaired byte sequence with its Git blob; compute SHA-256 and byte length;
  inspect the complete repair diff; and validate the noncyclic discovery
  manifest independently.
command: |-
  git cat-file -t <commit>
  git ls-tree a7be6b8ae70d8b44e88db8dfd6804f8d946ca382 -- <path>
  git hash-object --no-filters -- <path>
  git diff 091d0a458ab1f96e3b3f491b677c84824bbf8f44 a7be6b8ae70d8b44e88db8dfd6804f8d946ca382 -- attempts/wave30-general-h729
outputs:
  freeze_record: verification/wave30-general-h729/reverification-freeze.md
limitations:
  - The original failed revision and veto remain separate historical records.
  - The artifact manifest intentionally omits its own hash to avoid a cycle.
  - Mathematical verification is recorded in reverification-audit.md.
```

## Commit objects and ancestry

The exact repaired target exists as a Git commit:

```text
commit:  a7be6b8ae70d8b44e88db8dfd6804f8d946ca382
tree:    ee6f852c7072e0ff467c48b323682db69ff5486b
parent:  5a5eebfc888d7e3f278390a165de66b0c07235b4
subject: fix: repair Wave 30 general provenance freeze
```

The preserved original discovery and verifier-veto commits also exist:

```text
091d0a458ab1f96e3b3f491b677c84824bbf8f44
  search: preserve Wave 30 decomposable endpoint candidate

0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321
  verify: veto Wave 30 general replay provenance
```

Both are ancestors of the repaired commit. The path-specific ancestry is:

```text
091d0a458ab1f96e3b3f491b677c84824bbf8f44
0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321
a7be6b8ae70d8b44e88db8dfd6804f8d946ca382
```

## Exact repaired discovery bytes

Every checked-out byte sequence below had the same Git blob object as the
corresponding path at `a7be6b8ae70d8b44e88db8dfd6804f8d946ca382`.

| SHA-256 | Bytes | Git blob | Path |
|---|---:|---|---|
| `fd1f11a2ab5c5dfd2732a4ba1fb8d063dea1ae0e96d417aaf9d45eade4f2281a` | 17162 | `e3ccc75b6a9af85574b28b9430fbb1eacf3548dd` | `agents/2026-07-24-wave30-general-h729.md` |
| `e562654891c61a1ae50d34a6a38c6d9a39e985a03d7b0a253f60871539f1f006` | 896 | `7d997f62e15d73ea742afa9d5dfde885ba45c11d` | `attempts/wave30-general-h729/artifact-manifest.sha256` |
| `b3c2b4c79b23f418cb63876560236d62e0be2c6cac69979106e03e5a8247d6a5` | 20287 | `ad84942555c3b7931bf8eae0080774d61abe7c65` | `attempts/wave30-general-h729/exact_check.py` |
| `9075d5fd77253850ba09c4655d9cbab135eb32fdd36638dc4aa9051fa49898a2` | 9245 | `ad7890d5d51614d3e9eb96259e513546af91a99f` | `attempts/wave30-general-h729/test_exact_check.py` |
| `cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c` | 16125 | `ea4aee3784539628d0ccd0004502577af88854ef` | `attempts/wave30-general-h729/exact-results.json` |
| `5996de9f71b0f3fca34040ac5c710c9e6d87885ad2bba94638c8cfeabd9ce245` | 599 | `c98182e17103490890041e8e362c1de57bda9c49` | `attempts/wave30-general-h729/input-freeze.sha256` |
| `397f74c75a8ae24bedd26fea41c0fb82d03c6611a87627e86aeb29244a586006` | 2848 | `27d36649d8d00fa218baa13b008f5f77b8a7f3e5` | `attempts/wave30-general-h729/failed-routes.md` |
| `407bfb983f3df88335f8071d75127fdf554c59cf6ba41a3cdd7abdbc62dcc393` | 2931 | `dcf2158c7c6ca5039924fca479832c82c701690b` | `attempts/wave30-general-h729/run-report.yaml` |
| `1cf8aa09a65b552e7d81d2d9e46df6e59ce67222be6469094e9d788f99959cbd` | 5894 | `143144f090c6cf623defa0f289f0ea0154d492f9` | `attempts/wave30-general-h729/repair-ledger.md` |

The discovery artifact manifest has eight entries and validates all eight with
zero missing paths, syntax errors, or hash mismatches. Its own nonembedded
container hash is:

```text
e562654891c61a1ae50d34a6a38c6d9a39e985a03d7b0a253f60871539f1f006
```

The five-entry input freeze also validates with zero findings.

## Repair-diff boundary

The repair is provenance/status/metadata only:

- `exact_check.py` changes exactly two values: the Wave 29 audit SHA-256 from
  stale `4101a394252807fb9de8c39fb32b780bc88410d99e47dfe698da251b49f3e061`
  to committed `dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d`,
  and the pending-verifier status string to a pending-reverification string.
- `exact-results.json` changes exactly the corresponding frozen hash and
  status string.
- `input-freeze.sha256` changes exactly the stale hash.
- The discovery report, run report, manifest, and new repair ledger record
  repair provenance, dependent hashes, and status metadata.
- `test_exact_check.py` and `failed-routes.md` are byte-identical between
  `091d0a458ab1f96e3b3f491b677c84824bbf8f44` and
  `a7be6b8ae70d8b44e88db8dfd6804f8d946ca382`.

No lemma, arithmetic constant, candidate type, obstruction, tensor count,
limitation, or theorem scope changed.

## Re-verifier execution identity

```text
model: gpt-5.6-sol
reasoning_effort: max
role: independent adversarial re-verifier
```
