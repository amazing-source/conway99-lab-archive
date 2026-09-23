# Wave 189 proof B: star-local degree seven and companion-orbit packing

```yaml
role: proof_b
date_utc: 2026-07-29T02:18:14Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional rank-11 endpoint: derive the complete degree-seven constraints
  forced by the 99 point-star relations and their edge/nonedge intersection
  pattern; test them against an exact rational complete-enumerator control;
  and adversarially audit a companion-orbit and equality-face refinement of
  the minimal nonedge-circuit cover.
inputs:
  agents/2026-07-29-wave187-code-geometry-proof-b.md: 9da6239381d556084133dbedd0eb9db3071ba3bb907723bb42427c107db49c99
  attempts/wave187-code-geometry-proof-b/exact_check.py: 53053eaf294b32ee4ed736d8323053ebb12b93e4e9edea17b685ab9d430b5c59
  agents/2026-07-29-wave187-multiplicity-one-star-translation-proof-a.md: c171920d797056e883a365489f4bf218ea4fc50a8bdf1d6a8e632a2ae897257d
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave186-star-translation-cover-verifier/package-manifest.sha256: edb833cbed8706f164199d4ecab8ff26757c54dfc46915819e150e17d73fef76
  verification/wave188-affine-star-word-amplification-verifier/audit.md: 1cae5c4bc49bf8e9dda6d20d67a03de3a6dabb7a75f9ba9e22cca159538b68f3
method: >-
  Complete ternary MacWilliams transforms, a five-vertex star-local moment
  polygon, exact Fraction arithmetic, companion-involution closure, private
  label ownership, center-oriented support profiles, and a closed scalar
  packing certificate, and checkerboard residual circuit extraction. No
  graph, code, SAT, cover, configuration, isomorphism, or broad LP search.
command: python -B attempts/wave189-degree7-star-complete/exact_check.py
outputs:
  attempts/wave189-degree7-star-complete/exact_check.py: 0b2281f4071dc1d68456c3b956d016574074e2b3c13a1f3765c564886226a1d5
limitations:
  - The degree-seven null control is rational, not a code or point set.
  - Its three-point Gram census is rational rather than integral.
  - Star-local profiles and low complete moments do not encode a global
    simultaneous realization of all 99 stars.
  - The circuit refinement uses the Wave187 singleton extraction, whose
    source status is DERIVED_PENDING_INDEPENDENT_VERIFICATION.
  - This proof agent cannot promote its own circuit refinement to VERIFIED.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

There are two conclusions.

First, the negative `B_(7,0)` in the Wave 187 hostile control is not
universal.  A new exact nonnegative rational control satisfies the full
one-star degree-seven system, all complete MacWilliams rows through degree
seven, the exact adjacent/nonadjacent star-pair lower rows in degrees
12--14, the ordinary MacWilliams inequalities, and the frozen quadratic
type moments.  It has

```text
B_(7,0)=B_(0,7)=99.
```

Thus these constraints do not exclude the endpoint.

Second, companion-orbit packing followed by an equality-face cancellation
gives the candidate circuit theorem

```text
Q>=4852,
```

where `Q` counts nonedge-realizing projective short circuits.  The proof is
analytic and the scalar system is sharp.  It remains `DERIVED`, not
`VERIFIED`, pending a clean-room audit of the frozen Wave 189 source and the
Wave 187 singleton-extraction input.

## 1. Complete rows forced by the star words

Normalize the 99 point-star relations as all-one words `s_x` of complete
composition `(7,0)`.  Their negatives have composition `(0,7)`.  Therefore

```text
B_(7,0)>=99,
B_(0,7)>=99.                                      (1)
```

The known star intersections give more rows, but in higher total degree.
For an edge `xy`, the two stars meet in their unique block through that
edge.  Their sum and difference give

```text
B_(12,1)>=693,
B_(1,12)>=693,
B_(6,6)>=1386.                                   (2)
```

For a nonedge `xy`, the two stars are disjoint, giving

```text
B_(14,0)>=4158,
B_(0,14)>=4158,
B_(7,7)>=8316.                                   (3)
```

The supports recover the center or unordered center pair, so the words in
each displayed family are distinct.  Equations (2)--(3) are genuine
pair-intersection information, but they do not create another pure
total-degree-seven row.  At degree seven, (1) is the complete forced row.

## 2. The smallest one-star class-resolved system

Fix a primal word of complete composition `(a,b)`.  For each center `x`,
let `(r_x,s_x)` count its symbols `1,2` on the seven blocks of the `x`-star.
Orthogonality to `s_x` and triple incidence of triangle coordinates give

```text
r_x-s_x=0 mod 3,
r_x+s_x<=7,
sum_x r_x=3a,
sum_x s_x=3b.                                    (4)
```

There are exactly twelve allowed local patterns:

```text
(0,0), (0,3), (0,6), (1,1), (1,4), (2,2),
(2,5), (3,0), (3,3), (4,1), (5,2), (6,0).
```

Their convex hull has vertices

```text
(0,0), (6,0), (5,2), (2,5), (0,6)
```

and nontrivial facets

```text
r+s<=7,
2r+s<=12,
r+2s<=12.                                       (5)
```

Consequently every supported primal composition obeys

```text
a+b<=231,
2a+b<=396,
a+2b<=396.                                      (6)
```

Conversely, (6) is sufficient for a rational one-star profile.  Triangulate
the polygon from `(0,0)` and express `(a/33,b/33)` as a nonnegative rational
combination of the two surrounding boundary vertices and `(0,0)`.  If
`L_(a,b)^(r,s)` denotes the resulting aggregate local mass, then

```text
sum_(r,s) L_(a,b)^(r,s)       =99 A_(a,b),
sum_(r,s) r L_(a,b)^(r,s)     =3a A_(a,b),
sum_(r,s) s L_(a,b)^(r,s)     =3b A_(a,b),
L_(a,b)^(r,s)>=0.                              (7)
```

Equations (4), (7), and the twelve-pattern support are the smallest
class-resolved linear system visible from one star at a time.

## 3. Exact rational degree-seven null control

The checker records a 16-cell typed rational distribution:

```text
singular cells:   5, including mass 231 at (36,162)
norm-plus cells:  5
norm-minus cells: 6
```

Every cell and its scalar reverse satisfy (6), and the checker constructs
the rational local profile (7) explicitly.  It then verifies:

```text
B_(r,s)=0 for 1<=r+s<=3,
complete degree 4 = (0,0,positive,0,0),
B_(r,s)>=0 for 5<=r+s<=7,
B_(7,0)=B_(0,7)=99,
all six pair lower rows (2)--(3),
all ordinary B_j>=A_j>=0 for 0<=j<=231.
```

It also verifies the frozen singular/norm-plus/norm-minus factorial moments
through degree two.  The induced degree-three moments admit a nonnegative
rational Gram census with five classes:

```text
three orthogonal pairs,
two orthogonal pairs,
one orthogonal pair,
no-orthogonal plus,
no-orthogonal minus.
```

The exact census satisfies the total-triple, orthogonal-pair incidence,
orthogonal-wedge incidence, and three quadratic-complement equations.  It
is not integral and therefore remains only a relaxation control.

Finally,

```text
B_4+...+B_9
 =303955951136016513013761953327276372487328891
  /2147091333645300550865262629325
 >18018.
