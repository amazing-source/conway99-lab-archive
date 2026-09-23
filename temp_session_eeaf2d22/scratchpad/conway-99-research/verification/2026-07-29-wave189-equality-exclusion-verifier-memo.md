# Wave 189 verifier memo: exclusion of `Q=4851`

```yaml
role: verifier
date_utc: 2026-07-29T02:15:43Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CANDIDATE
scope: >-
  Conditional exclusion of equality in the Wave189 orbit-packing bound
  Q>=4851 by subtracting the canonical C4 checkerboard from each selected
  triple's 3+6 private-leaf relation.
inputs:
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave186-star-translation-cover-verifier/package-manifest.sha256: edb833cbed8706f164199d4ecab8ff26757c54dfc46915819e150e17d73fef76
  verification/2026-07-29-wave189-exact-three-orbit-verifier-memo.md: 1092f46fa18ea347e4f37f40c0757783ca3ab715b3ad92f451eb9147ad221557
method: >-
  Equality-case saturation, canonical C4 uniqueness, exact F3
  coefficient subtraction, proper-star independence, and exhaustive
  comparison with the equality circuit classes. No brute force, LP, graph,
  code, configuration, or isomorphism search.
command: None.
outputs:
  - verification/2026-07-29-wave189-equality-exclusion-verifier-memo.md
limitations:
  - No frozen Wave189 source derivation or source manifest exists.
  - The underlying singleton extraction/orbit-packing chain remains CANDIDATE.
  - Status therefore remains CANDIDATE rather than VERIFIED.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`CANDIDATE_PASS`.

Conditional on the candidate Wave189 bound and its equality description,

```text
Q=4851
```

is impossible. Hence the strict candidate conclusion is

```text
Q>=4852.
```

No sign, orientation, support-subset, or known-circuit loophole remains.

## 1. What equality forces

Equality in the geometric orbit-packing certificate forces

```text
n_1=n_2=p_2=0,
n_3=1386,
p_3=4158,
r=2079,
h=0.
```

Thus:

1. the 1,386 selected exact-three label sets partition all 4,158 nonedges;
2. every selected triple has all three labels private;
3. the selected circuits and their 1,386 companions contribute 2,772
   circuits;
4. the noncompanion extraction pool has 2,079 circuits of
   cross-multiplicity at most two; and
5. its 4,158 private-leaf assignments saturate the capacity-two bound.

Saturation in item 5 makes every extraction-pool circuit exact
multiplicity two and assigns it to both of its labels. Wave181 gives a
fixed-point-free involution on the 4,158 nonedges and one projective
checkerboard circuit on each of the 2,079 canonical quadrilaterals.
Therefore, for every nonedge `e`,

```text
the private-leaf extraction assigned to e is the unique checkerboard r_e.
```

The complete equality list of nonedge-realizing short circuits is:

```text
1,386 selected Wave180 circuits,
1,386 canonical companions,
2,079 canonical checkerboards.
```

There is no room for another circuit if `Q=4851`.

## 2. The private leaf relation

Fix a private label

```text
e={x,y}
```

owned by the selected Wave180 flag `(x,T)`, where `y` is one vertex of the
leaf triangle `T`.

Write the canonical weight-four relation as

```text
c_4=z_T+2*sum_(S in A) z_S=0,
|A|=3,
```

and normalize the full `y`-star relation as coefficient one on all seven
blocks. The private leaf relation is

```text
w_e=c_4+2s_y.
```

The coefficient at `T` is `1+2=0`. Its support consists of

```text
the three A blocks on S_x,
the six outer blocks on S_y.
```

Every surviving coefficient is exactly `2`. Hence

```text
supp(w_e) has profile 3+6 and weight 9,
T is not in supp(w_e).
```

## 3. Inclusion of the canonical checkerboard

The equality leaf assignment for `e` was extracted from `supp(w_e)`.
Section 1 identifies that extracted circuit with `r_e`. Therefore

```text
supp(r_e) subset supp(w_e).
```

Relative to `S_x,S_y`, the canonical checkerboard has two blocks on each
side. Consequently:

- its two `x`-side blocks lie in `A`; and
- its two `y`-side blocks are among the six outer blocks and omit `T`.

Equivalently, these are the two canonical common-neighbor blocks on each
endpoint side. Their geometric description is not an extra assumption; the
needed inclusion follows directly from extraction inside `w_e`.

## 4. Exact signs

Wave181 fixes the checkerboard kernel, in a suitable block order, as

```text
r_e=(1,2 | 2,1).
```

Thus each endpoint side has one coefficient `1` and one coefficient `2`.
Multiplying the entire relation by `2` only swaps these values and will swap
the two constructions below.

On all nine coordinates of its support,

```text
w_e=2.
```

Consider the two true relations

```text
u_e=w_e-r_e,
v_e=w_e-2r_e.
```

For `u_e`, the two checkerboard coordinates carrying coefficient `2` cancel.
For `v_e`, the complementary two checkerboard coordinates carrying coefficient
`1` cancel. Since each cancellation set contains one `x`-side and one
`y`-side coordinate,

```text
wt(u_e)=wt(v_e)=7,
side profile(u_e)=side profile(v_e)=2+5.
```

Both supports omit `T`. Each omits two coordinates of `r_e`, and the two
omitted pairs partition `supp(r_e)`.

No other cancellation occurs because all non-checkerboard coordinates occur
only in `w_e` with coefficient `2`.

## 5. Circuit extraction from the weight-seven relations

Each nonzero weight-seven relation contains a support-minimal circuit.
Neither support contains all seven blocks of either point-star:

```text
2<7 on S_x,
5<7 on S_y.
```

The full point-star relation is the unique relation on one star and has every
coefficient nonzero. Therefore no circuit contained in either support can be
one-sided.

Every contained circuit meets both disjoint stars `S_x,S_y`. Since `xy` is a
nonedge, every support block contains exactly one of `x,y`. Hence every
contained circuit genuinely cross-realizes `e` and has weight in `4..7`.

## 6. It is not any circuit in the equality list

Let `d` be a circuit contained in either `u_e` or `v_e`.

### Not the checkerboard

Each derived support omits two coordinates of `r_e`, so

```text
supp(r_e) is not contained in supp(u_e) or supp(v_e).
```

Thus `d` is not `r_e`.

Wave181 gives at most one projective exact-multiplicity-two circuit for the
canonical quadrilateral attached to `e`. Therefore `d` cannot be a different
known checkerboard crossing `e`.

### Not a selected triple circuit

The label `e` is private. Hence the only selected circuit crossing `e` is its
owner. Both canonical members of the owner's Wave180 pair contain `T`, while
the derived supports omit `T`. Therefore `d` is not the owner.

### Not a selected companion

Any companion crossing `e` has the same label set as its selected twin. By
privacy, that twin must be the owner. The only such companion is the owner's
canonical mate, which also contains `T`. Thus `d` is not in the selected
companion pool.

### Not an edge-isolated circuit

The verified edge circuits cross-realize no nonedge, whereas `d` cross-realizes
`e`. Hence no edge circuit can equal `d`.

The circuit `d` is absent from the complete `Q=4851` list, a contradiction.
Only one of `u_e,v_e` is needed; their simultaneous construction is a sign and
orientation check.

## 7. Strict consequence and boundary

The equality case is excluded, so integrality strengthens the candidate bound
to

```text
Q>=4852.
```

Adding the 693 verified edge-isolated projective circuits would give

```text
total projective short circuit classes>=5545,
B_4+B_5+B_6+B_7+B_8+B_9>=11090.
```

This remains a candidate until a frozen Wave189 source exists and the full
premise chain, including singleton extraction, is independently promoted. It
does not exclude the endpoint or rank 11.
