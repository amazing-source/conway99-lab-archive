# Wave 187 proof B: quadratic-type complete-enumerator control

```yaml
role: proof_b
date_utc: 2026-07-29T01:58:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional rank-11 endpoint: test whether ordinary or complete ternary
  MacWilliams moments, the parabolic-quadric type split, and the 231 marked
  weight-198 scalar pairs can upper-bound B4+...+B9 below the verified 18018
  lower bound.
inputs:
  verification/wave171-pq-centered-code/verification-report.md: 1f2ba5ed92ba6bb1ccc05cd753a8e359f208c3ddc7ca85766f26f8869346414f
  verification/wave173-complete-enumerator-lift/verification-report.md: 6e12244414d7360831e1eb78416dc55b77f00ef50a6a0a304befb7174d5d7f8c
  verification/wave174-no-weight3-dual/verification-report.md: 59bc0e470a7d007aa2ddaec262a2f3046c8df7da56192bdab90327962feb9b0a
  verification/wave175-polar-cap-boundary/audit.md: cefd905cc0339175f74353b7d8ebe94937944271c77c0ba80a02f8520145fb50
  agents/2026-07-29-wave186-nonedge-relation-dimension-proof-a.md: 1843d40d883f430bd4827a5cdd963301f266c777ee2328ec34d10af240b7db71
  verification/wave188-affine-star-word-amplification-verifier/audit.md: 1cae5c4bc49bf8e9dda6d20d67a03de3a6dabb7a75f9ba9e22cca159538b68f3
method: >-
  Exact Pless and complete MacWilliams moments, parabolic quadratic-form
  orbit counts, one/two/three-point orthogonal-complement counts, and a
  sparse rational hostile control certified with Python Fraction arithmetic.
  A finite LP selected the sparse support only; every reported equality and
  inequality is rechecked exactly, with no graph, code, or configuration
  enumeration.
command: python -B attempts/wave187-code-geometry-proof-b/exact_check.py
outputs:
  attempts/wave187-code-geometry-proof-b/exact_check.py: 53053eaf294b32ee4ed736d8323053ebb12b93e4e9edea17b685ab9d430b5c59
limitations:
  - The hostile control is rational and is not a linear code or point set.
  - Complete MacWilliams nonnegativity is certified only through degree six.
  - This sparse control has a negative complete degree-seven coefficient.
  - No upper bound below 8778 or 18018 is obtained.
  - Rank 11, endpoint existence, Conway-99, and external novelty remain UNKNOWN.
```

## Verdict

There is no MacWilliams contradiction at the tested level.  An exact
nonnegative rational control satisfies simultaneously:

```text
B1=B2=B3=0,
all ordinary B_j>=A_j>=0 for 0<=j<=231,
231 marked scalar pairs of composition (36,162),
all complete dual coefficients through degree six nonnegative,
the singular / norm-plus / norm-minus moments through degree three,
an integral three-point Gram-type census.
```

Nevertheless it has

```text
B4 = 126079749915623/131414760
   = 959403.265... > 18018,

B4+...+B9
   = 721437869830147204193861/3066344400
   = 235276203752633.65....
```

Thus ordinary moments, complete moments through degree six, and the
quadratic three-point data cannot prove the desired upper bound.  This is a
hostile relaxation, not evidence that the endpoint exists.

## 1. Terminology correction

Two frozen marked families must not be merged:

1. the centered Gram rows give **231 primal scalar pairs of weight 198**,
   each with composition `(36,162)` up to sign; and
2. the original vertices give **99 dual star scalar pairs of weight 7**.

The control below fixes the first family.  The star words contribute lower
bounds on the dual enumerator; they are not the marked weight-198 words.

The Wave 54 ordinary distribution is not reused.  It has `B3=120` and its
complete lift was refuted in Wave 173.  The present control instead has
`B1=B2=B3=0` and a different support.

## 2. Quadratic-form orbit moments

Write the ambient parabolic form as

```text
Q(x)=x_0^2+x_1*y_1+...+x_5*y_5
```

on `F_3^11`.  Its projective point classes have sizes

```text
singular:   29524,
Q=1:       29646,
Q=2:       29403.
```

For an ambient point `v`, put

```text
b_v = number of selected singular points orthogonal to v.
```

The elementary quadratic-form counts needed for the first two moments are:

| restriction | `Q=1` points | `Q=2` points |
|---|---:|---:|
| orthogonal to one selected singular point | 9963 | 9720 |
| orthogonal to an orthogonal selected pair | 3402 | 3159 |
| orthogonal to a nonorthogonal selected pair | 3321 | 3240 |

There are `3696` orthogonal selected pairs and
`binom(231,2)-3696=22869` nonorthogonal pairs.  Hence, for example,

```text
sum_(Q(v)=1) b_v
  =231*9963
  =2301453,

sum_(Q(v)=1) b_v^2
  =2301453+2*(3696*3402+22869*3321)
  =179344935.
```

The analogous norm-two moment is `173787768`.  Adding the 231 selected
points with `b_v=33` to Wave 175's outside-singular moments gives

```text
sum_singular b_v   =2273271,
sum_singular b_v^2 =176539671.
```

These calculations use the quadratic specialization rather than an
ordinary weight enumerator.

## 3. The first three complete moments

