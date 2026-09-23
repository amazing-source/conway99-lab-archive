# Wave 21 orchestrator replay

Verdict: **PASS for exact reproduction of the frozen discovery and independent
verification artifacts.** The raw equation from the pinned six-vertex source
fails in the independently predicted way; the explicitly corrected path and
both hostile suites pass. This replay does not strengthen `n3>=705` and does
not resolve Conway-99.

```yaml
role: verifier
date_utc: 2026-07-23T17:52:23Z
git_commit: 54dd37cc8bb68b8bc50a861e1e5f7e305ca93f3b
claim_label: VERIFIED
scope: >
  Orchestrator replay of the Wave 21 six-/seven-vertex necessary-count
  feasibility package, including fresh primary-source downloads, safe archive
  inspection, exact source hashes, byte-identical discovery and verifier
  results, the expected raw-source failure, the explicit correction, hostile
  tests, manifests, run-report parsing, line endings, and public hygiene.
inputs:
  candidate_commit: 6e043043022e1c528088fa50a76507b8e84472a6
  verifier_commit: 54dd37cc8bb68b8bc50a861e1e5f7e305ca93f3b
  six_archive_sha256: f8429d2f839267e2aaf98b04451cb2f0252c0353f75bee6ec6e6947eab0d5834
  six_tex_sha256: 823bcaf636a99f6655af453b2a910b9953338db980480572bca81730cfa1b44f
  seven_archive_sha256: 10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a
  seven_tex_sha256: 0b06fdc1c2951a344592c6af23abd133c4a8a68d717f199e7a0e2d7ceb909d0a
method: >
  Download the two pinned arXiv source archives into a unique system
  temporary directory; enumerate every archive member and reject absolute,
  parent-traversing, or drive-qualified paths before extraction; hash the
  archives and exact TeX inputs; execute the submitted and independently
  written checkers; compare every regenerated JSON byte-for-byte; replay both
  hostile suites; and validate every manifest entry and run-report.
command: >
  Direct PowerShell orchestration of exact_check.py, independent_check.py,
  both unittest files, Get-FileHash, archive-path validation, JSON byte
  comparison, manifest validation, YAML parsing, LF checks, and credential or
  machine-local-path scans. See REPRODUCING.md for public commands.
outputs:
  candidate_result:
    path: attempts/wave21-six-vertex-lp/exact-results.json
    sha256: 5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b
  raw_printed_result:
    path: verification/wave21-six-vertex-lp/independent-raw-printed-results.json
    sha256: 50129e12b180c4f7ad7655cb4febe229588a855042a04b28817eeb52a3b27fb6
  corrected_result:
    path: verification/wave21-six-vertex-lp/independent-corrected-results.json
    sha256: 1c0cc560206ce388308573f2174a0a6189ae909f83a4acb86093063b5adfeacd
  candidate_tests: "16/16 PASS"
  independent_tests: "19/19 PASS"
  manifest_entries: "24/24 PASS"
limitations: >
  This replay verifies the encoded necessary-count system and a narrow source
  equation correction. Formula feasibility is not global graph existence,
  and the seven-vertex source covers Hamiltonian types only. Current source
  status and novelty require a separate source-first audit. Conway-99 remains
  UNKNOWN.
```

## Observed replay

The fresh source downloads and guarded extraction gave:

```text
SourceArchives 2/2 HASH PASS
ArchivePathSafety PASS
SourceTex 2/2 HASH PASS
```

The submitted lane then gave:

```text
CandidateTests 16/16 PASS
CandidateReplay BYTE_IDENTICAL
```

The independent checker deliberately preserves two modes. Against the raw
printed `m7(n-5)` equation it returned process exit 1 and regenerated the
frozen `FAIL_AS_PRINTED` JSON byte-identically. Against the one named
correction, adding `+n23` to that right-hand side, it returned process exit 0
and regenerated the corrected JSON byte-identically:

```text
RawPrintedReplay EXPECTED EXIT 1 / BYTE_IDENTICAL
CorrectedReplay PASS / BYTE_IDENTICAL
IndependentTests 19/19 PASS
```

All discovery and verification manifest entries were present with matching
byte counts and SHA-256 hashes. Both run reports parsed, all checked evidence
used LF line endings, and the scoped credential and machine-local-path scan
passed:

```text
Manifests 24/24 PASS
Hygiene PASS
```

## Retained harness failure

The first attempt to run the long PowerShell orchestration through a
JavaScript tool wrapper failed before PowerShell started:

```text
SyntaxError: missing ) after argument list
```

This was an orchestration quoting error, not mathematical evidence. No replay
command ran and no artifact changed. The same checks were then issued directly
to PowerShell and produced the passing results above.

## Status boundary

The replay confirms:

```text
raw printed m7(n-5) equation:       REFUTED_AS_PRINTED
explicit +n23 correction:           VERIFIED
encoded six/seven count exhaustion: VERIFIED_INCONCLUSIVE
stronger lower bound than n3>=705:  NONE
Conway-99:                          UNKNOWN
novelty:                            UNKNOWN
```
