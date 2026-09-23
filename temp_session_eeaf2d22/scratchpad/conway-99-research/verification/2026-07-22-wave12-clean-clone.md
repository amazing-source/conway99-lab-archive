# Wave 12 detached clean-source replay

Verdict: **PASS**. A detached clone of the documentation checkpoint reproduced
both full test suites, every focused Wave 12 checker, the external GENREG
download and digest, a byte-identical support certificate, the independent
proof-tree replay, and all five certificate mutations. The clone remained
clean; the unlicensed third-party shortcode archive was ignored rather than
added to Git.

```yaml
role: verifier
date_utc: 2026-07-23T07:13:30Z
git_commit: 32713074557d0c3fa845b111519ef0d690b262c9
claim_label: VERIFIED
scope: clean-source reproduction of the conditional Wave 12 n3=42 exclusion artifacts
inputs:
  verification/2026-07-22-wave12-integration-audit.md: 90021fc6f29cfc4ac0d3df07769ce43b4f270a99a13784ff7491711d15352e70
  verification/n3-42-equality/verify_reduction.py: 8aeec3c8f6f53eb14a8a5da49651c0c2b58cf2e118ecd51157c87af13ee6bf72
  verification/n3-42-equality/build_support_certificate.py: f9c31766827a8be098d000a7b1cda8b1cc1fb2f8d20e981357f1316b9dc6917a
  verification/n3-42-equality/verify_support_certificate.py: 2c3a1a2375c148bdfc3149b521c13910c5b1d6b2d79a049fedec1a7d495def48
  verification/n3-42-equality/n3-42-support-certificate.json: 8115b5f34568a463952afc399bc22db927121f3f1aa28cfc33ae191ea93dc68a
  attempts/wave12-computation/n3-42-cubic-trianglefree-14.g6: 24bfd4964cc4e86554f721ff0f988c5e0bb8fc992b6113f142f09737d3ac90fd
  official_GENREG_14_3_4_scd: 6f3e9cf2b7e0d85c5df59c1638ab9d2fddbfc9905c49b35da01cc892f847e9a0
method: detached local clone; pinned existing Python environment; full unittest discovery; fresh official download; exact certificate regeneration; independent certificate replay; Git cleanliness check
command: |
  git clone --no-hardlinks --local <source-repository> <temporary-clone>
  git -C <temporary-clone> checkout --detach 32713074557d0c3fa845b111519ef0d690b262c9
  python -m unittest discover -s code -p "test_*.py" -q
  python -m unittest discover -s verification -p "test_*.py" -q
  python code/wave12_n3_42_active.py --certificate attempts/wave12-computation/n3-42-size2-active-local-candidate.json
  python code/wave12_n3_42_size2_scout.py --compare attempts/wave12-computation/n3-42-size2-active-local-candidate.json
  python code/wave12_n3_42_size2_caps.py --catalog attempts/wave12-computation/n3-42-cubic-trianglefree-14.g6
  python verification/n3-42-equality/verify_reduction.py
  Invoke-WebRequest -Uri https://www.mathe2.uni-bayreuth.de/markus/REGGRAPHS/SCD/14_3_4.scd -OutFile verification/n3-42-equality/14_3_4.scd
  python verification/n3-42-equality/build_support_certificate.py --scd verification/n3-42-equality/14_3_4.scd --graph6 attempts/wave12-computation/n3-42-cubic-trianglefree-14.g6 --output <scratch-certificate>
  python verification/n3-42-equality/verify_support_certificate.py --certificate verification/n3-42-equality/n3-42-support-certificate.json --scd verification/n3-42-equality/14_3_4.scd --graph6 attempts/wave12-computation/n3-42-cubic-trianglefree-14.g6 --mutations
outputs:
  code_tests: 52 PASS
  verification_tests: 92 PASS
  Python: 3.13.14
  Git: 2.51.0.windows.1
  platform: Microsoft Windows NT 10.0.26200.0
  official_shortcode_records: 110
  independently_classified_disconnected_types: 2
  mandatory_degree_survivors: 4
  support_cap_survivors: 0
  rejected_certificate_mutations: 5
  scratch_certificate_sha256: 8115b5f34568a463952afc399bc22db927121f3f1aa28cfc33ae191ea93dc68a
  committed_certificate_sha256: 8115b5f34568a463952afc399bc22db927121f3f1aa28cfc33ae191ea93dc68a
  clone_git_status: CLEAN
  conditional_n3_lower_bound: 45
  target_result: UNKNOWN
limitations: the source tree was clean and detached, but the already pinned local Python environment was reused rather than rebuilt; GENREG and nauty completeness remain external generator claims; the official shortcode binary has no stated redistribution license and is not committed; this is not a Conway-99 existence or nonexistence certificate
```

## Frozen source and environment

The clone was detached at
`32713074557d0c3fa845b111519ef0d690b262c9`. The interpreter reported Python
3.13.14, Git reported 2.51.0.windows.1, and the host reported Microsoft Windows
NT 10.0.26200.0. The replay reused the project's already pinned local virtual
environment; no package installation or source-tree mutation was needed.

The full discovery suite ran 52 tests and the full verification suite ran 92
tests. Both returned `OK`. Focused replays then independently returned the six
raw profiles, the guarded proof-side bound `n3>=45`, the 112-type construction
census, and the exact support exclusion.

## External catalog and certificate

The official University of Bayreuth `14_3_4.scd` archive was downloaded inside
the clone. Its 871 bytes had SHA-256
`6f3e9cf2b7e0d85c5df59c1638ab9d2fddbfc9905c49b35da01cc892f847e9a0`
and decoded to 110 connected types. The direct small-order census supplied the
two disconnected types, and the exact isomorphism bridge covered all 112
graph6 records.

The regenerated certificate and the committed certificate both had SHA-256
`8115b5f34568a463952afc399bc22db927121f3f1aa28cfc33ae191ea93dc68a`.
The independent checker replayed all four rejection trees, rejected all five
hostile mutations, and reported zero support-cap survivors.

## Cleanliness and status boundary

After the replay, `git status --porcelain` was empty. The downloaded `.scd`
file and Python caches were covered by explicit ignore rules. No third-party
binary or generated scratch certificate entered the repository.

This replay verifies the public computational artifacts for the conditional
exclusion `n3=42`. It does not resolve `srg(99,14,1,2)`, and it does not establish
literature novelty. Conway-99 and novelty remain `UNKNOWN`.
