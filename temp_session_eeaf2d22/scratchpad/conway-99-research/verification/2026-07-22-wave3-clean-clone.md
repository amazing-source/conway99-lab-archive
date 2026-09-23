# Wave 3 / N3 clean-clone replay

Verdict: `PASS` for reproducibility at the frozen technical commit. Target
result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-22T22:22:00Z
git_commit: 98ee7b3dac89d57f09c583f83a356b3ef9541b3e
claim_label: VERIFIED
scope: clean-clone replay of committed tests, public finite checks, canonical OPB generation, and pair-2/pair-3 proof certificates
inputs:
  requirements-search.txt: 262f4a1a62fab79ee790da44b9f923b14ed77bafe6e9a6732846953ee9c622ce
  code/sat_model.py: c29744c4835306d576a8625b3951b51815f0a5f806a9c93c6c8eff494639276c
  verification/literature-audit/verify_reimbayev_six.py: 64a517cf6701b8cec68d57eaad30362e4873307f875745ab75ea731d30687fa2
  verification/cyclic-design/cyclic-2-22-4-2.json: c31a2a5abe33582569c1ac86016fa1a56ec5d538782714a031d763d8eecf7959
method: detached clean clone, fresh virtual environment, independent test suites, deterministic regeneration, and two proof checkers
command: |
  python -m venv .venv
  .venv/Scripts/python -m pip install --requirement requirements-search.txt
  .venv/Scripts/python -m unittest discover -s code -p "test_*.py" -v
  .venv/Scripts/python -m unittest discover -s verification -p "test_*.py" -v
  .venv/Scripts/python verification/cyclic-design/verify.py
  .venv/Scripts/python verification/cyclic-design/check_linear_systems.py
  .venv/Scripts/python verification/cyclic-design/size_hypergraph_relaxation.py
  .venv/Scripts/python verification/literature-audit/verify_reimbayev_six.py
  # Run the formula and proof replay blocks from verification/2026-07-22-veripb-calibration.md.
outputs:
  persistent_output: not_applicable_clean_clone_scratch_only
  pair2_proof_sha256: 9e5f7991dd66886424a97a7020a05e3f7e702b6c87a9710e1ff3fe1b24a0d104
  pair2_kernel_sha256: a35302332cd6b55273d626b36d21940488cee3467fee3a22d5c02dfdf406a08d
  pair3_proof_sha256: ad9f8cb98b88ee98e23f77aade39f48a5e28a1cdeec9f154803045075b7504bd
  pair3_kernel_sha256: 4b8264195a538e1088db6ff388bde3e9993a3985f92ac66c687acde768ec3f80
limitations: no target certificate or exhaustive target proof was produced
```

## Environment

The replay used a detached clone at the exact commit above, Python 3.13.14,
`python-sat==1.9.dev7`, and `six==1.17.0`. The three proof-tool binary hashes
matched the pinned values in the VeriPB calibration report.

## Results

- All 35 discovery/model tests passed.
- All 11 independent validator tests passed.
- The cyclic `2-(22,4,2)` certificate, linear systems, modular ranks, and
  relaxation-size calculation passed.
- The clean-room Reimbayev enumeration reproduced 156 unlabeled graphs, 14
  determinant-relevant types, `209286+n3`, and `3n1+n3=4158`.
- Pair-2 and pair-3 OPB formulas regenerated with their committed SHA-256
  values.
- Exact regenerated the pair-2 SAT and pair-3 UNSAT proofs byte-identically.
  Strict VeriPB accepted each raw proof, elaboration regenerated each committed
  kernel byte-identically, strict VeriPB accepted each kernel, and CakePB
  reported `VERIFIED SATISFIABLE` / `VERIFIED UNSATISFIABLE` respectively.
- The unnormalized and N3-normalized target formulas regenerated with hashes
  `c84eb4d82e8c8f848d1d992d7dfdc103360418ad3e893ab836c5be23c29d3001`
  and `ad7a8bf5d76c3f740f3f65fee5b134cf6b8e6720e22fd780916121edd59fd0de`.

The target formulas were not solved exhaustively. Their successful generation
and the small-control proof replay validate infrastructure only.
