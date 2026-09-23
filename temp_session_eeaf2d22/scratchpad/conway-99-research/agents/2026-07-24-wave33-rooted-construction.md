# Wave 33: rooted Fano-support construction continuation

```yaml
role: construction
date_utc: 2026-07-24T10:17:37Z
git_commit: b2595baa40d50e9c259051751fe27090bee6a449
claim_label: CANDIDATE
scope: >-
  Exact consequences of the labeled Wave 32 Fano-complement support, plus
  one explicit hostile active-to-Z partial object inside a restricted simple
  2-(15,3,2) design family. No complete graph extension or UNSAT certificate
  is claimed.
inputs:
  attempts/wave33-rooted-construction/input-freeze.sha256: f2f62195ba324f091683732e382ee682abca0e070ed6ae712f7b196c0ac59a04
  attempts/wave33-rooted-construction/protocol-freeze.md: c194b60cfbb9fe7694217e20009944244a719d09cad39b489f7d20cee81c639f
  attempts/wave33-rooted-construction/input-addendum.sha256: 67338e2a4b212660aa5439fc1cd28fb12464f906df9bd715051d61b0520ec107
method: >-
  Derive and check the exact graph block equations with no outside
  automorphism; construct a simple twofold triple design; run bounded
  discovery; and independently verify the retained explicit partial object
  using only the Python standard library.
command: >-
  python attempts/wave33-rooted-construction/exact_check.py
  --partial-certificate
  attempts/wave33-rooted-construction/partial-design-certificate.json
  --output attempts/wave33-rooted-construction/exact-results.json
outputs:
  attempts/wave33-rooted-construction/run-report.yaml: 31f3bd60447155c1956b0686ddc4d5d10ef70a4a3bfed803d2dc077d5fe47c3e
  attempts/wave33-rooted-construction/partial-design-certificate.json: 340e5df716ad63bceba25c745ab04c22ea1a3dca01e939072f09775a5fc5f634
  attempts/wave33-rooted-construction/exact-results.json: ba6640eacd041bc8349024a1d3f13e3d74bd67cdad64d2d78c9a94927319c496
  attempts/wave33-rooted-construction/bounded-search-manifest.json: 64024b16bee8e24d7a3f6b3c9a2d101b7c36f2a1fa5a638cfae476d0d750e955
limitations:
  - Discovery cannot self-promote to VERIFIED.
  - The retained object fails ten support-group/point equations and supplies
    no active-active edge set.
  - The active-active quadratic block and full rooted endpoint layer are not
    checked.
  - The MILP timeout and all other nonhits have no negative status.
  - Graph extension, rooted n3=708, Conway-99, and novelty remain UNKNOWN.
```

## Frozen domain

The exact labels, equations, certificate standards, and status wall were
frozen in `protocol-freeze.md` before construction search and before any
inspection of Wave 33 sibling packages. The fixed labeled support has
vertices `P0,...,P6,R0,...,R6`; its cross edge is

```text
popcount((p+1)&(r+1)) odd.
```

The 85 outside labels are the 28 support edges `E`, two copies over each of
the 21 support nonedges `N`, and 15 zero-support vertices `Z`. No outside
orbit, stabilizer, lexicographic representative, or graph automorphism is
imposed.

The correction ledger narrows the phrase "complete finite labeled domain":
the three frozen block equations are complete for the labeled
`srg(99,14,1,2)` graph extension, but they are only a relaxation of the full
rooted `n3=708` endpoint, whose projector/lattice/tensor/Schur conditions
remain separate.

## Exact reduction

The standard-library checker proves directly from

```text
A_S B + B D = -B + 2J
```

that every one of the 70 active outside vertices must have nine active
neighbors and three Z neighbors. Every Z must have fourteen active
neighbors, no Z neighbor, and exactly two neighbors in each of the fourteen
support groups. The active graph would therefore have 315 edges, the
active-to-Z layer 210 edges, and the full graph 693 edges.

If the Z-Z quadratic SRG entries are also enforced, the 70 active-to-Z
neighborhoods are triples on 15 points in which every point occurs fourteen
times and every pair occurs twice. This is a `2-(15,3,2)` design condition.
The package gives an explicit simple example: the union of a cyclic
`STS(15)` with bases

```text
(0,1,4), (0,2,8), (0,5,10)
```

and a block-disjoint permuted copy. Simplicity is an explicit search
restriction, not a consequence claimed without loss of generality.

## Retained hostile partial object

The exact certificate contains all 70 labeled active-to-Z triples. Independent
reconstruction checks:

```text
70 active vertices, each Z-degree 3
15 Z vertices, each active-degree 14
210 active-to-Z edges
105 Z pairs, each with exactly 2 common active neighbors
9 of 14 support groups exactly balanced
10 support-group/point violations: five counts 1 and five counts 3
squared support-balance defect 10
```

Thus this is an exact positive certificate only for the named partial layer.
It is deliberately hostile: it already misses ten support-side equations
and supplies no active-active edges. It is not an extendibility certificate.

## Bounded discovery and nonhits

The reproducible SciPy 1.18.0/HiGHS phase-1 MILP encoded all `70!`
bijections of the frozen 70-block design to the 70 labeled active vertices
using 4,900 binaries and 350 equalities. The objective was identically zero.
The 25-second run returned status `1`,

```text
Time limit reached. (HiGHS Status 13: model_status is Time limit reached;
primal_status is None)
```

with no primal point, objective value, node count, or gap. It did not enter
the active-graph phase. The encoding contained the full named restricted
assignment domain; the run did not cover or enumerate it. The timeout has no
mathematical status.

The retained partial object came from nine seeded fixed-budget annealing
restarts. Replaying that discovery produced a byte-identical certificate
with SHA-256
`340e5df716ad63bceba25c745ab04c22ea1a3dca01e939072f09775a5fc5f634`.
Fourteen hostile checker tests pass, including rejection of self-promotion,
missing/duplicate labels, duplicate design blocks, and invalid Z labels.

## Status wall

```text
complete target graph extension: UNKNOWN
complete-domain UNSAT certificate: NONE
full rooted endpoint: UNKNOWN
n3=708: UNKNOWN
Conway-99: UNKNOWN
novelty: UNKNOWN
```
