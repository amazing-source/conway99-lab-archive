# Wave 189 verifier memo: exact-three orbit closure

```yaml
role: verifier
date_utc: 2026-07-29T02:15:43Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CANDIDATE
scope: >-
  Conditional exact-three orbit-closure and translated-support packing
  refinement of the Wave189 companion-pool separation, yielding the
  integer circuit bound Q>=4851.
inputs:
  agents/2026-07-29-wave187-multiplicity-one-star-translation-proof-a.md: c171920d797056e883a365489f4bf218ea4fc50a8bdf1d6a8e632a2ae897257d
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave186-star-translation-cover-verifier/package-manifest.sha256: edb833cbed8706f164199d4ecab8ff26757c54dfc46915819e150e17d73fef76
method: >-
  Analytic orbit closure, private-label and assignment-incidence charging,
  Wave180 companion involution, and an exact integer linear certificate.
  No brute force, LP, graph, code, configuration, or isomorphism search.
command: None.
outputs:
  - verification/2026-07-29-wave189-exact-three-orbit-verifier-memo.md
limitations:
  - No frozen Wave189 source derivation or source manifest exists.
  - The multiplicity-one outside-circuit lemma is DERIVED_PENDING_INDEPENDENT_VERIFICATION.
  - Status therefore remains CANDIDATE rather than VERIFIED.
  - Sharpness is for the integer orbit/cover relaxation, not an actual cover.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`CANDIDATE_PASS_WITH_DEFINITION_REPAIR`.

The exact-three enhancement is sound if the counted set is defined as the
**orbit closure** of the raw noncompanion extraction pool. The label/incidence
argument alone gives

```text
18Q>=20C,
C=4158,
Q>=4620.
```

The additional Wave180 support-profile packing is also sound and strengthens
this to

```text
12Q>=14C,
Q>=4851.
```

If `X` is instead defined to contain only circuits actually returned by the
extraction assignments, the identity `|X|=r+2h` is false when an exact-three
mate is unassigned. This is a wording/set-definition defect, not a defect in
the repaired count.

No clean-room package is created because there is no frozen Wave189 source and
the type-one extraction premise has not yet been independently promoted.

## 1. Raw extraction set and orbit closure

Let `E` be the set of distinct noncompanion outside circuits obtained from
private-label extraction assignments:

```text
type one:   one assignment per private label,
type two:   two distinct assignments per private label,
type three: one noncompanion leaf assignment per private label.
```

The type-two and type-three statements are verified in Wave186. The type-one
statement is the derived singleton affine-translation lemma and remains a
pending premise for promotion.

Put

```text
P=n_1+p_2+p_3
```

for the number of distinct private labels represented in `E`, and put

```text
A=n_1+2p_2+p_3
```

for the number of assigned circuit-label incidences. The two type-two
assignments for one label are distinct, so the same circuit-label pair is
never counted twice.

Now define `X` by closing `E` under the Wave180 companion involution only for
members of exact cross-multiplicity three:

```text
X=E union {mate(c): c in E and c has exact multiplicity three}.
```

This closure definition is essential. A mate need not itself have been
returned by an extraction.

## 2. Added mates are legitimate new circuits

Let `c in E` have exact multiplicity three and let `c*` be its Wave180 mate.
The two circuits have exactly the same three-label set.

### The mate is not selected

The circuit `c` realizes the private label `e` of its selected owner. Hence
`c*` also realizes `e`. If `c*` were selected, privacy would force it to be
the selected owner of `e`.

- A type-one or type-two owner cannot equal `c*`, whose complete
  cross-multiplicity is three.
- For a type-three owner, equality would make `c` the owner's canonical
  companion. Wave186 proves that the noncompanion leaf extraction differs
  from both canonical members.

Thus `c*` lies outside the selected cover.

### The mate is not in the selected-companion pool

Let `H` be the `n_3` canonical companions of the selected type-three circuits.
If `c*` equaled the companion of a selected circuit `d`, applying the
fixed-point-free companion involution would give

```text
c=d.
```

But every member of `E` is outside the selected cover. Contradiction.
Therefore

```text
X intersect H is empty.
```

Both members of every exact-three orbit represented in `E` are genuine,
distinct short circuits in `Q`, even when one member is unassigned.

## 3. Exact decomposition of the closed pool

Let

```text
r = number of circuits in X with cross-multiplicity at most two,
h = number of distinct exact-three Wave180 orbits represented in E.
```

Exact-three mates also have multiplicity three, and distinct companion orbits
are disjoint. Therefore

```text
|X|=r+2h.                                           (1)
```

This equality is valid for the orbit closure. It need not hold for the raw set
`E`.

## 4. Distinct-label and assignment-incidence bounds

A circuit of multiplicity at most two realizes at most two private labels.
Both members of one exact-three orbit have the same three-label set. Hence
the number of distinct private labels satisfies

```text
P<=2r+3h.                                           (2)
```

For assignment incidences, each low-multiplicity circuit receives at most two
distinct label assignments. Each of the two circuits in an exact-three orbit
can receive assignments for at most its three labels. Thus

```text
A<=2r+6h.                                           (3)
```

An orbit mate that is unassigned only lowers the actual incidence count; it
does not invalidate either upper bound.

Divide (2) by three and (3) by six, then add:

```text
P/3+A/6
 <=(2r+3h)/3+(2r+6h)/6
 =r+2h
 =|X|.
