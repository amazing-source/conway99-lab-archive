# Independent hostile audit

## Verdict

**`VERIFIED_WITH_SCOPE`.**  No correction to Wave 186 is required.  All
four direct frozen input manifests and every file named by them match.  The
source package manifest and input freeze also match.

## 1. The multiplicity classifications apply before equality

Wave 179 verifies that a short circuit cross-realizes at most three pairs.
Wave 180 classifies every circuit whose complete nonedge-realization set has
size three as one member of a canonical weight-four/weight-five companion
pair.  This theorem precedes and does not assume the later lower-bound
equality.

Wave 181 separately excludes shared-center multiplicity two and classifies
every exact multiplicity-two circuit as the checkerboard weight-four conic
on a canonical induced quadrilateral.  Its `Q=2079` assumption is introduced
only in the subsequent equality-face section.  Thus both classifications
are available for arbitrary size-two and size-three members of the Wave 186
minimal cover; no equality premise is being smuggled into the argument.

## 2. Multiplicity-two translates force cross circuits

Fix either nonedge label `{x,y}` of an exact multiplicity-two conic.  Its
checkerboard relation has profile

```text
c=(1,-1,0^5 | -1,1,0^5)
```

on the disjoint stars at `x` and `y`.  Adding a suitable nonzero multiple of
the full `x`-star relation cancels one occupied `x` coordinate and fills the
other five, producing a nonzero relation with profile `6+2` and weight
eight.  Translating at `y` similarly produces profile `2+6`.

Each side of either translated support is a proper star subset.  Because a
point-star has exactly one relation and that relation has all seven
coordinates nonzero, no circuit can lie wholly on one side.  Every nonzero
relation contains a support-minimal dependent subset, so each translated
support contains a circuit meeting both stars.  Since `xy` is a nonedge,
every triangle in those two stars contains exactly one of `x,y`; the circuit
therefore genuinely cross-realizes `{x,y}`.

The translated circuit cannot equal the original conic because the
translation canceled one conic coordinate.  The two translated supports
intersect in exactly two coordinates.  A circuit common to both would have
weight at most two, contradicting the verified dual distance at least four.
Thus the two translates force two distinct other short circuits for the
chosen label.

## 3. Multiplicity-three companion and leaf translate

For an exact multiplicity-three circuit, Wave 180 gives

```text
c_4=z_T+2*sum_(S in A) z_S=0, |A|=3,
c_5=z_T+  sum_(S in B) z_S=0, |B|=4,
```

where `A,B` partition the center star and both circuits have the same three
labels.  The companion involution is fixed-point-free.

For a label `{x,y_i}`, add twice the full `y_i`-star relation to `c_4`.
The shared coordinate `T` cancels, leaving a nonzero relation on the three
`A` blocks at `x` and the six outer blocks at `y_i`.  Both sides are proper
star subsets, so a circuit minimal inside this support must meet both and
cross-realize `{x,y_i}`.  Its weight lies in `4..9`.

This translated circuit differs from `c_4` because it omits `T`, and differs
from `c_5` because their supports are disjoint.  Therefore, whether the
selected triple circuit is `c_4` or `c_5`, its companion and the leaf
translate are two distinct other circuits realizing the chosen label.

## 4. Privacy really puts the forced circuits outside

Take an inclusion-minimal set cover by the complete nonedge-realization sets
of short circuits.  A private label of a selected circuit belongs to no
other selected support.  The two circuits forced in Sections 2 or 3 both
realize that label and have already been proved different from the selected
circuit.  Hence both are outside the selected cover.

This conclusion is not made for nonprivate labels.  If one selected triple
support has several private labels, its single companion can be assigned to
all of them.  Leaf translates belonging to different labels may also
coincide.  The counting below permits all such overlap.

## 5. Private-label and capacity arithmetic

Let `n_i` count selected supports with complete label-set size `i`, put

```text
N=n_1+n_2+n_3,
S=n_1+2*n_2+3*n_3,
C=4158,
```

and let `P_priv` be the number of labels covered exactly once.  Every nonprivate
label has incidence at least two, so

```text
S>=P_priv+2(C-P_priv),
P_priv>=2C-S.
```

The sole label of every selected size-one set is private, or that set would
be redundant.  Therefore the number `p` of private labels owned by selected
size-two or size-three supports satisfies

```text
p=P_priv-n_1>=2C-2n_1-2n_2-3n_3.
```

Each such label supplies two distinct outside-circuit assignments.  An
outside circuit can receive assignments from at most three distinct labels,
because its complete cross-realization set has size at most three.  There is
only one selected owner of a private label, and its two forced circuits are
distinct, so the same circuit-label pair is never counted twice.  Hence

```text
3O>=2p.
```

This is exactly the denominator-three overlap allowance; it does not assume
different private labels have different translates or companions.

## 6. Triple companions are distinct but may overlap the assignment pool

The companion of a selected triple circuit is outside: both members have the
same three labels, so selecting both would make either redundant.
Companionship is an involution, hence companions of distinct selected triple
circuits are distinct.  Therefore

```text
O>=n_3.
```

These companions are not added to the circuits counted through private-label
assignments.  Both constraints apply to the same `O`; any overlap is allowed.

## 7. Exact `8/9` certificate

Combining the private-label lower bound with `3O>=2p`, then doubling, gives

```text
6O+8n_1+8n_2+12n_3>=8C.          (A)
```

The inequality `O>=n_3`, weakened only by adding the nonnegative
`n_1+n_2`, gives

```text
3O+n_1+n_2-3n_3>=0.              (B)
```

Adding `(A)` and `(B)` yields, coefficient by coefficient,

```text
9(O+n_1+n_2+n_3)>=8C,
9(O+N)>=8C.
```

Since the selected and outside classes are disjoint subsets of the `Q`
nonedge-realizing projective short circuits,

```text
Q>=N+O>=ceil(8*4158/9)=3696.
```

The arithmetic control
`(n_1,n_2,n_3,P_priv,p,O)=(0,0,1848,2772,2772,1848)`
makes every displayed scalar inequality an equality.  It is not asserted to
be a cover.

## 8. Enumerator consequence and boundary

Wave 179's 693 edge-isolated projective circuits realize no nonedge, so they
are disjoint from the `Q` family:

```text
projective short circuits>=3696+693=4389.
```

Every projective ternary circuit has exactly two nonzero scalar words:

```text
B_4+B_5+B_6+B_7+B_8+B_9>=8778.
```

Thus `Q=2079` and its conditional Waves 182--185 continuation are excluded.
No incompatible full weight-enumerator upper bound is known.  Rank 11,
endpoint existence, external novelty, and Conway 99 remain `UNKNOWN`.
