# Wave 199 proof A: near-face orientation gluing obstruction

## Verdict

`DERIVED_PENDING_HOSTILE_AUDIT`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
Q>=7038,
```

where `Q` counts projective short circuits cross-realizing at least one
graph nonedge.

Wave198 proves `Q0>=7036.425`, so the only arithmetic case below 7,038 is
`Q0=7037`. Its integral certificate budget is only 23. That budget forces
at least 48 selected oriented labels to attain the local multiplicity-five
cap, while the four-fiber Hilton--Milner geometry permits at most 7.
This excludes the entire near face without graph or configuration search.

```yaml
role: proof_a
date_utc: 2026-07-29T06:10:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: analyze the integral
  Q0=7037 near face of the sealed Wave198 orientation certificate,
  combine its 23-unit slack budget with local Hilton--Milner equality
  geometry, exclude that face, and derive Q>=7038.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave196-four-fiber-hilton-milner-verifier/package-manifest.sha256: eb833bf4ad503fb2243882704492f6bf836525f4b619de8a1979ffc6f0f785c9
  attempts/wave198-orientation-lift-proof-b/package-manifest.sha256: ba949fa2ededb7a23596fa0b05ca9e2d259f0e6a18c042814e2f3bc87b5b9054
  attempts/wave198-orientation-lift-proof-a-audit/package-manifest.sha256: 60f5b4a87893fe0e820f05989e666c26abaaa8f30b9a5598a7a7db571740c924
method: >-
  Integral slack-budget analysis, oriented multiplicity deficits,
  four-fiber leaf repetition, the two Hilton--Milner equality templates,
  and exact rational arithmetic. No graph, code, cover, SAT, LP,
  configuration, enumeration, isomorphism, or brute-force search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave199-near-face-gluing-proof-a\exact_check.py --verify
  attempts\wave199-near-face-gluing-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave199-near-face-gluing-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave199-near-face-gluing-proof-a.md
  - attempts/wave199-near-face-gluing-proof-a/
limitations:
  - This is a proof-A derivation pending hostile and verifier audits.
  - It is conditional on the prism-free rank-11 endpoint.
  - It excludes Q0=7037 but supplies no incompatible endpoint upper bound.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain
    UNKNOWN.
  - The sealed Wave198 hostile-audit package passes its documented test
    command, but generic unittest discovery has a relative-import
    portability failure; that non-mathematical issue is not used here.
```

## 1. The 23-unit near-face budget

Wave198 proves

```text
Q0-(76C-349V)/40

 =4SI/5+6S2/5+SE2/5+7RA/10+3SL/10
  +S5/40+3SH/40+13SF/40
  +a1/10+3b3/5+c2/5+9g/40+2W/5.               (1)
```

At `C=4158,V=99`, the target is `281457/40`. If the integer `Q0`
equaled 7,037, multiplying (1) by 40 would give

```text
23
 =32SI+48S2+8SE2+28RA+12SL
  +S5+3SH+13SF
  +4a1+24b3+8c2+9g+16W.                        (2)
```

Every term is a nonnegative integer. In particular,

```text
SF<=1,  g<=2,  SH<=7,  S5<=23.                 (3)
```

## 2. Split the orientation slack

Let

```text
J = full-pool oriented label union,
T = selected oriented label union,
A = a3+b3,
delta =3564-J,
eta   =J-T-A.
```

For each nonprivate selected oriented label `x->y`, let `m_x(y)` be its
selected multiplicity. The local theorem gives `1<=m_x(y)<=5`. Put

```text
q       = number of nonprivate selected oriented labels,
epsilon = sum_nonprivate (5-m_x(y)).
```

Private labels have multiplicity one, so direct expansion of the three
successive Wave198 inequalities gives

```text
S5=5*delta+5*eta+epsilon.                       (4)
```

Therefore (3) implies

```text
delta<=4,
epsilon<=23.                                    (5)
```

Let `s` be the number of nonprivate oriented labels with multiplicity
exactly five. Every other nonprivate orientation contributes at least one
to `epsilon`, hence

```text
s>=q-epsilon.                                   (6)
```

## 3. At least 48 saturated orientations are forced

Use the flag-count and old-label slacks

```text
n3+h+g=1287-SF,
A=3h-SH.
```

The selected oriented incidences and union identity are

```text
3n3=p3+5q-epsilon,
p3+q+A=3564-delta-eta.
```

Eliminating `n3,h,p3,A` gives the exact relation

```text
4q
 =297-3SF-3g-SH+epsilon+delta+eta.              (7)
```

Using (3) and nonnegativity in (7),

```text
4q>=297-3-6-7=281,
q>=71.
```

Together with (5)--(6),

```text
s>=71-23=48.                                    (8)
```

## 4. Local fiber geometry permits at most 7

At center `x`, let `c_x` be the number of full-pool flags and `j_x` their
distinct leaf-label count. Define

```text
phi_x  =13-c_x,
delta_x=36-j_x.
```

The verified local theorem gives nonnegative integer deficits with

```text
sum_x phi_x=SF,
sum_x delta_x=delta.                            (9)
```

Suppose `m_x(y)=5`. The five selected flags containing the oriented label
`x->y` have five distinct local `A`-sets, all through the fixed pair
`P_x(y)`. Thus:

1. `P_x(y)` has degree five in the full local three-set family; and
2. five leaf occurrences in its four-element fiber are all the same
   vertex `y`.

The second point alone gives

```text
j_x<=3c_x-4.                                    (10)
```

There are two cases.

### Tight center: `c_x=13`

A common-star family has at most 12 flags, so a 13-member family is a
Hilton--Milner equality family. In each of the two equality templates
`H,K`, exactly three block-pairs have degree five. Different saturated
leaf labels cannot use the same pair, because every flag has only one leaf
in that pair's fiber. Hence

```text
s_x<=3.
```

Moreover, the other two degree-five pair fibers each contain five leaf
occurrences but only four vertices, so each loses at least one further
distinct label. The saturated fiber loses four. Thus the total loss from
the 39 leaf occurrences is at least six:

```text
j_x<=33,
delta_x>=3.
```

### Deficient center: `c_x<=12`

The sum of all pair-degrees is `3c_x`, so there are at most

```text
floor(3c_x/5)<=7
```

degree-five pairs and therefore `s_x<=7`. If even one is saturated, (10)
gives `j_x<=32`, hence

```text
delta_x>=4.
```

By (3) and (9), there is at most one deficient center and total
`delta<=4`. If the deficient center is saturated, it consumes all four
units of `delta`, so no tight center can be saturated and `s<=7`. If it
is not saturated (or does not exist), at most one tight center can be
saturated because each consumes at least three units of `delta`; it
contributes at most three labels. In either case,

```text
s<=7.                                           (11)
```

Equations (8) and (11) contradict one another. Thus `Q0=7037` is
impossible.

## 5. Consequence

Equation (1) gives `Q0>=7036.425`, and `Q0` is an integer count.
The preceding argument excludes its only remaining value below 7,038.
Therefore

```text
Q>=Q0>=7038.
```

Adding the 693 verified edge-isolated projective circuits gives at least
7,731 projective short circuits in total, or 15,462 nonzero scalar circuit
words.

## Boundary

```text
23-unit budget (2):                       DERIVED
S5 deficit decomposition (4):             DERIVED
forced saturated count s>=48:             DERIVED
local saturated cap s<=7:                 DERIVED
Q0=7037 face:                             REFUTED
conditional Q>=7038:                      DERIVED
hostile Wave199 audit:                    pending
clean-room verifier promotion:            pending
endpoint contradiction:                   no
Conway-99 / external novelty:              UNKNOWN
```