Pair a nonzero word with its negative.  For a scalar-pair composition
`(a,b)`, put

```text
w=a+b,
d=a-b,
x=231-3*w/2.
```

The paired complete coefficients used here are

```text
K10 = 2*x,
K20 = x^2-x-(3/4)*d^2,
K11 = 2*x^2+(3/2)*d^2-462,

K21 = x^3-x^2-460*x+(3/4)*(x+1)*d^2,
K30 = x^3/3-x^2+154-(3/4)*(x+1)*d^2.
```

If `t_(a,b)` is the scalar-pair mass, vanishing of every complete dual
coefficient of degrees one through three is equivalent to

```text
sum t      =88573,
sum K10*t  =-231,
sum K20*t  =-26565,
sum K11*t  =-53130,
sum K21*t  =-6083385,
sum K30*t  =-2027795.
```

The right sides are exactly the negatives of the zero-word contributions.

## 4. Exact rational hostile control

The nonzero typed scalar-pair masses are recorded below.  `S,+,-` denote
singular, norm-one, and norm-two ambient projective points.

```text
S:
(0,81)       1/1700
(6,24)       45334/697
(36,162)     231
(72,81)      2142276162781519/576217218500
(75,78)      2368455943056339/144054304625
(78,78)      226718/25

+:
(0,120)      1663/84
(0,228)      81673674496579188347/3569527376475060000
(33,195)     1459598804117088331/100114860628282500
(75,78)      12502563/425
(102,102)    160341/952
(114,114)    59981815805188283/23787060262812000

-:
(0,114)      445838499187/2044229600
(0,120)      957613632057/3212360800
(72,78)      2033920953923/292032800
(78,78)      8822683455071/408845920
(108,111)    481518113773/1405407850
```

All masses are positive.  Aggregating over the three types gives the
ordinary primal support

```text
0,30,81,114,120,150,153,156,198,204,219,228.
```

Exact Krawtchouk transformation checks all 232 ordinary coefficients:

```text
B0=1,
B1=B2=B3=0,
B_j>=A_j>=0 for every j.
```

The complete transform has degree-four row

```text
(B_04,B_13,B_22,B_31,B_40)
  =(0,0,126079749915623/131414760,0,0),
```

and every complete coefficient of degrees five and six is also
nonnegative.

## 5. The control also passes the three-point quadratic split

Use factorial moments `M_h=sum_v binom(b_v,h)`.  The typed control gives:

| type | `M_0` | `M_1` | `M_2` | `M_3` |
|---|---:|---:|---:|---:|
| singular | 29524 | 2273271 | 87133200 | 2233980128 |
| norm one | 29646 | 2301453 | 88521741 | 2242872288 |
| norm two | 29403 | 2245320 | 85771224 | 2174315184 |

The third moments sum to

```text
6651167600 = binom(231,3)*3280,
```

as required because Wave 174 makes every selected triple linearly
independent and its common perpendicular contains `3280` projective points.

For a selected triple, classify its zero-diagonal `3 by 3` Gram matrix by
the number of orthogonal pairs.  If no pair is orthogonal, split by the two
determinant types.  The numbers of singular, norm-one, and norm-two points
in its common perpendicular are:

| triple type | singular | norm one | norm two |
|---|---:|---:|---:|
| three orthogonal pairs | 1093 | 1215 | 972 |
| two orthogonal pairs | 1093 | 1134 | 1053 |
| one orthogonal pair | 1093 | 1134 | 1053 |
| no orthogonal pair, plus type | 1066 | 1107 | 1107 |
| no orthogonal pair, minus type | 1120 | 1080 | 1080 |

The following **integral hostile census** reproduces the displayed typed
third moments:

```text
three orthogonal pairs:        38192
two orthogonal pairs:              0
one orthogonal pair:          731808
no orthogonal pair, plus:     302968
no orthogonal pair, minus:    954827
```

It also obeys the exact pair and wedge incidences

```text
n1+2*n2+3*n3 =3696*(231-2)=846384,
n2+3*n3      =231*binom(32,2)=114576.
```

This census is only a moment control.  It is not asserted to arise from a
231-point set.

## 6. Precise stopping point

The exact sparse control first fails at complete degree seven:

```text
B_70=B_07
  =-10151603437954385741/508426957500 < 0.
```

Therefore this report does **not** exhibit a complete formal enumerator
through degree nine.  It proves the narrower and useful negative result:

```text
ordinary MacWilliams
+ complete MacWilliams through degree 6
+ quadratic point-type moments through degree 3
do not upper-bound B4+...+B9 below 18018.
```

The smallest unconsumed geometric statistic is the type-resolved fourth
factorial moment

```text
M_(4,epsilon)=sum_(Q(v)=epsilon) binom(b_v,4).
```

It is governed by the rank, radical, and determinant types of the selected
`4 by 4` Gram matrices.  The first transform constraint that rejects this
specific sparse control is complete degree-seven positivity.  A productive
continuation should therefore target either:

1. a four-point Gram-type census strong enough to constrain the typed
   fourth moments; or
2. the complete degree-seven coefficients coupled directly to the 99
   distinguished seven-coordinate star relations.

Neither bridge is present in the frozen ordinary or three-point data.
There is no endpoint exclusion, strict `n3` improvement, graph
construction, or Conway-99 resolution here.
