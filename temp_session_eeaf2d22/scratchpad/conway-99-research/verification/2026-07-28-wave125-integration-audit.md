# Waves 120, 121, 124, and 125 integration audit

```yaml
role: verifier
date_utc: 2026-07-28T05:53:08Z
git_commit: 127acd31ff7980d3d629009167a2bf7f95150b18
claim_label: VERIFIED
scope: fixed-C4 sum/difference geometry, vector-theta orbit inequalities, primitive scalar C4 Jacobi marking, and one extended conditional motif-SAT run
inputs:
  - attempts/wave120-fixedc4-sumdiff/package-manifest.sha256: e2e35519158556a1810affdee4bc148a333ee95a63557ea1a1e687dfcd883017
  - verification/wave120-fixedc4-sumdiff/package-manifest.sha256: f5ccd78abd93d1851d5d64a2c0198d0fedea8ffcb1b7741e49784d3268eb5076
  - attempts/wave121-vector-theta-orbits/package-manifest.sha256: ab3ede13ea60315885ac077cd8e0b3e7b124f34329d51e82fa2f4d08434cf803
  - verification/wave121-vector-theta-orbits/package-manifest.sha256: effd23d11eb89028f1a78152d9a03392d4363083144109b53f8a868d12f4ce6c
  - attempts/wave124-c4-index70-jacobi/package-manifest.sha256: fbdaa5071229c921fdf652a91eaa895f57ce1d31f726cb4f465f0356a6dfec55
  - verification/wave124-c4-index70-jacobi/package-manifest.sha256: aea9d0a1b66fba381bd98f2d07f54e95e53cd64e537e7a0033bc7f87a045bf46
  - attempts/wave125-long-motif-sat/package-manifest.sha256: 1f86976b5d309d9014995d189d02b27857ea3b574fc70da4b07997446e53a666
method: replay all discovery and independent test suites, compare sealed manifests, and publish only the independently reconstructed scoped claims
command: .venv/Scripts/python.exe -B -m unittest discover -s PACKAGE -p test_*.py -v
outputs:
  - this integration audit
limitations: no vector cap, rank exclusion, strict n3 upper bound, graph construction, or Conway-99 resolution is proved
```

## Replayed evidence

The orchestrator reran 72 exact tests:

- Wave 120: 7 discovery and 11 independent tests;
- Wave 121: 16 discovery and 12 independent tests; and
- Wave 124: 11 discovery and 15 independent tests.

All passed.  The Wave 125 manifest also rehashed exactly.  Its solver result
is `UNKNOWN_TIMEOUT`, not mathematical evidence of existence or
nonexistence.

## Verified scoped conclusions

### Fixed four-cycle geometry

For a doubled alternating coordinate on a fixed induced `C4`, the real
affine minimum is `112/5`.  Integrality plus the graph anchor equations
raise the lattice norm lower bound to 32.  For `r` same-oriented vectors,
the verified aggregate inequality is

```text
norm(x_1+...+x_r) >= 4*r^2+8*r.
```

The exact 40-record formal family satisfies every checked pairwise
sum/difference interval, positive-definite Gram condition,
constant-weight-code restriction, and fixed-anchor condition.  It is not a
family in one graph eigenspace.  Its role is to refute those pairwise
relaxations as a route to the desired cap.

### Vector-theta orbit and scalar marking

The exact-value `O^-(30,7)` orbit inequalities add valid scalar constraints
but leave the previously attained truncated theta optima unchanged.  The
formal even-integral prefixes are not lattices.

For an induced four-cycle `C`, its alternating vector `d_C` is primitive of
norm 20 in `L`; the corresponding vector in `K` has norm 140 and
divisibility seven.  The Jacobi indices reduce from 70 on `K` to 10 on `L`.
Through norm 20, the coefficients at elliptic exponent 28 have the exact
alternating-cycle incidence interpretation.

### Tight frame and modular boundary

Across all 2,079 induced four-cycles,

```text
sum_C d_C d_C^T = 945 I
```

on the 45-dimensional `-4` eigenspace.  Hence

```text
11*sum_r r^2*c_K(n,r) = 70*n*sum_r c_K(n,r),
11*sum_r r^2*c_L(n,r) = 10*n*sum_r c_L(n,r).
```

The full-level `J_22,10` calculation and its signed oldform escape
directions were independently reconstructed.  They occupy only a subspace
of the full level-seven Jacobi space and are not graph-positive.  The
post-verification observation that fifth even moments remove one support
escape remains `CANDIDATE`, not `VERIFIED`.

## Status wall

```text
fixed-C4 affine and integer bounds:       VERIFIED
size-40 pairwise formal null witness:     VERIFIED AS A RELAXATION
vector-theta orbit inequalities:         VERIFIED SCOPED
primitive C4 marking and tight frame:     VERIFIED WITH CLARIFICATIONS
full Gamma0(7) positive cone:             UNKNOWN
Wave125 conditional SAT branch:          UNKNOWN_TIMEOUT
rank 28 or rank 30 excluded:              NO
Conway-99:                                UNKNOWN
```
