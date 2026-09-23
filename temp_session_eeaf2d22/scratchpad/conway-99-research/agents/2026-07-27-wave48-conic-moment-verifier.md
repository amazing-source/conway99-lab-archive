# Wave 48 exact facial-reduction verifier

```yaml
role: verifier
date_utc: 2026-07-27T18:32:36Z
git_commit: e4394aa9172fa97a6dafa9158148c2183603a01b
claim_label: VERIFIED
scope: exact Wave44 affine rank/nullity and eleven complete universal moment kernels
inputs: verification/wave48-conic-moment/input-freeze.sha256
method: independent exact RREF, stacked affine matrix kernels, rank-nullity completeness, modular checks, delayed comparison
command: .\.venv\Scripts\python.exe verification\wave48-conic-moment\verify_exact_faces.py reconstruct
outputs: verification/wave48-conic-moment/{independent-reconstruction.json,verification-results.json}
limitations: no numerical artifacts opened; feasibility and endpoint remain UNKNOWN
```

The independent reconstruction was sealed at
`e2b7c1684cf4681504c303a090fe3b8f9882ddb2a6c514a973fd6686394a10e4`
before the Wave48 face claims were parsed.

Exact results:

- the 170-row Wave44 system has rational rank 93 and affine nullity 116;
- all 170 particular identities and 19,720 nullspace identities pass;
- all eleven universal kernels are complete by exact rank-nullity;
- every active rank agrees modulo three independent primes; and
- all eleven reconstructed kernel subspaces, ranks, nullities, forced-zero
  diagonal sets, and modular ranks agree with the frozen Wave48 face package.

This supports `VERIFIED_SCOPED` only. No floating solver output was opened or
used, and aggregate feasibility, endpoint `n3=4158`, graph construction, and a
strict upper bound remain `UNKNOWN` or `NOT_PROVED`.
