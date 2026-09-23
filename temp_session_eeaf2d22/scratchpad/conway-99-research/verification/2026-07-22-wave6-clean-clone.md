# Wave 6 refined-cover clean-source replay

Verdict: `PASS` for reproducibility at the frozen technical commit. Target
result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T00:03:07Z
git_commit: a066170e452f31efe1e00610b8159a66b825b01f
claim_label: VERIFIED
scope: clean-source tests, standalone refined-cover checking, and byte-identical certificate regeneration
inputs:
  requirements-search.txt: 262f4a1a62fab79ee790da44b9f923b14ed77bafe6e9a6732846953ee9c622ce
  code/matching_orbits.py: 1ba68393c385ef296458555b7c48533786ea592a50bec589be675f95fd550240
  code/sat_model.py: 45f0da74619b31a1a31cc407f702f8e86a0597ee73d29ec268528cd89980aef8
  verification/n3-refined-cover/n3-refined-cover.json: fd9a14193365bf40d3d7bcbe53d56c6f1ffa8a93ca63d5b68506c3354f3b9f8a
  verification/n3-refined-cover/verify.py: cbf0b46a4656b54c0f5b6a65a7f0e549286a5cfb68ca7ee54813b43423d1cb9a
method: fresh no-local source clone, pinned existing virtual environment, full test replay, independent certificate verification, and deterministic regeneration
command: |
  git clone --no-local --branch codex/first-research-wave SOURCE CLEAN
  $python = (Resolve-Path SOURCE/.venv/Scripts/python.exe).Path
  Push-Location CLEAN
  & $python -m unittest discover -s code -p "test_*.py"
  & $python -m unittest discover -s verification -p "test_*.py"
  & $python verification/n3-refined-cover/verify.py
  & $python code/matching_orbits.py --n3-refined --output regenerated.json
  Pop-Location
outputs:
  persistent_output: not_applicable_clean_clone_scratch_only
  code_tests: 48_passed
  verification_tests: 19_passed
  certificate_sha256: fd9a14193365bf40d3d7bcbe53d56c6f1ffa8a93ca63d5b68506c3354f3b9f8a
  regenerated_sha256: fd9a14193365bf40d3d7bcbe53d56c6f1ffa8a93ca63d5b68506c3354f3b9f8a
limitations: the replay used a clean source clone but reused the already pinned project virtual environment; no branch was solved
```

## Results

The clean source tree was checked out at exactly
`a066170e452f31efe1e00610b8159a66b825b01f`. The replay used Python 3.13.14
and the project's pinned `python-sat==1.9.dev7` environment.

- All 48 discovery and encoding tests passed.
- All 19 independent verification and strict-parser tests passed.
- The standalone checker reproduced parent stabilizer order 768, oriented
  stabilizer order 384, twelve parent matching orbits, 945 matchings, 10,395
  refined states, 78 refined orbits, and Burnside sum 29,952.
- Regeneration through `code/matching_orbits.py --n3-refined` produced exactly
  the committed certificate SHA-256
  `fd9a14193365bf40d3d7bcbe53d56c6f1ffa8a93ca63d5b68506c3354f3b9f8a`.

This replay establishes source and certificate reproducibility. It is not a
complete search, and it supplies no target graph or target UNSAT proof.
