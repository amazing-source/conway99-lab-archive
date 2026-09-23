# Waves 64--65 alternative-space integration audit

```yaml
role: orchestrator
date_utc: 2026-07-27T22:44:31Z
git_commit: 6dba25f93ba8b0375a6d7057eac4c83e58934fb4
claim_label: VERIFIED
scope: conditional integration of the rooted transition-design and hypergraph-algebra results at n3=4158
inputs:
  - path: logs/2026-07-27-wave63-public-checkpoint.json
    sha256: 0e53832e00e8a1b44a2b6a983160e425cb97c9d64d399d1887440f7f54ba1c0e
  - path: attempts/wave64-rooted-transition-design/package-manifest.sha256
    sha256: b3ab03ee16ea80fbda0e4279090a48174797722843e17b890c2aba509b01ff74
  - path: verification/wave64-rooted-transition-design/package-manifest.sha256
    sha256: dd138310fcaa4e3e2d2989281f9c7487b498ad1d15901403b32919d7018bb905
  - path: attempts/wave65-rooted-hypergraph-algebra/package-manifest.sha256
    sha256: 085b2ecae05f7268080b49e2bff8e719d1d693072f4dd4d32a288e9de6b0a02f
  - path: verification/wave65-rooted-hypergraph-algebra/package-manifest.sha256
    sha256: ed910ace571fee408d5560cf943f125e4c04fe7a9f5fe726e7c7a288f6edf4b5
method: enforce discovery-verifier separation, reconstruct the finite spaces independently, retain solver and symmetry scope walls, and identify the first missing nonlinear compatibility
outputs:
  - verification/2026-07-27-wave65-integration-audit.md
  - verification/2026-07-27-wave65-orchestrator.md
  - logs/2026-07-27-wave65-public-checkpoint.json
limitations:
  - every graph-theoretic statement is conditional on the prism-free endpoint unless explicitly described as a positive control
  - the linear and averaged relaxations are feasible
  - no graph, endpoint exclusion, or strict upper bound below 4158 is obtained
```

## Verdict

`PASS_SCOPED`.

Two clean-room verifiers reproduced the mathematical claims with zero
mathematical mismatches. The Wave 64 verifier passed eight tests and validated
both sealed manifests. The Wave 65 verifier passed seven tests and validated
all eleven discovery-manifest and ten verifier-manifest entries.

The Wave 65 verifier records one procedural limitation: its first visible-file
freeze omitted the hidden `.gitattributes` file. The subsequent independent
manifest audit checked that file byte-for-byte. This does not change a
mathematical result, but it remains public.

## Accepted rooted transition/design formulation

Fixing a root identifies the 84 residual vertices with the edges of

```text
H = K14 - 7K2 = K_{2,2,2,2,2,2,2}.
```

The residual edge set splits structurally into:

- fourteen local perfect matchings on the twelve `H`-edges through each base
  point, giving 84 selected transition edges from 840 allowed variables; and
- 140 three-edge matchings of `H`, giving the 420 selected disjoint-label
  edges.

Independent enumeration verifies 35,560 candidate blocks, the five-type
census

```text
(0,0,3): 6720
(0,1,2): 20160
(0,2,1): 6720
(0,3,0): 280
(1,0,2): 1680,
```

exactly 6,040 allowed transition matchings per base point, and 280
transition-triangle cuts.

The explicit 140-block witness satisfies the block-only master, including
label degree five, pair simplicity, local dichotomy two, relation counts
`(5,74,341)`, and support occupancy `(n0,n1,n2)=(32,96,12)`. It is not an
integral transition/design and not a graph.

The stronger linear master has an exact rational feasible point:

```text
z = 1/120 on type (0,0,3)
z = 1/240 on type (0,1,2)
z = 0 on the other block types
t = 1/10 on every allowed transition.
```

All 1,176 endpoint-profile rows and every other declared linear row vanish
exactly at this point. Therefore no Farkas contradiction exists at this
linear level.

For binary variables, the missing residual closure is

```text
sum_{r != p,q} x_pr*x_qr = 2 - Q_pq - x_pq,
Q_pq = |label(p) intersect label(q)|.
```

Together with the rooted scaffold, pair simplicity, and endpoint profiles,
these equations complete the strongly regular graph equations. They do not
separately impose the global absence of triangular prisms away from the
selected root.

## Accepted hypergraph-algebra restrictions

Write `B=T+D`, where `T` is the transition 2-factor and `D` is the point
graph of the selected 3-uniform linear five-regular hypergraph. If `Z` is its
84-by-140 point/block incidence matrix and

```text
R = Z^T Z - 3I,
```

then independent reconstruction verifies

```text
D + 5I = Z Z^T,
R is 12-regular with local graph 3K4,
lambda_min(R) >= -3,
mult_R(-3) >= 56,
c4(R) = 1260 + c4(D),
1260 <= c4(R) <= 2331.
```

The exact scalar coupling with the target spectrum gives

```text
64/5 <= tr(T E_3) <= 16,
5376 <= tr(B^3 T) <= 5712,
tr(B^4 T) + 3 tr(B^3 T) = 52416.
```

All `43*6=258` scaffold-averaged PSD lanes survive, with exact minimum
`12/5`.

An independently checked 84-point local control satisfies the hypergraph and
local-graph requirements but fails the target `B` moments in degrees four
through six by

```text
+5496, -12020, +239772.
```

This proves that the scalar, averaged, and unlabelled local layer is too weak.
The control is not a rooted-scaffold witness and not a graph candidate.

## Promotion boundary

```text
Wave 64 finite transition/design formulation:     VERIFIED SCOPED
Wave 64 block-only integral witness:               VERIFIED RELAXATION POINT
Wave 64 full linear rational control:              VERIFIED RELAXATION POINT
Wave 65 hypergraph/spectral restrictions:          VERIFIED SCOPED
Wave 65 scalar and averaged obstruction:           NOT OBTAINED
integral transition/design:                        UNKNOWN
entrywise noncommutative Z,T,Q compatibility:      UNKNOWN
full residual codegree closure:                    UNKNOWN
strict upper bound below 4158:                     NOT PROVED
rigorous interval:                                 708 <= n3 <= 4158
endpoint / graph / Conway-99 / novelty:            UNKNOWN
```