```

This proves only that the tested analytic relaxation remains feasible.  It
does not construct the endpoint.

## 4. Companion and extraction pools

Choose an inclusion-minimal cover of the `C=4158` nonedges by projective
short circuits.  Let `n_i` count selected circuits with exact complete
cross-multiplicity `i`, and let `p_i` count their private labels.  Then

```text
p_1=n_1,
n_2<=p_2<=2n_2,
n_3<=p_3<=3n_3,                                  (8)
```

and private-label incidence gives

```text
2n_1+2n_2+3n_3+p_2+p_3>=2C.                     (9)
```

Let `H` be the pool of companions of the selected type-three circuits.
Wave 180 makes companionship a fixed-point-free involution and gives

```text
|H|=n_3.
```

Now choose noncompanion extraction assignments:

```text
one  for each type-one private label,
two  for each type-two private label,
one  leaf translate for each type-three private label.
```

Their total number is

```text
A=n_1+2p_2+p_3.                                  (10)
```

Every extraction is outside the selected cover by privacy.  It is also
outside `H`: if an extraction assigned to a private label `e` equaled the
companion of a selected type-three circuit, its selected twin would have
the same three labels and would also cover `e`.  Privacy excludes a
different owner, while the explicit support comparison excludes the
same-owner type-three leaf extraction.

Close the extraction pool under the Wave 180 involution whenever an
extracted circuit has exact cross-multiplicity three.  An added mate is
outside the selected cover: otherwise privacy forces it to be the selected
owner, making the original extraction its already excluded own companion.
An added mate is outside `H`: otherwise involution would make the original
extraction selected.  Thus the selected cover, `H`, and the closed
extraction pool `X` are pairwise disjoint.

## 5. Center orientation cuts orbit capacity

Write

```text
X = r circuits of multiplicity at most two
    plus h complete exact-three companion pairs,
