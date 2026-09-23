# Waves 56--59 alternative-space integration audit

```yaml
role: orchestrator
date_utc: 2026-07-27T21:30:29Z
git_commit: 4bb1989e9e286b2ec753a855db58ad584e31f63a
claim_label: VERIFIED
scope: conditional integration of closure, star-complement, cross-incidence, and incidence-spectral restrictions at n3=4158
inputs:
  - path: logs/2026-07-27-wave58-public-checkpoint.json
    sha256: 43c5ed4c2981cdc7d99cbae112093e5bb336e8c5be83f900c7962806b819b84e
  - path: attempts/wave59-incidence-spectral-excess/package-manifest.sha256
    sha256: c3d29fb9c55dd28012238d042aa6d863b487e550448aad374e1bdcf55bcf413f
  - path: verification/wave59-incidence-spectral-excess/package-manifest.sha256
    sha256: a660ede44009ed40c20bb1661d54b0b977f1817269b85983777f04aa4a78c574
method: preserve the verified Wave 58 boundary, independently reconstruct Wave 59 before comparison, validate manifests, and enforce the unresolved endpoint wall
outputs:
  - verification/2026-07-27-wave59-integration-audit.md
  - verification/2026-07-27-wave59-orchestrator.md
  - logs/2026-07-27-wave59-public-checkpoint.json
limitations:
  - every new mathematical result is conditional on a hypothetical prism-free endpoint
  - non-distance-regularity is not nonexistence
  - no endpoint case is closed and no strict upper bound below 4158 follows
```

## Verdict

`PASS_SCOPED`.

The clean-room verifier reconstructed every selected Wave 59 quantity without
opening or executing discovery code, found zero mathematical mismatches, and
passed 14 tests including hostile mutations. It made only metadata-level
corrections to the official spelling of Miquel Àngel Fiol and the printed page
on which Theorem 6 is stated.

## Accepted incidence geometry

Let `N` be the 99-by-231 point--triangle incidence matrix of a hypothetical
prism-free endpoint and let `L` be its bipartite incidence graph. Then
`NN^T=A+7I`, and `L` is connected with bidegrees `(7,3)`, order 330, girth
eight, diameter six, and spectrum

```text
±sqrt(21)^1, ±sqrt(10)^54, ±sqrt(3)^44, 0^132.
```

Every point root has layers `1,7,14,84,84,140` and intersection array
`{7,2,6,2,5;1,1,1,2,3}`. Triangle roots have layers
`1,3,18,36,180,60,32`; their distance-four layer splits into 36 relation-B
triangles with two predecessors and 144 relation-C triangles with one.
Therefore `L` is not distance-biregular.

## Accepted triangle-graph geometry

The triangle graph `K=N^TN-3I` is 18-regular on 231 vertices, has diameter
three, and has spectrum

```text
18^1, 7^54, 0^44, (-3)^132.
```

Its exact degree-three predistance polynomial has spectral excess 50 while
the actual excess is 32. The relation-specific defect is

```text
p3(K)-A_D=(A_C-2A_B)/4.
```

The projection residual has normalized squared norm `288/25`. The signed
defect is indefinite, so it is not a positive-semidefinite contradiction.
The binary pair-neighborhood Gram matrix is `153I+10K+A_B`, is at least
`87I`, and consequently has full rank 231.

Exact Ihara--Bass extraction gives
`C8=2079`, `C10=33264`, `C12=250866`, and `C14=2494800`. The relevant
`(7,3;8)` Moore lower bound is only 130 vertices, versus 330 here.

## Promotion boundary

```text
Wave 59 finite conditional identities:            VERIFIED SCOPED
incidence graph distance-biregular:                FALSE
triangle graph distance-regular:                   FALSE
pair-neighborhood Gram rank:                       231
spectral or cage contradiction:                    NONE
simultaneous B and compatible A_Y:                 UNKNOWN
strict upper bound below 4158:                     NOT PROVED
rigorous interval:                                 708 <= n3 <= 4158
endpoint / graph / Conway-99 / novelty:            UNKNOWN
```
