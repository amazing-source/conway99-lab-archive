# Wave 5 clean-clone replay

Verdict: `PASS` for reproducibility at the frozen technical commit. Target
result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-22T23:16:16Z
git_commit: b075fdd33c0023cbbbebc63469a87f5430c2da34
claim_label: VERIFIED
scope: clean-clone tests, standalone joint-cover verification, and byte-identical regeneration of all 12 N3-branch OPB formulas
inputs:
  requirements-search.txt: 262f4a1a62fab79ee790da44b9f923b14ed77bafe6e9a6732846953ee9c622ce
  code/matching_orbits.py: c216d8a0b15fb9a7da501be07f2b631917e383033c142fa5cc9f3979c498ca1f
  code/sat_model.py: 787fdd808b4a9bfc263cbe820a999612a9ee845f6600b8ddd1bac81a151d5ca5
  verification/n3-joint-cover/n3-joint-cover.json: 58c4994ff0eef9c5e1702840f791d1400c3da71b445e3c217e3704c5e70de172
  verification/n3-joint-cover/verify.py: c3fc65f7d42afa3d84c8a8ea76fb912ca7bb2eb71a222fbb9414158636fc4598
method: fresh local clone, fresh virtual environment, full test replay, independent certificate check, and deterministic OPB regeneration
command: |
  python -m venv .venv
  .venv/Scripts/python -m pip install --requirement requirements-search.txt
  .venv/Scripts/python -m unittest discover -s code -p "test_*.py" -v
  .venv/Scripts/python -m unittest discover -s verification -p "test_*.py" -v
  .venv/Scripts/python verification/n3-joint-cover/verify.py
  1..12 | ForEach-Object { .venv/Scripts/python code/sat_model.py --pair-count 7 --cardinality native --n3 --n3-branch $_ --opb ("logs/local/wave5-clean-replay/branch-{0:D2}.opb" -f $_) }
outputs:
  persistent_output: not_applicable_clean_clone_scratch_only
  code_tests: 43_passed
  verification_tests: 16_passed
  certificate_sha256: 58c4994ff0eef9c5e1702840f791d1400c3da71b445e3c217e3704c5e70de172
  regenerated_formulas: 12_hash_matches
limitations: formulas were generated but not solved exhaustively; no target certificate or complete target proof was produced
```

## Environment

The replay used a fresh clone at exactly
`b075fdd33c0023cbbbebc63469a87f5430c2da34`, Python 3.13.14,
`python-sat==1.9.dev7`, and `six==1.17.0`. The clone remained clean; generated
OPB files were confined to the ignored `logs/local/` directory.

## Results

- All 43 discovery and encoding tests passed.
- All 16 independent validator and strict-parser tests passed.
- The standalone certificate checker reproduced stabilizer order 768, 945
  matchings, 12 orbits, Burnside sum 9,216, and legacy-fiber count 78.
- All 12 OPB formulas regenerated with 14,241,485 bytes and header
  `289338` variables / `291756` constraints.
- Every regenerated SHA-256 matched the independent scout exactly.

| branch | OPB SHA-256 |
|---:|---|
| 1 | `7514f95f4dac05e6b430396c6d41e4d1ee29fa7811297e2289788cb9e927dbfb` |
| 2 | `e2cc79bc2678d5c02804eddb98dfc7b745998150b6ae513d457ab9dd61b61d3d` |
| 3 | `8fc96ad1cd65a3f5e84b8f9ec78afc541c6036dc8bd18af437dea44f8eac2bdb` |
| 4 | `3e975ade479bd08e8025fff0c9569c4c4a3a1f19179c1b3a79f9db5ed7493256` |
| 5 | `f097f3649e51140b502f301d5f2de4c4a5e682e8735b67847b2c7b7f8017249e` |
| 6 | `5093c905da2de07fe5cf9596688ccaf6176643139ab433990f87fb1fcbc99964` |
| 7 | `48b1c7937c90d64c13082a8ceda0ddf30d2d2bd30e2a5ed5b979c06d8946b775` |
| 8 | `80dff7535ca0075bd158f9c7cc70b020376b34553d8d510bae4887c2d8108909` |
| 9 | `39df03cdeed910b1c79080597ab47738e8d7f7d9d16515aefc6423e4302d3bad` |
| 10 | `15d014e9388897f49dd2e9af3e050908121ff108de32729e994125a6af554acc` |
| 11 | `998cc48bfb317de25e497be4585ab4b181cad9aaec9467dc1637297993bb3e70` |
| 12 | `420fc2eb89699e61f4cac0120c5350f0405c2d2dc30269c7bd53c9274322dd62` |

The formulas are reproducible search inputs. Their successful generation is
not a target result, and the bounded proof logs discussed in the audit certify
only `NO CONCLUSION`.
