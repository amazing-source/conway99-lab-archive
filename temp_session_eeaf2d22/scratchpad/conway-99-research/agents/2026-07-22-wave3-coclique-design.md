# Wave 3 coclique/design lane

```yaml
role: proof_b
date_utc: 2026-07-22T21:30:08Z
git_commit: 98ee7b3dac89d57f09c583f83a356b3ef9541b3e
base_commit: d1b6d3d237bac44d10123b7d190c46f092d74eee
integration_commit: 98ee7b3dac89d57f09c583f83a356b3ef9541b3e
claim_label: DERIVED
scope: necessary conditions conditional on an alpha-22 coclique, plus one explicitly restricted cyclic design
inputs:
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
outputs:
  verification/cyclic-design/cyclic-2-22-4-2.json: c31a2a5abe33582569c1ac86016fa1a56ec5d538782714a031d763d8eecf7959
  verification/cyclic-design/verify.py: a92f0d2f1707c0cfb1167f8ea64ae3eb8eac97f76e13f9725b5590339b89334a
  verification/cyclic-design/check_linear_systems.py: 1d6ddbf8e40426c3ed54b9f89845cf13bcb2ac807920cc0bd37842bd4a8e6f78
  verification/cyclic-design/size_hypergraph_relaxation.py: 2cf73a0e630cd08002882a6918c2f0df03173ce163465e6eea595fa5dc4462d3
method: exact matrix algebra, cyclic difference-family construction, finite-field elimination, restricted SAT calibration, and independent reconstruction
command: |
  python verification/cyclic-design/verify.py
  python verification/cyclic-design/check_linear_systems.py
  .venv/Scripts/python verification/cyclic-design/size_hypergraph_relaxation.py
limitations: no compatible outside graph D, no coverage of all designs, no nonexistence proof, and no completed-graph automorphism assumption
```

All statements below were independently checked in the Wave 3 audit. They are
conditional necessary conditions, not a resolution of Conway-99.

## Explicit design certificate

Work in `Z_22`. Develop the following blocks through full translation orbits:

```text
{0,1,3,7}, {0,2,7,16}, {0,3,8,12},
```

and develop `{0,1,11,12}` through its short orbit of length 11. The resulting
77 distinct blocks form a simple `2-(22,4,2)` design. Every point has
replication 14, and the block-intersection histogram is

```text
intersection 0: 1,155
intersection 1: 1,540
intersection 2:   231.
```

The compact certificate and standard-library verifier are under
`verification/cyclic-design/`. This proves that the design equations alone are
consistent; it does not construct the remaining 77 graph vertices.

## Exact projector reduction

Let `N` be the 22-by-77 point-block incidence matrix, `G=N^T N`, and `D` the
adjacency matrix induced outside the coclique. The design and cross-block
equations are

```text
N N^T = 12I + 2J,
N 1 = 14 1,
N^T 1 = 4 1,
ND = -N + 2J.
```

Assume `D` is symmetric, hollow, and Boolean. These equations imply `D1=10 1`.
Define

```text
E = D^2 + D + G - 12I - 2J,
X = 4D + 16I - G.
```

Exact expansion gives the bidirectional identity

```text
X^2 - 28X = 16E.
```

Thus the remaining SRG equation is equivalent to `X^2=28X`. Moreover
`XN^T=0`, `diag(X)=12`, and `trace(X)=924`, so a compatible `X` has spectrum
`28^33,0^44` and rank 33.

Equivalently, the quadratic equations may be replaced by the exact PSD
sandwich

```text
D + 4I >= 0,
33I - 11D + J >= 0.
```

For the reverse implication, the error `E` is supported on `ker N`. The two
bounds confine every eigenvalue `q` of `D|ker(N)` to `[-4,3]`, where
`(q-3)(q+4)<=0`; Booleanity and degree ten give `trace(E)=0`, forcing `E=0`.

## Forced combinatorics

Every design block meets 6 other blocks twice, 40 once, and 30 not at all.
Intersection-two pairs are forced nonedges. A compatible `D` would have 154
intersection-one edges and 231 disjoint-block edges.

For each of the 22 design points, its 14 blocks induce a perfect matching.
These 22 matchings are edge-disjoint and account for the 154
intersection-one edges. The remaining 231 edges split into 77 triangles of
pairwise-disjoint blocks. Those triples form a linear `77_3` configuration:
each block lies on three triples, and two triples share at most one block.
The triples are not mutually vertex-disjoint.

## Restricted exact model and failed routes

For one fixed max-intersection-two design, the 231 intersection-two pairs are
fixed nonedges, leaving 2,695 Boolean edge variables. The equation `ND=2J-N`
gives 1,694 integer linear equations. Adding either `X^2=28X` or the PSD
sandwich is an exact fixed-design model.

For the cyclic certificate, the linear system is consistent with ranks

```text
field  rank
F2     1,386
F3     1,463
F5     1,463
F7     1,463.
```

This says only that no obstruction occurs in these four linear reductions. It
does not exclude another modulus or a nonlinear obstruction. A clean
sequential-counter relaxation had 445,599 variables and 892,122 clauses; its
size and a MiniCard access violation produced no mathematical result.

Compatibility of the cyclic design, the full alpha-22 case, and the original
target all remain `UNKNOWN`.
