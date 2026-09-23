# Independent hostile audit

## Verdict

`VERIFIED_WITH_SCOPE`.

The frozen Wave 188 lower bound survives clean-room reconstruction. The result
is conditional on the verified prism-free rank-11 endpoint model and counts
projective dual words, not only circuit supports.

## 1. Integrity and separation

The verifier freezes the Wave 188 source manifest and the five direct verified
prior manifests. Every file named by all six manifests is hashed. The
independent checker does not import or execute the discovery checker.

## 2. The affine orbit has at least three short classes

For a selected cross circuit `c`, write the coefficient frequencies on its two
disjoint stars as

```text
(a_0,a_1,a_2), (b_0,b_1,b_2).
```

Both zero frequencies are positive because a circuit meeting both stars cannot
contain an entire seven-star circuit. The nine affine words have weights

```text
14-a_i-b_j.
```

The clean-room census imposes exactly:

1. both triples sum to seven;
2. `a_0,b_0>=1`;
3. the selected base weight is in `4..9`; and
4. every affine weight is at least four, by the verified dual distance.

There are 438 ordered profiles. Their numbers of short affine words are

```text
3: 36 profiles
4: 140 profiles
5: 226 profiles
6: 36 profiles.
```

Thus the minimum is three.

These are projective classes, not merely nine coefficient pairs. In the
abstract basis `c,s_x,s_y`, the representatives are `(1,alpha,beta)`.
Projective normalization fixes the first coordinate, so all nine are nonzero
and projectively distinct.

## 3. Capacity is a support statement

Let a short word realize `{x,y}` and have at least two support blocks in each
star. A second realization sharing `x` would force every `y`-side block to
contain one fixed edge, contradicting `lambda=1` once there are two such
blocks. The same holds with `x,y` reversed.

For a disjoint second realization, every block has one of four endpoint
patterns. At most one triangle realizes each pattern, again by `lambda=1`.
Hence the support has at most four blocks. It follows that:

```text
both sides >=2, weight 4:  capacity <=2
both sides >=2, weight >4: capacity =1.
```

This uses no circuit extraction and applies directly to translated relation
words.

## 4. One-block alternatives

If the one-block side is `T={y,u,v}`, the relation puts `z_T` in `E_x`.
Because `xy` is a nonedge, `x` cannot be adjacent to both `u,v`. If it is
adjacent to exactly one, the already verified shared-center pairing argument
has profile

```text
five 1s, two 2s.
```

Its square sum is `7=1 mod 3`, contradicting projector singularity. Therefore
`x` is anticomplete to `T`.

The clean-room reconstruction of the local two-dimensional relation space has
four projective directions of weights

```text
4,5,7,8.
```

The weight-seven direction is the star only. The three cross directions have
weights `4,5,8` and realize the same anticomplete triple. This explicitly
includes the weight-eight noncircuit required by the new word count.

## 5. Type-one contribution

Every selected type-one circuit has at least two other short affine words.

- If neither has a one-block side, both assignments have capacity at most two,
  so maximum reuse still gives one outside word per selected type-one circuit.
- If a one-block alternative occurs, all three `4,5,8` triple words are
  available. They differ from the exact-multiplicity-one selected circuit and
  each has capacity three, again giving one outside word per selected circuit
  under maximum reuse.

The two pools cannot collide because their complete realization
multiplicities differ. Privacy keeps every assigned word outside the selected
cover.

## 6. Type-two and type-three words

For a selected checkerboard conic, the profile relative to either label is

```text
(5,1,1) | (5,1,1).
```

The two nonzero translations at either endpoint give four distinct projective
axis words. Their profiles are two copies each of `6+2` and `2+6`, all of
weight eight. Section 3 makes each exact-singleton for that private label.
Thus type two contributes `4p_2` outside words.

For a selected triple, the local cross directions are weights `4,5,8`.
Whichever of the two circuits is selected, the companion and the weight-eight
noncircuit are outside. Different complete triple-label sets distinguish these
base orbits, giving `2n_3`.

Translating the weight-four member by a private leaf star cancels `T` and
gives profile `3+6`, weight nine. It is exact-singleton by Section 3, giving
another `p_3`.

## 7. Collision audit

The verifier checks all ten pairs among:

```text
type1 generic, type1 triple, type2 singleton,
type3 singleton, type3 base.
```

Different complete realization multiplicities exclude most collisions.
Two exact-singleton words can agree only if their labels agree, which would
give two selected owners of a private label. A type-one triple word cannot
equal a selected type-three base-orbit word: the selected triple circuit would
cover the type-one private label. The selected cover is also disjoint from
every added family by privacy; the type-three companion is outside by cover
minimality, and the weight-eight base word is not a circuit.

Therefore

```text
O >= n_1+4p_2+p_3+2n_3.
```

## 8. Exact count

Minimality gives `p_2>=n_2`. Private-label incidence gives

```text
2n_1+2n_2+3n_3+p_2+p_3 >= 2C,  C=4158.
```

The selected cover plus outside words gives coefficient row

```text
2n_1+n_2+3n_3+4p_2+p_3.
```

Subtracting the private-label row leaves

```text
3p_2-n_2 >= 2n_2 >=0.
```

Hence the nonedge-realizing projective word count is at least

```text
2C=8316.
```

The hostile triple-only row is an equality control:

```text
n_3=1848, p_3=2772
3n_3+p_3=8316.
```

Adding the 693 verified edge-isolated projective circuit words gives 9009
projective classes. Each ternary projective class has two nonzero scalar
representatives, proving

```text
B_4+B_5+B_6+B_7+B_8+B_9 >= 18018.
```

## Boundary

No incompatible complete weight-enumerator upper bound is known. The theorem
does not improve `n3`, exclude rank 11, decide endpoint existence, establish
external novelty, or resolve Conway 99.
