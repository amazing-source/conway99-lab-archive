# Wave 189 compact derivation

## 1. Degree-seven star system

The 99 all-one star relations and their negatives force

```text
B_(7,0)>=99, B_(0,7)>=99.
```

For a primal composition `(a,b)`, its local counts `(r_x,s_x)` on a
seven-star obey

```text
r_x-s_x=0 mod 3,
r_x+s_x<=7,
sum_x r_x=3a,
sum_x s_x=3b.
```

The twelve allowed local patterns have convex-hull vertices

```text
(0,0), (6,0), (5,2), (2,5), (0,6).
```

The nontrivial facets give

```text
2a+b<=396, a+2b<=396.
```

Conversely, triangulation from `(0,0)` supplies an exact rational local
profile for every point satisfying these inequalities.  The exact checker
contains a 16-cell typed rational enumerator satisfying this local system,
all complete rows through degree seven, both endpoint equalities
`B_(7,0)=B_(0,7)=99`, the star-pair rows in degrees 12--14, all ordinary
MacWilliams inequalities, and the quadratic type moments.  Hence there is
no contradiction in this relaxation.

## 2. Closed extraction pool

Let an inclusion-minimal short-circuit cover of the `C=4158` nonedges have
type counts `n_i` and private-label counts `p_i`.  Then

```text
p_1=n_1,
n_2<=p_2<=2n_2,
n_3<=p_3<=3n_3,
2n_1+2n_2+3n_3+p_2+p_3>=2C.
```

The selected type-three companions form a disjoint outside pool `H` of size
`n_3`.  Choose noncompanion extraction assignments:

```text
A=n_1+2p_2+p_3.
```

Privacy, the explicit same-owner support distinction, and companion
involution show that the extraction pool can be closed under companions of
its exact-three members while remaining disjoint from both the selected
cover and `H`.

Write the closed pool as `r` circuits of exact multiplicity at most two and
`h` exact-three companion pairs.  The two type-two translations for a
private label `xy` have profiles `6+2` and `2+6`.  An exact-three circuit
inside the first must center at `x`, while one inside the second must center
at `y`.  Thus they cannot be companion mates.  Every exact-three pair
receives at most one assignment from each of its three labels:

```text
A<=2r+3h,
|X|=r+2h>=A/2.
```

Consequently

```text
2Q>=3n_1+2n_2+4n_3+2p_2+p_3.
```

The exact coefficient identity

```text
18n_1+12n_2+24n_3+12p_2+6p_3

=7(2n_1+2n_2+3n_3+p_2+p_3)
 +4n_1+2(p_2-n_2)+(3n_3-p_3)+3p_2
```

gives

```text
12Q>=14C,
Q>=4851.
```

## 3. Equality-face cancellation

Equality throughout forces

```text
n_3=1386, p_3=4158,
n_1=n_2=p_2=0,
|H|=1386,
r=2079, h=0.
```

Thus the selected triples partition all nonedges, and every one of the
4158 leaf-extraction assignments is one of the 2079 exact-two canonical
checkerboard conics, each used for its two diagonal labels.

Fix a private label `e=xy`.  Normalize its `3+6` leaf relation `w_e` to
coefficient `2` on all nine coordinates.  Equality forces the canonical
checkerboard conic `r_e` inside it.  Normalize

```text
r_e=(1,2 | 2,1).
```

Both nonzero residuals

```text
w_e-r_e,
w_e-2r_e
```

have profile `2+5`, omit the owner's leaf triangle, and omit opposite
coordinates of `r_e`.  A minimal circuit inside either residual meets both
proper star sides and cross-realizes `e`.  It is:

- not `r_e`, because the residual omits part of its support;
- not selected, by privacy of `e`;
- not a selected companion, because its selected twin would also cover
  `e`; and
- not another member of `X`, because equality makes every member of `X`
  an exact-two circuit receiving two assignments, and the unique such
  circuit serving `e` is `r_e`.

This produces a circuit outside the three equality pools, contradicting
`Q=4851`.  Since `Q` is integral,

```text
Q>=4852.
```

Adding the 693 edge-isolated projective circuits gives 5545 projective
short circuit classes and the conditional scalar bound

```text
B_4+...+B_9>=11090.
```

The stronger verified Wave 188 value `18018` counts all short dual words,
including nonminimal words.  Rank 11 and Conway-99 remain `UNKNOWN`.