```

Equivalently,

```text
6|X|>=2P+A.                                        (4)
```

## 5. Total circuit count

The selected cover contributes

```text
n_1+n_2+n_3
```

circuits. Its disjoint companion pool contributes another `n_3`. Define

```text
B=n_1+n_2+2n_3.
```

The selected cover, `H`, and `X` are pairwise disjoint, so

```text
Q>=B+|X|.                                          (5)
```

From (4) and (5),

```text
18Q>=18B+3(2P+A).                                 (6)
```

## 6. Exact certificate

The private-label incidence inequality is

```text
I=2n_1+2n_2+3n_3+p_2+p_3>=2C.                   (7)
```

Direct coefficient expansion gives the identity

```text
18B+3(2P+A)
 =10I+[7n_1+2(p_2-n_2)+(6n_3-p_3)].             (8)
```

Every term in the bracket is nonnegative:

```text
n_1>=0,
p_2>=n_2,
p_3<=3n_3, so 6n_3-p_3>=3n_3>=0.
```

Equations (6)--(8) therefore give

```text
18Q>=10I>=20C.                                    (9)
```

Since

```text
C=4158=9*462,
20C/18=10C/9=4620,
```

there is no residual ceiling:

```text
Q>=4620.                                          (10)
```

## 7. Sharp arithmetic control

The certificate is sharp for the stated integer cover/orbit constraints. Take

```text
n_1=n_3=p_3=0,
n_2=p_2=2772,
r=0,
h=924.
```

Then

```text
I=3*2772=8316=2C,
P=2772=3h,
A=5544=6h,
|X|=2h=1848,
B=2772,
Q=B+|X|=4620.
```

The selected label incidence is `2n_2=5544`: 2772 labels can be private and
the remaining 1386 labels can each have selected incidence two. All displayed
integer constraints are met.

This row is not asserted to arise from circuits or a graph. It only proves
that `4620` is sharp for the abstract variable/orbit system.

## 8. Geometric packing inside an exact-three orbit

The previous incidence bound allowed as many as six assignment incidences in
one exact-three orbit. The translated support geometry lowers this to three.

Fix a type-two private label `{x,y}`. Wave186 produces one extracted circuit
inside a support of profile

```text
6 on S_x, 2 on S_y
```

and another inside a support of profile

```text
2 on S_x, 6 on S_y.
```

Suppose the first extracted circuit has exact cross-multiplicity three.
Wave180 gives a common center for its three labels. Because `{x,y}` is one of
those labels, the center is either `x` or `y`.

Relative to any included center-leaf label, a Wave180 circuit has support
profile

```text
(3 or 4) on the center star, 1 on the leaf star.
```

The extracted circuit is only a subset of the translated `6+2` support, but
that causes no loophole:

- if centered at `x`, its `(3 or 4)+1` support fits inside `6+2`;
- if centered at `y`, it would require `3` or `4` blocks on `S_y`, while the
  containing support has only `2`.

Thus an exact-three circuit extracted from `6+2` must be centered at `x`.
Symmetrically, an exact-three circuit extracted from `2+6` must be centered at
`y`.

The common center of a three-label Wave180 star is unique. Therefore the two
type-two assignments for one private label cannot lie in the same Wave180
companion orbit.

Type-one and type-three owners supply only one noncompanion extraction
assignment per private label. Since a private label has only one selected
owner, any fixed exact-three orbit receives at most one assignment incidence
for each of its three labels. Hence

```text
A<=2r+3h.                                          (11)
```

No orientation, alternate-center, or support-subset case evades (11).

## 9. Stronger orbit-packing bound

From `|X|=r+2h` and (11),

```text
2|X|=2r+4h>=2r+3h>=A,
|X|>=A/2.                                         (12)
```

Retain

```text
B=n_1+n_2+2n_3,
Q>=B+|X|.
```

Then

```text
12Q>=12B+6A.                                      (13)
```

With

```text
I=2n_1+2n_2+3n_3+p_2+p_3>=2C,
```

direct coefficient expansion gives

```text
12B+6A
 =7I+4n_1+2(p_2-n_2)+(3n_3-p_3)+3p_2.           (14)
```

Every remainder term is nonnegative:

```text
n_1>=0,
p_2>=n_2,
p_3<=3n_3,
p_2>=0.
```

Therefore

```text
12Q>=7I>=14C.                                     (15)
```

Since `C=4158=6*693`,

```text
Q>=7C/6=4851.                                     (16)
```

Again there is no unresolved ceiling.

## 10. Equality conditions and sharp control

Equality in (14)--(16) forces

```text
n_1=0,
p_2=n_2,
p_3=3n_3,
p_2=0.
```

Thus

```text
n_2=p_2=0.
```

Equality `I=2C` then gives

```text
6n_3=2C,
n_3=1386,
p_3=4158.
```

Here

```text
B=2772,
A=4158.
```

Equality in `|X|>=A/2` requires `|X|=2079`. Combining

```text
A=2r+3h=4158,
|X|=r+2h=2079
```

forces

```text
h=0,
r=2079.
```

This integer row satisfies the stated cover/orbit equations and proves that
`4851` is sharp for the strengthened abstract system. It does not construct
the circuits or graph.

## 11. Consequence and promotion blockers

Adding the 693 verified edge-isolated projective circuits would give

```text
total projective short circuit classes>=4851+693=5544,
B_4+B_5+B_6+B_7+B_8+B_9>=2*5544=11088.
```

This remains below the independently verified `18018` bound for all short dual
words, but it is a stronger circuit-level candidate.

Two exact blockers prevent promotion:

1. no frozen Wave189 source derivation or manifest exists; and
2. the type-one outside-circuit lemma used in `P` and `A` is still labeled
   `DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

The orbit-closure and coefficient arguments themselves have no remaining
algebraic gap.
