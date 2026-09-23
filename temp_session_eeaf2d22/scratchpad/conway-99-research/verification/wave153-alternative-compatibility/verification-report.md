# Independent verification report: Wave153

## Verdict

```text
VERIFIED_WITH_SCOPE:
exact rational null witness for the complete safe-orbit bounded
pair-correlation projection only
```

This verdict is restricted to the sealed Wave153 rational relaxation. It is
not a binary incidence design, a compatible residual graph, an endpoint
construction or exclusion, a strict `n3` upper bound, a Conway-99 resolution,
or an external novelty claim.

## Frozen boundary

Before inspecting the payload, the verifier froze the discovery package
manifest at
`31234fe670e26a534d6087515ec969e7ac1b670190da318dd97cbcdae26ee8d0`
and the compressed exact results at
`af3df69fa2542066cd1089f75f09f16582c0583f0304b60df3b9516d0ff035dd`.
All 22 discovery-manifest entries and all six entries in the discovery input
freeze replayed against their bytes.

The verifier did not import or execute
`attempts/wave153-alternative-compatibility/correlation_polytope.py`.

## Independent reconstruction

The verifier rebuilt all 18 cubic, triangle-free, fibre-labelled component
adjacency matrices from the Wave60 edge lists. For each of the six
permutations of the three fibres, it independently:

1. moved each component's fibre coordinates;
2. minimized its edge mask over the `S4 x S4 x S4` within-fibre relabelings;
3. identified the resulting component type by that canonical mask.

The resulting six type permutations exactly equal the frozen Wave60
coordinate action. Applying them to the 1,140 unordered triples of 18 types
produces 275 disjoint orbits, with exactly the frozen representative, member,
and orbit-size records. Their member indices cover `0..1139` once each.
This is coordinate relabeling; no automorphism of a hypothetical target graph
was assumed.

For each representative, rows were rebuilt in fibre-major order and the 630
off-diagonal entries of

```text
G = 12I - A_X + 2J - blockdiag(J12,J12,J12) - A_X^2
```

were recomputed. Every diagonal is 10, every off-diagonal entry is 0, 1, or 2,
and every off-diagonal row sum is 50.

The verifier partitioned every local vertex pair by its three-fibre count
profile. The six profiles have exactly 21 ordered triples whose aggregate is
`(2,2,2)`. Taking the Cartesian product of all positive-target local pairs in
those profiles enumerates every six-set with:

- two vertices per component;
- two vertices per fibre;
- no zero-target pair.

Candidate uniqueness and every one of those conditions were checked directly
for every representative. Counts range from 15,936 to 27,200 and, after
weighting each representative by its independently rebuilt orbit size, recover
the complete frozen 1,140-triple count distribution.

## Exact witness replay

Every sparse coefficient was parsed as a canonical reduced rational with a
positive denominator. Every candidate index was integral, unique, and in
range, and every coefficient satisfied `0 < x_s <= 1`.

Across all 275 representatives the verifier replayed:

- 173,250 exact unordered-pair equations (`275 x 630`);
- 9,900 exact row margins (`275 x 36`);
- 275 exact total-weight equations, each equal to 60.

The support range is 438 through 462. All per-lane and aggregate maximum,
denominator, support, active-equation, and replay metadata agree with the
independently recomputed values.

## Hostile checks

Nine tests passed. They independently reject mutations to:

- a numerator;
- a denominator;
- a candidate index;
- an orbit position;
- the coefficient upper bound;
- candidate-index uniqueness;
- canonical rational encoding.

The remaining tests confirm that the coordinate action was rebuilt and that
both live manifests verify.

## Resource boundary

The complete replay ran sequentially in 101.91 seconds. Available physical
memory was 26.27% at the start and 28.08% at the end, and the verifier checked
the 15% floor periodically.

## Scope wall

The verified result is a null result for a finite rational projection: this
projection does not rule out any of the 1,140 component triples. Rational pair
marginals do not supply a common 0/1 family of 60 distinct columns. Even such
a binary family would not by itself supply the compatible 60-vertex residual
graph. No stronger conclusion is certified here.
