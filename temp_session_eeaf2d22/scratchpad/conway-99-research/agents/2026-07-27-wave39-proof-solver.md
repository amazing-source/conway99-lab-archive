# Wave 39 construction: proof-producing branch-15 micro-shard

```yaml
role: construction
date_utc: 2026-07-27T02:29:20Z
git_commit: 019b78ac9a5170107d105ad4d8fcd27f55dde642
claim_label: CANDIDATE
scope: refined branch 15 with the additional primary-edge polarity x187=1
inputs:
  attempts/wave37-proof-producing-endpoint/branch-15.opb.gz: 7683599142bfb51dc2d461d56fc1820bc58c658ed5167b17b5004473b589933e
  attempts/wave38-solver-harvest/coverage-plan.json: 2de85c3f73d4b12a579b281c10171a47c12e26a323ecdf9617c1a842a81d8bf2
method: generalized-unit certificate plus Exact and strict VeriPB raw/kernel replay
command: see attempts/wave39-proof-solver/run-report.yaml
outputs:
  attempts/wave39-proof-solver/branch-15-x187-positive-certificate.json: 5b3119c9429b06398a7628bac2636763f5e29892f770d90dd2cd92910521c1b6
  attempts/wave39-proof-solver/branch-15-x187-positive.raw.pbp: b2fcb06206d8a09ab636535f0358f6013e5daddaf14b7132180698a2f59340d5
  attempts/wave39-proof-solver/branch-15-x187-positive.kernel.pbp: 5645dded139847ff144e84ddc6dd59e90267a9c585a986f13e20748b773c07a0
limitations: CakePB was interrupted with no output; independent replay is pending; branch 15 and all 33 endpoint cases remain open
```

## Exact reduction

The frozen branch-15 OPB contains the normalization unit `x24=1` and the
refinement unit `x2=1`. Its common-neighbor capacity constraint at source
line 571132 forces the wedge variable `x3591=0`. If the residual primary edge
`x187` were present, source line 106 would require that same wedge to be
present. Therefore branch 15 entails `x187=0`.

This excludes one member of the exhaustive polarity split
`x187=1 | x187=0`. It does not exclude refined branch 15 because the negative
polarity remains open.

## Proof evidence

- Project-local generalized-unit replay: `PASS`.
- Exact pinned binary SHA-256 `842ac70b...`: `UNSATISFIABLE`, 830
  propagations, zero decisions.
- VeriPB 3.0.2 pinned SHA-256 `635b6f2f...`: strict raw replay,
  elaboration, and strict kernel replay each reported
  `VERIFIED UNSATISFIABLE`.
- CakePB: `NO_CONCLUSION_INTERRUPTED`; the lane-owned process was terminated
  and its empty transcript removed.

The claim stays `CANDIDATE` until the formal-kernel and independent-verifier
gates pass. Endpoint proof coverage remains exactly `0/33`.
