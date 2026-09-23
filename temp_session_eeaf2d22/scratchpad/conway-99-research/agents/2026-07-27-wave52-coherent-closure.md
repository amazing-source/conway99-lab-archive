# Wave 52 automorphism-free rooted coherent closure

```yaml
role: proof_b
date_utc: 2026-07-27T19:19:35Z
git_commit: 7a77446e8f1aa163170ff91e3b5068482603898b
claim_label: DERIVED
scope: one-root completion-free coherent closure at the prism-free n3=4158 endpoint
inputs:
  attempts/wave52-coherent-closure/input-freeze.sha256: frozen source hashes
method: exact 2-WL on the forced partial triangle structure and its B-cap incidence lift
command: python -B attempts/wave52-coherent-closure/coherent_closure.py --verify attempts/wave52-coherent-closure/exact-result.json
outputs:
  attempts/wave52-coherent-closure/exact-result.json: 75951c260b3a0dda55c2acc324fc6c60322778a72eabb049445d3a87f982e2e9
limitations: one rooted neighborhood only; discovery work; no graph or endpoint resolution
```

## Derived local structure

Fixing one graph triangle gives eighteen other incident triangles partitioned
as `3K6`. For any two of the six-petal sectors, the `B` relation is forced to
be a simple bipartite 2-factor: each petal has two `B` and four `C` neighbors
in that opposite sector. Relation `D` does not occur inside this rooted
19-triangle set.

The key point is not a symmetry assumption. For an external point `x` of an
`a`-petal, the nonadjacent pair `x,b` has common neighbors `a` and one point
in a unique `b`-petal. The two external points of the `a`-petal hit distinct
`b`-petals, because hitting the same petal would make a triangular prism.

## Coherent closure

The uncompleted 19-triangle pair coloring has six colors and is already
2-WL-stable. It yields no finer forced relation.

To retain the exact degree caps, I built a completion-free incidence object
with 19 triangle nodes, all 108 possible cross-sector `B` choices, and 36
exact-two cap nodes. Its exact 2-WL closure refines from 26 to 47 colors in two
proper rounds. The diagonal classes remain the four object roles with sizes
`1,18,36,108`; no individual petal, cap, or `B` choice is forced. Every stable
intersection number is integral.

Explicit bipartite 2-factor completions satisfy all caps. The four possible
cycle partitions for one sector pair are `(6)`, `(4,2)`, `(3,3)`, and
`(2,2,2)`. Across 64 canonical triples of these profiles, completed closures
produce 39 fingerprints and color counts from 8 to 361. Therefore any further
colors obtained after selecting a `B/C` completion are conditional on that
selection.

## Disposition

This is a useful null result, not a breakthrough:

```text
new forced intersection/integrality obstruction: no
positive local-cap control:                       yes
completion dependence:                            yes
prism-free endpoint:                              UNKNOWN
Conway-99:                                        UNKNOWN
```

A coherent-configuration continuation must couple two or more overlapping
roots, or add point-level SRG constraints that actually restrict the three
local 2-factors. Refining one arbitrarily completed root cannot close the
endpoint.