|X|=r+2h.                                        (11)
```

A low-multiplicity circuit receives at most two assignments.

The crude capacity of a companion pair would be six assignments, but the
type-two support geometry cuts it to three.  For a private type-two label
`xy`, Wave 186 gives translated supports with profiles

```text
W_x: 6 on S_x plus 2 on S_y,
W_y: 2 on S_x plus 6 on S_y.
```

An exact-three Wave 180 circuit has a unique common center and profile
`(3 or 4)+1` relative to that center and any one leaf.  Since its labels
include `xy`, its center is `x` or `y`.  The support `W_x` has only two
`y`-side coordinates, so any exact-three subcircuit in `W_x` must center at
`x`.  Symmetrically an exact-three subcircuit in `W_y` must center at `y`.
The two type-two assignments for one label therefore cannot be companion
mates, because companion mates have the same three labels and the same
unique center.

Type-one and type-three private labels contribute only one extraction
assignment each.  Hence an exact-three companion pair receives at most one
assignment from each of its at most three labels.  Therefore

```text
A<=2r+3h,
|X|=r+2h>=A/2.                                   (12)
```

No distinctness between extractions belonging to different labels is
assumed.

## 6. Closed scalar certificate

The selected cover, `H`, and `X` are disjoint subsets of the `Q`
nonedge-realizing projective short circuits.  Equations (10)--(12) give

```text
2Q
 >=2(n_1+n_2+n_3+n_3)+A
 =3n_1+2n_2+4n_3+2p_2+p_3.                      (13)
```

Multiply (13) by six.  The resulting left row has the exact decomposition

```text
18n_1+12n_2+24n_3+12p_2+6p_3

=7(2n_1+2n_2+3n_3+p_2+p_3)
 +4n_1+2(p_2-n_2)+(3n_3-p_3)+3p_2.              (14)
```

The first parenthesis is at least `2C` by (9), and every term in the
remainder is nonnegative by (8).  Thus

```text
12Q>=14C,
Q>=14*4158/12=4851.                              (15)
```

The variable system is sharp at

```text
n_3=1386, p_3=4158,
n_1=n_2=p_2=0,
|H|=1386,
r=2079, h=0,
Q=1386+1386+2079=4851.
```

This is an arithmetic control, not an asserted cover.

## 7. The `Q=4851` equality face is impossible

Equality in (15) forces

```text
n_3=1386, p_3=4158,
n_1=n_2=p_2=0,
|H|=1386,
r=2079, h=0.
```

Thus the selected type-three circuits partition all 4158 nonedges.  Every
member of `X` has exact multiplicity two, receives two extraction
assignments, and is the unique Wave 181 checkerboard conic for the paired
diagonal labels.

Fix a private label `e=xy`.  Its type-three leaf relation `w_e` has profile
`3+6`, omits the owner's leaf triangle `T`, and can be normalized to
coefficient `2` on all nine coordinates.  Equality forces the canonical
checkerboard conic `r_e` inside `w_e`.  Normalize its two-star coefficients
as

```text
r_e=(1,2 | 2,1).
```

The two residual relations

```text
w_e-r_e,
w_e-2r_e
```

both have profile `2+5`.  Each cancels one conic coordinate on each side,
so neither residual contains `r_e`; both continue to omit `T`.

Take a support-minimal circuit in either residual.  Both star sides are
proper, hence the circuit meets both and cross-realizes `e`.  It is not:

1. `r_e`, because the residual omits part of `supp(r_e)`;
2. a selected circuit, by privacy of `e`;
3. a selected companion, because its selected twin would have the same
   label set and would also cover `e`; or
4. another member of `X`, because equality makes every member of `X` the
   exact-two canonical conic for its two assignments, and the unique such
   circuit serving `e` is `r_e`.

This produces a projective short circuit outside the three equality pools,
contradicting `Q=4851`.  Since `Q` is integral,

```text
Q>=4852.                                          (16)
```

## 8. Consequence and boundary

The 693 verified edge-isolated projective circuits are disjoint from the
nonedge family.  If (16) is independently verified, then

```text
projective short circuit classes>=4852+693=5545,
B_4+B_5+B_6+B_7+B_8+B_9>=11090                  (circuits only).
```

Wave 188's verified `18018` bound remains stronger for all short dual
words because it also counts nonminimal words.  The new statement is a
strict circuit-level refinement.

Neither the degree-seven control nor the circuit theorem excludes rank 11.
Endpoint existence, the Conway-99 problem, and external novelty remain
`UNKNOWN`.
