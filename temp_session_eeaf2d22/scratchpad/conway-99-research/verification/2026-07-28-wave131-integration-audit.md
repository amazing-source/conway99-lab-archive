# Waves 123 and 127--131 integration audit

```yaml
role: orchestrator
date_utc: 2026-07-28T06:52:33Z
git_commit: e1484c6564ddfde580191cdcb4a66a8f6ad7f2a2
claim_label: VERIFIED_SCOPED | VERIFIED_SCOPED_FINITE | UNKNOWN
scope: >-
  Integration of exact fixed-C4 projector checks, finite level-seven
  Jacobi feasibility, the conditional motif finite-primary eigenlattice
  split, and the binary LCD ordinary-enumerator boundary.
inputs:
  - path: attempts/wave123-fixedc4-threepoint/package-manifest.sha256
    sha256: 39d680e78bf547c4fb5564048c6b7b1561382fd7d289f54a8a86154cff1a08a7
  - path: verification/wave123-fixedc4-threepoint/package-manifest.sha256
    sha256: 9cd5c9de7ed6b8a919804cf94bab8f0df1bacefd6f57ea273453e14c122fe6c1
  - path: attempts/wave127-independent-jacobi-certificate/MANIFEST.sha256
    sha256: f4a1039928dcbd21e8de81f199265c80631182ec53f51d8c7e657259ee2f5fe4
  - path: attempts/wave129-jacobi-stress/MANIFEST.sha256
    sha256: 93e1f208faec2187ed3339e131af670d181a63a9518e6fd39ef0939540d79e5b
  - path: verification/wave127-wave129-jacobi-audit/package-manifest.sha256
    sha256: d4e69a7a39920b946d4907423faaf26c78a7e3e5d15eceac28baab1a5fcabf8c
  - path: attempts/wave128-alternative-spaces/package-manifest.sha256
    sha256: 851df7c40ab2056f6a5f927093707e5e9b578df2b18662e6b95fcf6335033038
  - path: verification/wave128-alternative-spaces/package-manifest.sha256
    sha256: 8d48809b536d5eff823c05254b8a34bfdf743f8b97facf5799352ddad2bae606
  - path: attempts/wave131-binary-lcd-enumerator/package-manifest.sha256
    sha256: c305de05df2001d869db3dbfc14f7a2a8c7f305ce43471c56c66dc775e89d576
  - path: verification/wave131-binary-lcd-enumerator/package-manifest.sha256
    sha256: 2315e9d9a0b25e2592340829ea6d2c3941fb30d3c85efab42af24cff6a9dcde3
method: >-
  Replay every package seal; run discovery and independent tests; compare
  clean-room mathematical reconstructions; and retain every finite,
  conditional, heuristic, and timeout boundary without promotion.
outputs:
  - path: verification/2026-07-28-wave131-integration-audit.md
limitations: >-
  No package constructs or excludes srg(99,14,1,2). Cutoff 28 Jacobi
  feasibility, universal fixed-C4 caps, the integral binary enumerator,
  motif extension, all rank exclusions, and novelty remain UNKNOWN.
```

## Verdicts

| Lane | Integrated verdict | Exact boundary |
|---|---|---|
| Fixed-C4 projector | `VERIFIED_SCOPED` | The displayed 40-word realization and one alternate 26-word realization fail; no universal cap follows |
| Level-seven Jacobi | `VERIFIED_SCOPED_FINITE` | Exact rational feasible through cutoff 20; cutoff 28 `UNKNOWN` |
| Finite-primary eigenlattices | `VERIFIED_SCOPED` | Local groups, phases, type, and rootlessness fixed; every rank row survives |
| Binary LCD enumerator | `VERIFIED_SCOPED_RATIONAL` | Exact rational ordinary enumerator survives with distances `14/15`; integral feasibility `UNKNOWN` |

## Exact replay summary

- Wave 123 discovery `5/5` and verifier `6/6` tests pass.  The alternate
  26-set passes diagonal leverage and all 2,340 feature-Gram blocks but
  fails exactly 352 of 4,851 graph-valued pair rows.
- The Jacobi verifier checks module dimension 239, all seven coherent
  Fourier caches, and 5,874 original rows.  Exact rational candidates pass
  at cutoffs `10,12,14,16,18,20`; no cutoff-28 certificate exists.
- Wave 128 discovery `12/12` and verifier `8/8` tests pass.  The derived
  `O^-(k,7)` local type is compatible with every `k=16,18,...,30`.
- Wave 131 discovery `5/5` and verifier `6/6` tests pass.  All 200
  MacWilliams rows hold, but 34 image and 32 dual coefficients are
  fractional.

## Status wall

The projector failures concern displayed formal coordinate families, not
all graph-compatible families.  Finite Jacobi feasibility is a relaxation,
not a lattice.  Local discriminant compatibility is not an integral
eigenlattice construction.  A rational ordinary enumerator is neither an
integral enumerator nor a code.  Bounded searches and timeouts remain
non-evidentiary.

```text
rank 28 excluded:                  NO
rank 30 excluded:                  NO
C4 box K3 motif extended/excluded: UNKNOWN
strict n3 upper bound below 4158:  UNKNOWN
Conway-99:                         UNKNOWN
literature novelty:                UNKNOWN
```
