# Independent Wave191 exact-three residual audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
Q>=6237.
```

The local alternative in which a private type-three leaf extraction is
itself exact-three is `REFUTED`.  No incompatible upper bound follows, so
rank 11 and endpoint existence remain open.

## Clean-room separation and integrity

The independent mathematical payload was generated and frozen with file
SHA-256

```text
9eb61695c70a7ddc5275e30e72e5541ae02414a0b99243f9534c738377d2c13d
```

before the Wave191 source manifest or source files were opened.  The later
source comparison found the same local exclusion, capacity rows,
coefficient identity, and bound.

The frozen source manifest has SHA-256

```text
a0e2697b7e826f5543c2e007a1428633e37fb54e9e8449e73a731a7291f468c4.
```

All seven direct frozen inputs, all nine source entries, and all eight
entries in each of the five premise verifier manifests matched.  The
discovery checker was not imported or executed before the independent
result was frozen.

Two source-account findings are preserved rather than silently repaired:

1. the proof-agent report's final boundary table says
   `new Q=5891 arithmetic row`, an evident stale label; the theorem,
   derivation, exact result, and preceding body all correctly state
   `Q>=6237`;
2. the displayed `Q=6237` null row is a null only for the displayed weak
   scalar inequalities.  It uses capacity two per new residual circuit,
   whereas the separately audited exact-two residual exclusion in Section 6
   rules out that interpretation for an actual residual family.

Neither finding enters or weakens the `Q>=6237` proof.

## 1. Local exact-three raw exclusion

Fix a selected exact-three flag

```text
(x,T),  T={y,u,v},
```

and the private label `xy`.  The three source `A_x` blocks contain the six
distinct common-neighbor incidences.  No block can pair two incidences of
the same leaf type: those two common neighbors are adjacent inside the
block, so their edge would have both `x` and that leaf as common neighbors,
contradicting `lambda=1`.

Thus the three blocks have pair-types

```text
yu, yv, uv.
```

Wave191's owner-center subtraction is sound: an exact-three raw centered at
`x` would leave a nonzero relation on six proper `y`-star blocks.

If it is centered at `y`, its leaf block must be anticomplete to `y`.
Therefore it is the unique source block `S` of pair-type `uv`.  Exactly two
cross edges join `S` to `T`, so in the target flag `(y,S)`,

```text
T in A_y.
```

The only companion member contained in the leaf support is consequently
the weight-five member `c5`.  Subtracting `2c5` from the all-two leaf
relation leaves coefficient word

```text
(2,2 | 2,2)
```

on the four canonical quadrilateral blocks through the two common
neighbors of `xy`.

The independently verified Wave181 canonical Gram has projective kernel

```text
(1,2 | 2,1).
```

The all-equal word has Gram image `(2,2,2,2)`, not zero.  Hence it cannot be
a true relation on that support.  This contradiction excludes the
leaf-centered case as well:

```text
every type-three raw leaf extraction is exact-one or exact-two.       (1)
```

## 2. Joint exact-one occupancy

Use the frozen raw-pool notation

```text
A=n1+2p2+p3,
delta=2r+3h-A,
```

and let `r1` count the exact-one low raw circuits.  Put

```text
t=number of type-three raws on exact-one circuits,
u=r1-t.
```

By (1), the remaining `p3-t` type-three raws are exact-two and force
Wave190 residual assignments.

Exact-one old circuits cannot absorb a residual.  In the old exact-two and
exact-three pools, the number of unused combined circuit-label slots is
exactly

```text
delta-r1.
```

If `Z` is residual assignment incidence outside every old pool, then

```text
Z
 >=(p3-t)-(delta-r1)
 =p3+u-delta,

p3+u<=delta+Z.                                    (2)
```

This count does not reuse a circuit-label pair.  A private type-three label
has one raw extraction, and its residual differs from that extraction.
Both members of an exact-three orbit share a three-label set, so the pair's
combined capacity is three rather than six.

## 3. Orbit closure of genuinely new residuals

Close every new exact-three residual under the Wave180 companion
involution.  If the new pool has `y` low circuits and `g` complete
exact-three pairs, then

```text
Y=y+2g
```

counts its circuits and its assignment capacity is at most

```text
2y+3g<=2Y.
```

An added mate cannot collide with the orbit-closed old raw pool.  Privacy
excludes the selected and selected-companion pools.  Equation (2) gives

```text
p3+u<=delta+2Y,
delta+2Y>=p3.                                     (3)
```

## 4. Both type-two translates are non-exact-two

For a private label of a selected type-two circuit, the selected owner is
already the unique Wave181 exact-two circuit through that label.  Wave186's
two outside translates are distinct from the owner, so neither can be
exact-two.

The `t` exact-one circuits occupied by type-three raws are unavailable to
type two.  At most the remaining `u` exact-one circuits and the `3h`
exact-three orbit-label slots can receive the `2p2` type-two assignments:

```text
2p2<=u+3h.                                        (4)
```

Eliminating `u` between (2)--(4),

```text
delta+3h+2Y>=2p2+p3.                              (5)
```

The split prevents double charging the same exact-one slot.

## 5. Coefficient certificate

The disjoint pools give

```text
Q>=B+A/2+delta/2+h/2+Y,
B=n1+n2+2n3.
```

Equations (3) and (5) enter through the exact decomposition

```text
delta/2+h/2+Y
 =(delta+2Y)/3+(delta+3h+2Y)/6
 >=p2/3+p3/2.
```

Therefore

```text
12Q
 >=18n1+12n2+24n3+16p2+12p3

 =9I+6(p2-n2)+p2+3(p3-n3)
 >=18C.
```

Here `I>=2C`, `p2>=n2`, and `p3>=n3`.  With `C=4158`,

```text
Q>=3C/2=6237.
```

Adding the 693 verified edge-isolated projective circuits gives at least
6,930 projective short circuits and 13,860 scalar circuit words.  Wave188's
verified 18,018 bound for all short words remains numerically stronger
because it includes nonminimal words.

## 6. Wave192 lever, not used here

Suppose a type-three raw is exact-two.  Wave181 identifies it as the unique
checkerboard circuit `r_e` through its private label `e`.  A Wave190
residual crosses `e` but its support omits coordinates of `r_e`.

If that residual circuit were exact-two, Wave181 uniqueness would force it
to equal `r_e`, impossible because `r_e` is not contained in the residual
support.  Therefore

```text
such a residual has exact multiplicity one or three.
```

This statement passes the audit but is deliberately not used in the
`Q>=6237` certificate.  It is recorded as a possible Wave192 refinement.
In particular, it prevents the source's displayed arithmetic null row from
being promoted to a null control for all currently known structure: that row
uses `Y=1039` to absorb 2,078 new residual assignments at capacity two per
circuit.

## Reproducibility and boundary

```text
independent math replay:  PASS
independent full replay:  PASS
independent tests:        7/7 PASS
source replay:            PASS
source tests:             6/6 PASS
all frozen hashes:        PASS
```

No graph, cover, code, SAT, LP, configuration, isomorphism, or enumeration
search was used.  No graph or code is constructed; rank 11, endpoint
existence, strict `n3` improvement, external novelty, and Conway-99 remain
`UNKNOWN`.
