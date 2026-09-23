# Wave 30 general-`h=729` discovery repair ledger

```yaml
role: proof_b
date_utc: 2026-07-24T05:01:15Z
claim_label: DERIVED
repair_status: PENDING_INDEPENDENT_REVERIFICATION
objection: V30-GEN-001
preserved_discovery_commit: 091d0a458ab1f96e3b3f491b677c84824bbf8f44
preserved_verifier_veto_commit: 0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321
scope: >-
  Provenance-only repair of the Wave 30 discovery package after its frozen
  Wave 29 audit hash failed committed replay. No mathematical statement,
  test semantics, surviving type, limitation, or status boundary changed.
```

## Failure preserved

The original discovery revision is preserved by:

```text
091d0a458ab1f96e3b3f491b677c84824bbf8f44
  search: preserve Wave 30 decomposable endpoint candidate
```

Its checker froze the transient hash

```text
4101a394252807fb9de8c39fb32b780bc88410d99e47dfe698da251b49f3e061
  verification/wave29-s0-frame-exclusion/audit.md
```

The applicable committed file instead has:

```text
dbdcb88bf309cbfa47a42b9fb63dd7cf483e07cac8b92c475094c96be3723b7d
  verification/wave29-s0-frame-exclusion/audit.md
```

The independent verifier preserved the resulting zero-test/generator failure
and publication veto in:

```text
0bc6dc9b90dff6589cfaf9db1a84e2d8242b6321
  verify: veto Wave 30 general replay provenance
```

The authoritative objection is `V30-GEN-001` in
`verification/wave30-general-h729/failure-ledger.md`.  Its scoped
mathematical reconstruction passed, but the submitted discovery tests stopped
in `setUpClass` and the submitted generator stopped before output because of
the stale hash.

## Exact repair

The repair changes only:

1. the Wave 29 audit hash in the report, checker, input freeze, run metadata,
   and regenerated JSON;
2. the generated/result and dependent checksum metadata;
3. explicit repair provenance and pending-re-verification wording; and
4. this ledger and its manifest entry.

The test source and its semantics are unchanged.

## Pre-repair and post-repair hashes

| Artifact | Pre-repair SHA-256 | Post-repair SHA-256 | Disposition |
|---|---|---|---|
| `agents/2026-07-24-wave30-general-h729.md` | `1bc63f569600bca88e12c977a0bd94ecdd03aa5f3fd8c4f203d4778fbec78efa` | `fd1f11a2ab5c5dfd2732a4ba1fb8d063dea1ae0e96d417aaf9d45eade4f2281a` | prior hash and repair metadata updated |
| `attempts/wave30-general-h729/exact_check.py` | `ed8edcbb0febde6d6fbd57776b7696402f832421fa11fb1984fcd57c8369eaff` | `b3c2b4c79b23f418cb63876560236d62e0be2c6cac69979106e03e5a8247d6a5` | frozen input and repair status updated |
| `attempts/wave30-general-h729/exact-results.json` | `93cc1633d0b25d5f3daecd4c49cbc3b2dc3f754576a3cd5c9364c729a79a7698` | `cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c` | regenerated, not hand-edited |
| `attempts/wave30-general-h729/input-freeze.sha256` | `a07c703b20237441b221e13c68be885d01db180871b8496af5d7204e2587793b` | `5996de9f71b0f3fca34040ac5c710c9e6d87885ad2bba94638c8cfeabd9ce245` | committed Wave 29 audit hash substituted |
| `attempts/wave30-general-h729/run-report.yaml` | `77232c06827c4c62e7dc6f5380cc4ebe2a3c6d5496fe8c3592589986089e416f` | `407bfb983f3df88335f8071d75127fdf554c59cf6ba41a3cdd7abdbc62dcc393` | inputs, outputs, and repair metadata updated |
| `attempts/wave30-general-h729/test_exact_check.py` | `9075d5fd77253850ba09c4655d9cbab135eb32fdd36638dc4aa9051fa49898a2` | `9075d5fd77253850ba09c4655d9cbab135eb32fdd36638dc4aa9051fa49898a2` | unchanged |
| `attempts/wave30-general-h729/failed-routes.md` | `397f74c75a8ae24bedd26fea41c0fb82d03c6611a87627e86aeb29244a586006` | `397f74c75a8ae24bedd26fea41c0fb82d03c6611a87627e86aeb29244a586006` | unchanged |
| `attempts/wave30-general-h729/artifact-manifest.sha256` | `29cbbdff1ab167b436db725130d830bfd047beb1c4ba834c51b5a33c3aed690a` | manifest-container hash reported in the final repair handoff | rebuilt with eight entries, including this ledger |
| `attempts/wave30-general-h729/repair-ledger.md` | absent | pinned by the rebuilt artifact manifest | new repair provenance |

The two container hashes cannot be embedded into this ledger without a
checksum cycle: the manifest hashes this ledger, and this ledger cannot also
contain the final manifest hash while remaining the byte sequence hashed by
that manifest.  The rebuilt manifest contains every artifact hash, including
this ledger; the final handoff reports the manifest file's own SHA-256.

## Replay evidence

The unchanged command:

```text
python -B -m unittest -v test_exact_check.py
```

now runs:

```text
Ran 20 tests
OK
```

The generator:

```text
python -B exact_check.py --output exact-results.json
```

emits SHA-256:

```text
cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c
```

A second generation to an external temporary directory matched this file
byte for byte:

```text
BYTE_IDENTICAL PASS
bytes=16125
sha256=cb0a58195506a51ca6a39aaab197a3592344f7aef8b5b0c2af51770c7069ad6c
```

The final repair audit also passed JSON and YAML parsing, exact eight-entry
manifest validation, LF-only files with exactly one terminal newline, NUL
screening, privacy scanning, and `git diff --check`.

## Mathematical and status invariants

No mathematical or evidentiary boundary changed:

```text
conditional decomposable-rootless h=729 classification:  DERIVED
repair:                                                   PENDING INDEPENDENT RE-VERIFICATION
unique rank-20 plus rank-24 type:                         UNKNOWN
rooted h=729 forms:                                      UNKNOWN
integrally indecomposable h=729 forms:                    UNKNOWN
n3=708:                                                  UNKNOWN
Conway-99:                                               UNKNOWN
novelty:                                                 UNKNOWN
```

No construction, full endpoint package, graph, automorphism reduction, or
failed-search inference is introduced by this repair.
