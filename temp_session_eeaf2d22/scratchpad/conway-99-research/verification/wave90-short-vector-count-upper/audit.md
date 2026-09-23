# Wave 90 independent prism-free norm-14 count audit

Date UTC: 2026-07-28T00:55:45Z.

Verdict: **VERIFIED in the frozen conditional scope**.

```text
prism-free endpoint P=0:                         REQUIRED
equivalent endpoint value n3=4158:               IMPORTED
rank r=28:                                       NOT USED
N14 counts t and -t separately:                  YES
rooted positive-vector upper bound:              392
global norm-14 shell upper bound:                N14 <= 5544
bound on N14+N16+N18:                            NOT PROVED
q=16 / graph / Conway-99 / novelty:              UNKNOWN
```

## Freeze and independence

The discovery manifest was hashed before inspection:

```text
f7dda4995714a4216c8a8c00738d8da070ff4f485fb7ddd4596921b309482f88
```

All 11 discovery files were inventoried by path, length, and SHA-256.
Post-inspection comparison found every discovery byte unchanged, and the
discovery manifest has zero mismatches.

`independent_verify.py` does not import or execute discovery code.  It
constructs the rooted scaffold, prism-free transition domain, local perfect
matchings, complementary-Fano reconstruction, and global orientation count
from independent definitions.  Only after writing the independent result
was the discovery JSON projected for comparison; the projections have zero
mismatches.

## Rooted scaffold

Fix a root `o`.  Its 14 neighbors induce seven disjoint mate edges because
each neighbor has exactly one common neighbor with `o`.

Every residual vertex has two nonmate neighbors in `N(o)`.  Conversely, a
nonmate pair in `N(o)` is nonadjacent and has exactly two common neighbors:
`o` and one residual vertex.  Hence the residual vertices are exactly the
84 edges of

```text
K14 - 7K2.
```

At a base point `s`, the 12 incident residual labels are paired into six
selected transitions.  Across all 14 base points there are 84 selected
transitions.  Under `P=0`, a transition

```text
{s,a} -- {s,b}
```

cannot have `a,b` as mates.

## Seed injectivity and both sign sides

Let `t_o=+1` for a norm-14 vector.  Wave 71 gives seven positive and seven
negative coordinates whose support is the complementary-Fano
`2-(7,4,2)` incidence graph.  The four negative neighbors of `o` form a
seed `Q`; independence permits at most one point from each root mate pair.
Thus there are

```text
C(7,4)*2^4 = 560
```

possible seeds.

For each of the six pairs in `Q`, the pair's two common graph neighbors are
`o` and its unique residual label.  Complementary-Fano saturation makes
those six labels distinct and identifies them with all other positive
vertices.

This also recovers the negative side, not merely the positive side.  Every
pair of positive vertices already has its two common neighbors in the
negative side, exhausting `mu=2`; the union of these pairwise common
neighbor sets contains all seven negative vertices.  Therefore `Q`
determines both sign classes and the signed vector.  The independent
canonical Fano model checks all seven choices of the rooted block.

Rooting at a positive coordinate removes the global sign ambiguity: `-t`
is a different oriented vector and is rooted at its own seven positive
coordinates.

## Transition-seed count

A selected transition uses three base points in distinct mate groups.
Extending these points to a four-point seed means choosing one endpoint
from one of the four unused mate groups:

```text
4*2 = 8
```

extensions.  Therefore the 84 selected transitions have

```text
84*8 = 672
```

transition-seed incidences.

Within a seed, fix one of its four base points.  The three seed labels
through that point meet a perfect matching, so at most one pair is a
selected transition.  The four base points therefore give a cap of four
selected transitions per seed.  At least

```text
672/4 = 168
```

of the 560 seeds contain a forbidden positive-side adjacency.  At most

```text
560-168 = 392
```

seeds can represent rooted vectors.

The independent checker reconstructs all 840 prism-free transition
candidates, exactly eight seed extensions for each, 6,040 admissible local
perfect matchings at every base point, and local star cap one.

## Global orientation count

`N14` counts oriented vectors, including both `t` and `-t`.  Each oriented
vector has exactly seven positive coordinates, so

```text
7*N14
 = sum_o #{t : ||t||^2=14 and t_o=+1}
 <= 99*392.
```

Since `392=7*56`,

```text
N14 <= 99*56 = 5544.
```

An antipodal pair contributes 14 rooted-positive incidences--seven from
each orientation--so no hidden factor of two is missing.

## Boundary

The proof uses the saturation specific to norm 14.  Norm-16 and norm-18
supports have deficiency patterns and are not bounded here.  The theorem
alone neither excludes `q=16` nor resolves the graph.  Conway-99 and
literature novelty remain `UNKNOWN`.
