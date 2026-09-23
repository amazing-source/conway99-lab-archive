# Wave 191 verifier addendum: joint exact-one capacity

```yaml
role: verifier
date_utc: 2026-07-29T02:58:49Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CANDIDATE
scope: >-
  Independent adversarial audit of the joint exact-one capacity refinement
  linking type-three residual assignments with the two type-two raw
  translates. The refinement passes and yields the conditional candidate
  bound Q>=6237.
inputs:
  verification/2026-07-29-wave191-refinement-verifier-addendum.md: 19f660194d78ea80428c40e66054791f10643002318f429b5a5e68fb46018c7c
  verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256: fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4
  verification/wave190-residual-stability-verifier/package-manifest.sha256: 15686d17472fd60122072b3d679980d90d3cfe12fd87e5359344e52e216f1280
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave186-star-translation-cover-verifier/package-manifest.sha256: edb833cbed8706f164199d4ecab8ff26757c54dfc46915819e150e17d73fef76
method: >-
  Exact-one occupancy splitting, combined raw-plus-residual label capacity,
  orbit closure of new exact-three residuals, type-two exact-conic
  uniqueness, and an exact coefficient identity. No discovery code, graph,
  code, SAT, LP, configuration, isomorphism, or enumeration search.
command: None.
outputs:
  - verification/2026-07-29-wave191-joint-capacity-verifier-addendum.md
limitations:
  - The argument is conditional on the frozen prism-free rank-11 endpoint.
  - This append-only memo is not a sealed source-plus-verifier package.
  - The bound Q>=6237 remains CANDIDATE pending separate frozen promotion.
  - Rank 11, the endpoint, external novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`CANDIDATE_PASS`.

The shared exact-one slack must not be charged independently to the
type-three residual row and the type-two raw row.  Splitting its actual
occupancy produces a stronger joint inequality, and every collision and
unused-capacity term is accounted for.

The resulting candidate circuit bound is

```text
Q>=3C/2=6237.
```

## 1. Split the exact-one raw occupancy

Retain the orbit-closed raw pool notation

```text
A=n_1+2p_2+p_3,
delta=2r+3h-A,
```

and let `r_1` be the number of exact-one circuits in its low part.
Every circuit in the raw pool receives at least one raw assignment.
An exact-one circuit receives at most one, so all `r_1` such circuits are
occupied exactly once.

Let

```text
t = number of type-three raw assignments on exact-one circuits,
u = r_1-t.
```

Thus `u` is the number of exact-one raw slots occupied by assignments of
other types.  Both quantities are nonnegative.

The preceding Wave191 local audit excludes exact-three type-three raw
extractions.  Therefore exactly

```text
p_3-t
```

type-three raw assignments land on exact-two circuits and force residual
assignments.

## 2. Old-pool residual capacity

An exact-one old raw circuit cannot absorb any residual:

- it cannot absorb a residual for another label because its complete
  cross-realization multiplicity is one; and
- it cannot absorb the residual for its own raw label because a type-three
  private label has only one raw extraction, and the residual differs from
  that raw circuit.

The exact-two and exact-three portions of the old raw pool have total
combined label capacity

```text
2(r-r_1)+3h.
```

The raw assignments already occupying this part number `A-r_1`.  Hence the
number of still unused combined circuit-label slots is exactly

```text
2(r-r_1)+3h-(A-r_1)
 =2r-r_1+3h-A
 =delta-r_1.                                     (1)
```

There is no repeated raw/residual circuit-label pair.  For a type-three
private label the raw circuit and its residual are distinct, and no second
selected owner supplies another raw assignment for the same private label.
Within one exact-three companion orbit, both members share one three-label
set, so their combined capacity is three, not six.

Let `Z` be the residual assignment incidence that remains outside every old
pool.  From (1),

```text
Z
 >=(p_3-t)-(delta-r_1)
 =p_3+(r_1-t)-delta
 =p_3+u-delta.
```

Equivalently,

```text
p_3+u<=delta+Z.                                  (2)
```

## 3. Orbit closure of the new pool

Close every genuinely new exact-three residual circuit under its canonical
companion involution.  If the closed new pool contains `y` low circuits and
`g` complete exact-three pairs, then

```text
Y=y+2g
```

is its number of projective circuits.  Its residual-assignment capacity is
at most

```text
2y+3g<=2(y+2g)=2Y.
```

An added mate cannot collide with an old orbit, because the old raw pool is
already orbit-closed.  Privacy and the omitted source block exclude the
selected and selected-companion pools.  Thus

```text
Z<=2Y.
```

Together with (2),

```text
p_3+u<=delta+2Y.                                 (3)
```

In particular,

```text
delta+2Y>=p_3.                                   (4)
```

## 4. The same exact-one slots constrain type two

For each private label of a selected type-two circuit, Wave186 gives two
distinct outside raw translates.  Wave181 makes the selected owner the
unique projective exact-two circuit through that label.  Hence both outside
translates are non-exact-two.

The `t` exact-one slots occupied by type-three raws cannot also receive a
type-two assignment.  At most the remaining `u` exact-one circuits can
receive any of the `2p_2` type-two raw assignments.  Every other such
assignment must lie in an exact-three raw orbit, and the `h` orbits have
total raw label capacity `3h`.  Therefore

```text
2p_2<=u+3h.                                      (5)
```

Eliminating `u` between (3) and (5) gives

```text
delta+3h+2Y>=2p_2+p_3.                           (6)
```

No exact-one slot is charged twice in (3) and (6).

## 5. Exact coefficient certificate

The disjoint selected, selected-companion, raw, and orbit-closed new pools
give

```text
Q>=B+A/2+delta/2+h/2+Y,

B=n_1+n_2+2n_3.
```

The residual term has the exact decomposition

```text
delta/2+h/2+Y

 =(delta+2Y)/3
  +(delta+3h+2Y)/6.
```

Applying (4) and (6),

```text
delta/2+h/2+Y>=p_2/3+p_3/2.                     (7)
```

Consequently

```text
Q>=B+A/2+p_2/3+p_3/2.
```

Multiplying by 12 gives

```text
12Q
 >=18n_1+12n_2+24n_3+16p_2+12p_3

 =9I
  +6(p_2-n_2)
  +p_2
  +3(p_3-n_3),

I=2n_1+2n_2+3n_3+p_2+p_3.
```

Every remainder is nonnegative, and `I>=2C`.  Hence

```text
12Q>=18C,
Q>=3C/2.
```

For `C=4158`,

```text
Q>=6237.                                         (8)
```

Adding the 693 verified edge-isolated projective circuits gives at least

```text
6930
```

projective short-circuit classes and therefore at least

```text
13860
```

scalar short-circuit words.  Wave188's verified `18018` bound for all short
dual words remains numerically stronger because it includes nonminimal
words.

## 6. Boundary

The joint-capacity derivation is sound and improves the numerical circuit
bound from the preceding candidate `6048` to candidate `6237`.  It remains
a conditional counting theorem and supplies no incompatible upper bound.

No rank-11 or endpoint exclusion, graph or code construction, strict
improvement of the original graph parameter `n3`, or Conway-99 resolution
follows.
