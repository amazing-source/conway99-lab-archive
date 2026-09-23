# Wave 204 integration audit

## Verdict

`PASS_SCOPED_WITH_REFUTED_LOCAL_LEMMAS`.

Wave 204 produces one new conditional graph-specific invariant and closes
two proposed local-to-global routes negatively. It does not exclude the
ternary rank-11 branch, exclude `n3=4158`, improve `708<=n3<=4158`, construct
a graph or code, or resolve Conway 99.

## Frozen target and inherited boundary

The target remains the existence of a simple graph with
`srg(99,14,1,2)`. Root-level replay preserved:

```text
n3+3P=4158
708<=n3<=4158
conditional rank-11 Q>=7059
conditional rank-11 projective short circuits>=7752
conditional rank-11 nonzero scalar short-circuit words>=15504
m_(x->y)+m_(y->x)<=5
3n3+4p3<=5|U|
epsilon>=5b
Q>=7060: not proved
```

The replay record is
`verification/2026-07-29-wave204-preflight.md`. It also retains a historical
Wave 175 bibliography input-freeze mismatch as a provenance defect rather
than mathematical evidence.

## Promoted claims

### V1: exact relaxed `b=0` certificate

The verifier checked the complete submitted JSON semantics:

```text
99 centers
14-regular circulant skeleton; complement degree 84
1,287 full flags; 1,200 selected flags
J=3561, delta=3, p3=3123, q=237
selected multiplicities 1^3123, 2^234, 3^3
epsilon=708, L=0, b=0
maximum two-orientation occupancy 3
```

This is `VERIFIED` as an exact relaxed certificate. It is not an SRG and
contains no ternary columns, rank-11 code, circuit cover, or endpoint
realization. It therefore refutes only the restricted implication that the
frozen degree/complement data, local Hilton--Milner families, four-point
fibers, Wave 201 equality row, and Wave 203 slot capacity force `b>0`.
That implication is `REFUTED_WITH_SCOPE`.

### V2: honest block gain and absent center holonomy

For a true selected flag, the only canonical transition supplied by the
frozen data is a triangle-block arrow `S->T` with

```text
g(S->T)=z_T-z_S.
```

This gain is the literal coboundary `dz`, so it telescopes on every genuine
block cycle. The identity is `VERIFIED`.

A center walk `x->y->z` composes only when the incoming and outgoing
triangle blocks at `y` are equal. Wave 203 does not prove this equality or
a total five-slot map. Exact relaxed rank-11 `A6` controls for cycles of
lengths 3, 4, and 5 satisfy the normalized flag relations but have unmatched
intermediate blocks and nonzero projected defects. One-point partial maps
also admit total `S_5` extensions with different monodromy. The center-walk
chaining and determined-`S_5` implications are `REFUTED_WITH_SCOPE`.

### V3: fourth-order adjacent-pair detector

Conditional on the frozen rank-11 endpoint star geometry, for adjacent
vertices let `N` be the `6 by 6` biadjacency matrix between the outer parts
of their star decompositions. With

```text
G=J_6-I_6,  C=J_6+N,
```

exact arithmetic over `F_3` gives

```text
P_xP_yP_x|E_x = NN^T
h_xy=tr(P_xP_yP_xP_y)=tr((NN^T)^2).
```

For the four allowed edge types:

```text
type       6  4+2  3+3  2+2+2
h_xy       0   1    0     0
```

Moreover

```text
tr((wedge^2 P_x)(wedge^2 P_y))=h_xy,
tr((Sym^2 P_x)(Sym^2 P_y))=2h_xy.
```

This conditional adjacent-pair detector is `VERIFIED`. Independently
constructed rank-11 projector pairs with equal pair trace and intersection
dimension but different fourth traces show that those pairwise invariants do
not determine `h`; that implication is `REFUTED_WITH_SCOPE`.

The submitted optional 99-projector controls were source-replayed, not
independently reconstructed before unsealing. They use only 21 directions
for 231 labels and fail seven target premises. Their status remains
`SOURCE_REPLAYED_SCOPED_RELAXED`, not promoted.

## Independent verification

The verifier froze its protocol, implementation, 11 hostile tests, result,
and hashes before opening any Wave 204 submission. After unsealing it used a
second JSON-level checker importing no discovery code. Root replay obtained:

```text
submitted package entries:        32/32 match
submitted tests:                  8/8 + 10/10 + 10/10 pass
source-blind independent tests:   11/11 pass
post-source semantic tests:        5/5 pass
independent total:                16/16 pass
```

The verifier explicitly preserves the blind/source semantic discrepancies;
it does not silently substitute its abstract V1/V2 controls for the stronger
submitted semantics.

Package manifest:

```text
verification/wave204-global-compatibility-verifier/package-manifest.sha256
sha256 48cd018c7f7cebe7f2bc93a6dbd9440422f8dc843bc6c0fa96b29968e440f9c2
```

## Literature boundary

A focused primary-source audit through 2026-07-29 found no later resolution
in the searched sources and no theorem whose hypotheses simultaneously
capture the 231 singular ternary points, zero frame, all 99 star
decompositions, canonical quadrilateral relation, exact-three fibers, and
global overlap transitions. This is bounded non-discovery, not proof of
openness, novelty, or priority.

## Integration boundary

Promoted:

- the conditional adjacent fourth-order detector;
- the definitional triangle-block coboundary;
- the exact relaxed `b=0` certificate and its restricted refutation;
- the scoped refutations of center-walk chaining, determined total `S_5`,
  and pairwise determination of fourth trace.

Not promoted:

- the optional 99-projector relaxed controls beyond source replay;
- any claim that `b=0` occurs in a target graph;
- a count of `4+2` graph edges;
- any nonedge fourth-trace classification;
- rank-11 or endpoint exclusion;
- `Q>=7060`;
- graph existence or nonexistence;
- literature novelty or priority.

## Best next theorem

The most concrete next target is a graph-specific global fourth-order
identity:

> Classify `h_xy=tr(P_xP_yP_xP_y)` for nonadjacent pairs and derive an exact
> row, moment, module, or rank relation for the full `99 by 99` matrix
> `(h_xy)` that is incompatible with every possible distribution of the
> `4+2` edge type in an 11-dimensional endpoint realization.

This theorem must use actual SRG common-neighbor geometry or the 231-column
incidence frame. Pair traces, intersection dimensions, local partial slots,
and abstract repeated-direction projector controls are insufficient.

