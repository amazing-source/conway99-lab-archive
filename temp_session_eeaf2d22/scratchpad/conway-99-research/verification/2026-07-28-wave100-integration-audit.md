# Waves 90--100 shell-bound and alternative-space integration audit

```yaml
role: orchestrator
date_utc: 2026-07-28T03:09:16Z
git_commit: cbb91d1fb7e0f55f9d62a124cd4e4bfbfe739fee
claim_label: VERIFIED
scope: conditional norm-14 shell upper bounds for every hypothetical srg(99,14,1,2), a rank-28 heavier-shell corollary, exact characteristic-seven exterior structure, and one UNKNOWN scalar-theta finite-prefix report
inputs:
  - path: logs/2026-07-28-wave86-public-checkpoint.json
    sha256: 1b6610ff0905d7538adc4a4a12e78634d3cac825620882e0a7baa4ceb1165d34
  - path: attempts/wave90-short-vector-count-upper/package-manifest.sha256
    sha256: f7dda4995714a4216c8a8c00738d8da070ff4f485fb7ddd4596921b309482f88
  - path: verification/wave90-short-vector-count-upper/package-manifest.sha256
    sha256: 87577c23a8b6b3f251de7e3d08b13fcb7a6f30d809c88b35a11d15db5e40201a
  - path: attempts/wave94-general-n3-norm14-bound/package-manifest.sha256
    sha256: 6c6c12690b59c9d86daf25190e3c89b0616aef525498246295974f1d27c30bf8
  - path: verification/wave94-general-n3-norm14-bound/package-manifest.sha256
    sha256: a579aa242fc11583ef38525718cc87954fd86a732032b456939d9904a90603e9
  - path: attempts/wave97-f7-exterior-matroid/package-manifest.sha256
    sha256: dd7869bd8f9041014087cac1e1840763794a4e8d52f2c701262d7ec009515bec
  - path: verification/wave97-f7-exterior-matroid/package-manifest.sha256
    sha256: e7cdd56b40a385ffff42dcdf66f0a0f5b54f60af8472d6a9a9718f7209114992
  - path: attempts/wave98-scalar-positivity-probe/package-manifest.sha256
    sha256: beba870637ccd831963e6bc6a6aa68b70e7a307ce54a86807fde6aa932890f59
  - path: attempts/wave99-transition-pair-moment/package-manifest.sha256
    sha256: e3a30e37bbf08dcd60e4fff7df6f8f4e51780987ba3446e96ff136954e94a9e6
  - path: verification/wave99-transition-pair-moment/package-manifest.sha256
    sha256: 2d94086a0abef0612a445528319e1db4ef54c1fbb7fa361caef6025739aa654f
  - path: attempts/wave100-general-pair-moment/package-manifest.sha256
    sha256: 0dedf60c7994f842887c084bae7f6585f8fc98be568c940efb5b5ea90320bc88
  - path: verification/wave100-general-pair-moment/package-manifest.sha256
    sha256: a4aaed31aa47c26c3d2894985ae4b9602ed0408abe442d1d407510c2c893f916
method: replay all package seals and 113 exact tests, compare discovery and independent derivations, preserve the Wave 97 provenance correction, and publish Wave 98 only as UNKNOWN
outputs:
  - verification/2026-07-28-wave100-integration-audit.md
  - verification/2026-07-28-wave100-orchestrator.md
  - logs/2026-07-28-wave100-public-checkpoint.json
limitations:
  - all shell statements are conditional on a hypothetical target graph
  - the strongest theorem bounds N14 as a function of n3 and does not bound n3
  - no upper bound on N16 or N18 is proved
  - the scalar degree-1000 computation is a finite null result
```

## Verdict

`PASS_WITH_PROVENANCE_CORRECTION`.

All 11 package manifests replay against their sealed files. Fresh local
testing passes 42 discovery tests, 68 verifier tests, and three Wave 98
finite-probe tests: 113 tests total. The discovery and verifier results agree
on every promoted formula and boundary.

Wave 97 requires a repository-provenance correction, not a mathematical
one. Its `R*R=1_perp` identity and quadratic circuit were already immediate
consequences of verified Wave 51. The full Schur cube, `C*C`, compound code
and Smith form, generalized-weight bounds, and orthogonal-orbit reduction
are later project consequences.

## General norm-14 upper bound

For a root `o`, let `f_o` be the number of induced triangular prisms
containing it. A norm-14 vector with `+1` at `o` injects into a
four-point complementary-Fano seed. The second transition moment gives

```text
a14(o) <= 350+floor(5*f_o/2).
```

Every prism is counted at its six vertices, so `sum_o f_o=6P`. Summing,
using `n3+3P=4158`, and then using antipodal parity gives

```text
7*N14 <= 34650+15P = 55440-5*n3,
N14 <= 2*floor((55440-5*n3)/14).
```

This assumes neither rank 28, prism-freeness, nor any graph automorphism.
It improves the earlier verified first-moment coefficient from `-4*n3` to
`-5*n3`. Representative values are

| `n3` | `P` | even `N14` upper bound |
|---:|---:|---:|
| 4158 | 0 | 4950 |
| 4155 | 1 | 4952 |
| 708 | 1150 | 7414 |
| 0 | 1386 | 7920 |

The scalar sum and box constraints on `(f_o)` are sharp. Any further gain
along this route needs graph-specific parity or compatibility information
about the full rooted-prism incidence vector.

## Rank-28 heavier-shell consequence

At `n3=4158`, the general theorem specializes to `N14<=4950`. In the
additional rank-28 row, the verified Wave 86 modular inequality rearranges
to

```text
N14+(37/217)*N16+(43/2387)*N18 >= 1997236/341.
```

Consequently

```text
407*N16+43*N18 >= 2165002.
```

This is a precise target for a packing contradiction, but no verified upper
bound on either heavier shell is currently close enough to finish the row.

## Characteristic-seven exterior structure

Wave 97 independently verifies

```text
R*R*R = F7^99,
C*C = F7^99,
Hilbert function = (1,28,98,99).
```

The second compound `C2(S)` gives a projective self-orthogonal
`[4851,378]_7` code. At rank 28 its Smith form is

```text
1^378, 7^1204, 49^1687, 343^1204, 2401^280, 24010^98.
```

The finite orthogonal embedding is unique up to its ambient orthogonal
group, and norm-16 and norm-18 short classes occupy the same
square-anisotropic projective orbit. Abstract orthogonal geometry therefore
does not separate those two branches; coordinate-weight or incidence data
must be retained.

## Scalar-theta null boundary

Wave 98 reconstructs the Wave 86 formal scalar theta pair with an
independent long-prefix convolution. It remains integral, even, and
nonnegative through degree 1,000. This is published only as `UNKNOWN`.
Finite positivity is not all-orders positivity, and a formal scalar pair is
not a lattice, marked frame, or graph.

## Promotion boundary

```text
general N14 upper bound:                    VERIFIED
endpoint N14<=4950:                         VERIFIED
rank-28 weighted heavier-shell lower bound: VERIFIED
Wave 97 exterior/Schur/Smith formulas:       VERIFIED
Wave 97 repository provenance:              CORRECTED IN AUDIT
Wave 98 degree-1000 scalar probe:            UNKNOWN
upper bound on N16 or N18:                   NOT PROVED
rank r=28 excluded:                          NO
strict upper bound below 4158:               NOT PROVED
rigorous interval:                           708 <= n3 <= 4158
Conway-99 / novelty:                         UNKNOWN
```
