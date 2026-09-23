# Waves 71, 74, and 78 modular-theta integration audit

```yaml
role: orchestrator
date_utc: 2026-07-27T23:40:53Z
git_commit: 976098b50ce5194bf4a18aeeceaec1de98a1c5fb
claim_label: VERIFIED_WITH_CORRECTION
scope: conditional level-seven theta reduction and finite signed short-vector packing for a hypothetical srg(99,14,1,2)
inputs:
  - path: logs/2026-07-27-wave72-public-checkpoint.json
    sha256: 2f0e6a712a5d9948c8f518ae7f35f4f35e929c5761ce8cb5abd40b972d308999
  - path: attempts/wave71-modular-theta-extension/package-manifest.sha256
    sha256: f0551b070edafc29d4adf5a380769c9bf4793721634e627ec1babd86b3117b39
  - path: verification/wave71-modular-theta-extension/package-manifest.sha256
    sha256: 0eede2ebc625534360dda3f8e62456e582f5184fd18d3820dd44748de95a5237
  - path: attempts/wave74-short-vector-closure/package-manifest.sha256
    sha256: 4cb63f21352c2268714f72d55e3b37aab69394939bddbe87bbf06f5b918583e5
  - path: verification/wave74-short-vector-closure/package-manifest.sha256
    sha256: eb19bd74e6e6017186f458bcd74390d231bafa9edfa92ad9f7f81e2a1d566612
  - path: attempts/wave78-short-vector-packing/package-manifest.sha256
    sha256: 5537a48b72733345142b4a6aed2c10110e7a42e4a26efe87a0cf674f41f54c0e
  - path: verification/wave78-short-vector-packing/package-manifest.sha256
    sha256: f96134457f81fa7b66d3de73086323f640ec1259f49d134e77584d33056f766b
method: independently reconstruct the level-seven lattice and modular-form calculation, correct the norm-18 boundary, and verify successive exact packing reductions
outputs:
  - verification/2026-07-27-wave78-integration-audit.md
  - verification/2026-07-27-wave78-orchestrator.md
  - logs/2026-07-27-wave78-public-checkpoint.json
limitations:
  - every theorem is conditional on a hypothetical target and verified Wave 66
  - short-vector alternatives remain live
  - no strict n3 upper-bound improvement follows
```

## Verdict

`PASS_WITH_CORRECTION`.

Wave 71's verifier passed ten tests and the discovery suite passed seven.
Thirteen compared mathematical fields contain one correction. Wave 74's
verifier passed seven tests against six discovery tests. Wave 78's verifier
passed ten tests against seven discovery tests. All six sealed manifests
validate.

## Exact level-seven shift

Let `q=44-r`, where `r=rank_F7(2A-J+I)`. The common marked class of the 99
centered frame vectors has order nine and quadratic value `5/9`. Its
isotropic order-three subgroup gives an even index-three overlattice `L` with

```text
L*/L = (Z/7)^q,
det(L)=7^q,
level(L)=7.
```

The scaled dual

```text
K=sqrt(7)L*
```

is even of exact level seven, has determinant `7^(44-q)`, and satisfies
`min(K)>=14`.

Skoruppa's primary theorem reduces `Theta_K` modulo seven to a level-one
modular form of exact weight

```text
154-3q.
```

Independent finite-field row reduction proves:

```text
q=2,4,...,14: min(K)<=28;
q=16:          min(K)<=18.
```

In the hardest row `q=16`, equivalently `r=28`, the exact coefficient
relation is

```text
N14+N16+N18 = 2 mod 14.
```

Through norm 18 these lattice vectors correspond bijectively to integer
vectors `t` with

```text
At=-4t,  sum t_i=0,  sum t_i^2 in {14,16,18}.
```

## Finite signed-support boundary

All mixed-magnitude profiles are excluded. The remaining supports are:

```text
norm 14: seven +1 and seven -1;
norm 16: eight +1 and eight -1;
norm 18: nine +1 and nine -1.
```

Norm 14 forces the complementary-Fano `2-(7,4,2)` incidence graph and an
external `2-(15,3,2)` design. Norm 16 forces a 4-regular bipartite graph on
`8+8`.

Wave 71 discovery retained norm-18 `h=2`. Independent verification closes
it: opposite-support common neighbors saturate capacity 70, so every outside
vertex meets a sign side at most once, while 82 incidences must enter only 81
outside vertices. Hence norm 18 has only `h=0,1`.

Wave 78's four-subset packing proves:

```text
norm 16: outside degree per sign side d<=2;
norm 18: outside degree per sign side d<=3.
```

The exact outside histogram counts become:

```text
norm 16:       1 row,  (n0,n1,n2)=(11,64,8);
norm 18, h=0:  7 rows;
norm 18, h=1:  4 rows.
```

In the `h=1` lane, every `d=3` outside block avoids both endpoints of the
unique same-sign edge.

## Promotion boundary

```text
level-seven neighbor and theta reduction:       VERIFIED
q=16 short-vector congruence:                   VERIFIED
norm-18 h=2 branch:                             EXCLUDED
packing bounds and 1/7/4 histograms:            VERIFIED
labelled outside designs:                       UNKNOWN
all norm-14/16/18 alternatives excluded:        NO
rank r=28 excluded:                             NO
strict upper bound below 4158:                  NOT PROVED
rigorous interval:                              708 <= n3 <= 4158
Conway-99 / novelty:                            UNKNOWN
```
