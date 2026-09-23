# Wave 189 verifier memo: companion-pool separation

```yaml
role: verifier
date_utc: 2026-07-29T02:31:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CANDIDATE
scope: >-
  Conditional refinement of verified Wave186: separation of selected
  multiplicity-three companions from private-label translated extractions,
  and the resulting sharp minimal-cover variable bound Q>=4158.
inputs:
  verification/wave186-star-translation-cover-verifier/package-manifest.sha256: edb833cbed8706f164199d4ecab8ff26757c54dfc46915819e150e17d73fef76
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
method: >-
  Analytic label-set separation, private-label ownership, support
  intersection, capacity-three assignment charging, and exact integer
  cover inequalities. No brute force, LP, graph, code, configuration, or
  isomorphism search.
command: None.
outputs:
  - verification/2026-07-29-wave189-companion-pool-separation-memo.md
limitations:
  - No frozen Wave189 source derivation or source manifest was found.
  - Status therefore remains CANDIDATE rather than VERIFIED.
  - Sharpness is for the stated integer minimal-cover relaxation, not for an
    actual cover, code, graph, or endpoint.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain UNKNOWN.
```

## Preliminary verdict

`CANDIDATE_PASS_AWAITING_FROZEN_SOURCE`.

The proposed disjointness refinement is sound under the verified Wave180 and
Wave186 inputs. Its exact consequence is

```text
Q>=4158.
```

This improves the verified Wave186 nonedge-circuit bound `Q>=3696` by exactly

```text
4158-3696=462.
```

No clean-room package is created because no frozen Wave189 source derivation
exists.

## 1. Notation and minimal-cover constraints

Let an inclusion-minimal family of nonedge-realizing short circuits cover the

```text
C=4158
```

nonedges. Let `n_i` be the number of selected circuits with complete
realization-set size `i`, and let `p_i` be the number of private labels owned
by selected type-`i` circuits. Then

```text
p_1=n_1,
n_2<=p_2<=2n_2,
n_3<=p_3<=3n_3,
n_1+p_2+p_3<=C.
```

The selected label incidence covers every nonedge:

```text
n_1+2n_2+3n_3>=C.                                (1)
```

Every nonprivate label has selected incidence at least two, so

```text
n_1+p_2+p_3
 >=2C-(n_1+2n_2+3n_3),
```

or equivalently

```text
2n_1+2n_2+3n_3+p_2+p_3>=2C.                     (2)
```

All variables are nonnegative integers.

## 2. Type-two assignments

For each private label of a selected type-two checkerboard conic, verified
Wave186 translates at the two endpoints and extracts one cross circuit from
each translated support.

The two translated supports have profiles `6+2` and `2+6` and intersect in
exactly two coordinates. A circuit common to both would have support of size
at most two, contradicting the verified dual distance at least four.
Therefore:

```text
each type-two private label gives two distinct extraction assignments.
```

Both extracted circuits realize the private label and differ from its selected
owner, hence lie outside the selected cover.

## 3. Type-three assignments

For a selected type-three circuit and any private leaf label, Wave186 gives:

1. the canonical companion, which realizes the selected circuit's same three
   labels; and
2. a circuit extracted from the `3+6` leaf-translate support.

The leaf support meets the weight-four member in only three coordinates and is
disjoint from the weight-five member. Dual distance four therefore prevents
the extracted leaf circuit from equaling either canonical member. Thus:

```text
each type-three private label gives one noncompanion leaf assignment,
and every selected type-three circuit gives one distinct companion.
```

The same leaf circuit may serve several private labels. That collision is
retained below.

## 4. Companion pool and extraction pool are disjoint

Let `H` be the companion pool of the selected type-three circuits. Wave180
makes companionship a fixed-point-free involution, and inclusion-minimality
keeps the companion outside the cover. Hence

```text
|H|=n_3.
```

Let `R` be the outside pool receiving:

```text
2p_2 type-two extraction assignments,
p_3 type-three leaf assignments.
```

Suppose an extraction assigned to a private label `e` equaled a member of
`H`. That companion has exactly the same three-label set as its selected
type-three twin. Since the companion realizes `e`, the selected twin also
realizes `e`.

- If the selected twin differs from the private owner, this contradicts
  privacy of `e`.
- If it is the same selected type-three owner, Wave186's support-intersection
  argument already proves the leaf extraction differs from its own companion.

Therefore

```text
H intersect R is empty.                           (3)
```

This is the new separation. It does not require translated circuits belonging
to different private labels to be distinct.

## 5. Capacity-three charging inside the extraction pool

Every circuit in `R` cross-realizes at most three nonedges. The two
type-two assignments for one label are distinct, so no circuit-label pair is
charged twice. All remaining collisions, including type-two/type-three and
different-leaf collisions, are allowed at maximum capacity three.

Consequently

```text
|R|>=ceil((2p_2+p_3)/3).                          (4)
```

The selected cover, `H`, and `R` are pairwise disjoint. Thus

```text
Q
 >=n_1+n_2+n_3+n_3+ceil((2p_2+p_3)/3)
 = n_1+n_2+2n_3+ceil((2p_2+p_3)/3).              (5)
```

## 6. Exact integer lower bound

Add (1) and (2):

```text
3n_1+4n_2+6n_3+p_2+p_3>=3C.
```

Since every selected type-two circuit has a private label,

```text
p_2>=n_2.
```

Adding the nonnegative quantity `p_2-n_2` gives

```text
3n_1+3n_2+6n_3+2p_2+p_3>=3C.                    (6)
```

Put

```text
A=n_1+n_2+2n_3,
T=2p_2+p_3.
```

Equation (6) is `3A+T>=3C`. Because `A,T,C` are integers,

```text
A+ceil(T/3)>=C.
```

Combining with (5) proves

```text
Q>=C=4158.                                       (7)
```

No fractional relaxation or unhandled ceiling remains.

## 7. Sharpness within the variable system

The bound is sharp for the stated integer constraints. For example,

```text
n_1=n_2=0,
n_3=1386,
p_2=0,
p_3=4158.
```

Then every label is private, both (1) and (2) are equalities, all natural
upper and lower bounds on `p_3` hold, and (5) gives

```text
Q>=2*1386+ceil(4158/3)=4158.
```

This row is only a sharp arithmetic control. It is not asserted to be an
actual circuit cover.

## 8. Scalar consequence and boundary

The 693 verified edge-isolated projective circuits are disjoint from the
nonedge pool. Therefore the candidate refinement would give

```text
total projective short circuit classes>=4158+693=4851,
B_4+B_5+B_6+B_7+B_8+B_9>=2*4851=9702.
```

The independently verified Wave188 bound `18018` is stronger for all short
dual words, but it counts nonminimal words as well as circuits. Equation (7)
is the sharper circuit-level statement.

The exact unresolved gap is procedural rather than algebraic: a frozen
Wave189 source derivation and manifest are required before independent
promotion to `VERIFIED`.
