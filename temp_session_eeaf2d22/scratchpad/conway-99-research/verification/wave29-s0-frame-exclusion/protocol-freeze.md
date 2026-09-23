# Wave 29 independent-verifier protocol freeze

```yaml
role: verifier
date_utc: 2026-07-24T03:20:27Z
scope: >
  Blindly reconstruct or refute the claimed exclusion of the single lattice
  S0 = K12 orthogonal_sum LAMBDA(F) from the full n3=708 endpoint.
claim_label_at_entry: CANDIDATE
git_commit: d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b
```

The verifier had not opened or executed any Wave 29 discovery artifact before
freezing the following byte hashes. File-name discovery and hashing were the
only pre-freeze reads.

```text
e6ae61331a54d53f2a98712296ebac855f45b46de32ff2ec4d85018f2d8a5045  agents/2026-07-24-wave29-s0-frame-exclusion.md
8cb5b0198ac9e787a8234820e648626dc27f900f53b7511068d5442d06d7a39b  attempts/wave29-s0-frame-exclusion/artifact-manifest.sha256
6a31c4ae0b2c994f4c715ba5118e3b25a052e8b3fc99dea88ea794cb7d9d8dce  attempts/wave29-s0-frame-exclusion/exact_check.py
26dff5f61d6bc6e3d752f596f5c318baee47358f27552e4a0b7e4c3e8a6a5c4f  attempts/wave29-s0-frame-exclusion/test_exact_check.py
7a85c5321b5e91365c246dff7bae9264cc82494da5c866b1b351511099f6638c  attempts/wave29-s0-frame-exclusion/exact-results.json
91fba9dad3bb9d906eb69c06ca97be82ff804296dcb010be3f6749e67beba286  attempts/wave29-s0-frame-exclusion/run-report.yaml
5ddbd25498cf9f7048705e190f81e203d3d21efcc72d1750de2235e419fda1c4  attempts/wave29-s0-frame-exclusion/input-freeze.sha256
bba05cd84c1ac35284c9f8af7d8dd32480f11158ada69195b1bfa61892cad234  attempts/wave29-s0-frame-exclusion/failed-routes.md
```

The two caller-supplied hashes match the independently measured values.

## Postinspection metadata correction

The `git_commit` field above was carried from the parent context and names the
previous public Wave 27 head. After opening the frozen Wave 29 inputs, the
applicable local frozen base was found to be
`74b6f3adcee19ca2b0480258bb7bf51198bd085a`. The audit and run report use
that value. This correction changes no preinspection byte hash and is retained
rather than silently rewriting the entry metadata.

## Required reconstruction

- Prove the row-norm-four block split and the `63/168` count.
- Derive the induced block splitting of `M`, `W`, `Q`, and `B`.
- Derive `det(Q_K)=5` without importing discovery code.
- Check the even-unimodular rank-12 veto.
- Re-derive the row-alphabet equations and trace divisibility.
- Check both AM-GM thresholds exactly.
- Treat `C_K` only as integral and `G_K`-self-adjoint; do not assume it is PSD.
- Use only the consequence that every eigenvalue is greater than `-1/2`.
- Prove the pointwise logarithmic inequality on the entire interval
  `(-1/2, infinity)`, including `(-1/2,0)`.
- Justify that the characteristic pseudodeterminant is a positive integer.
- Reconstruct the final contradiction `det(B_K) >= 3645 > 729`.

## Scope wall

A passing audit may verify only that this particular `S0` cannot participate
in a full endpoint package satisfying the frozen premises. It does not exclude
all determinant-729 lattices, does not change the `n3` bound, does not settle
the Conway 99-graph problem, and makes no novelty claim.
