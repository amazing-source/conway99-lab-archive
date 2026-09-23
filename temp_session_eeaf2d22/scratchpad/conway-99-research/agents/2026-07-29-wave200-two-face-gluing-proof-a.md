# Wave 200 proof A: two-face orientation gluing obstruction

## Verdict

`DERIVED_PENDING_HOSTILE_AUDIT`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
Q>=7039.
```

The Wave198 certificate leaves only `Q0=7037` and `Q0=7038` below this
threshold. Their multiplied slack budgets are 23 and 63. Uniformly for
either budget, oriented incidence forces at least 27 multiplicity-five
labels, while local four-fiber loss permits at most 4. This excludes both
faces analytically, with no configuration or graph search.

```yaml
role: proof_a
date_utc: 2026-07-29T06:30:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: uniformly exclude the two
  integer near faces Q0=7037 and Q0=7038 of the sealed Wave198
  orientation certificate using its at-most-63 slack budget and a local
  additive four-fiber loss inequality, proving Q>=7039.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave196-four-fiber-hilton-milner-verifier/package-manifest.sha256: eb833bf4ad503fb2243882704492f6bf836525f4b619de8a1979ffc6f0f785c9
  attempts/wave198-orientation-lift-proof-b/package-manifest.sha256: ba949fa2ededb7a23596fa0b05ca9e2d259f0e6a18c042814e2f3bc87b5b9054
  attempts/wave198-orientation-lift-proof-a-audit/package-manifest.sha256: 60f5b4a87893fe0e820f05989e666c26abaaa8f30b9a5598a7a7db571740c924
method: >-
  Integral slack budgets, oriented multiplicity deficits, additive
  four-fiber leaf loss, Hilton--Milner equality templates, and exact
  rational arithmetic. No graph, code, cover, SAT, LP, configuration,
  enumeration, isomorphism, or brute-force search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave200-two-face-gluing-proof-a\exact_check.py --verify
  attempts\wave200-two-face-gluing-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave200-two-face-gluing-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave200-two-face-gluing-proof-a.md
  - attempts/wave200-two-face-gluing-proof-a/
limitations:
  - This is a proof-A derivation pending hostile and verifier audits.
  - It is conditional on the prism-free rank-11 endpoint.
  - The same coarse budget argument does not exclude Q0=7039.
  - No incompatible endpoint upper bound is obtained.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain
    UNKNOWN.
```

## 1. The two remaining faces have budget at most 63

Wave198 proves the exact nonnegative identity

```text
40Q0-(76C-349V)

 =32SI+48S2+8SE2+28RA+12SL
  +S5+3SH+13SF
  +4a1+24b3+8c2+9g+16W.                        (1)
```

At `C=4158,V=99`, its rational target is

```text
281457/40=7036.425.
```

If the integer `Q0` were below 7,039, then

```text
Q0 in {7037,7038}.
```

Let

```text
B=40*(Q0-281457/40).
```

The two values are `B=23,63`, so in either case

```text
B<=63.                                          (2)
```

Discarding other nonnegative terms from (1) gives

```text
S5+3SH+13SF+9g<=B.                              (3)
```

## 2. The oriented deficit equations

Retain the notation

```text
delta =3564-J,
eta   =J-T-(a3+b3),
epsilon=sum_nonprivate_orientations (5-m_x(y)),
q      =number of nonprivate selected orientations,
s      =number among them with m_x(y)=5.
```

The Wave198 row splits exactly as

```text
S5=5delta+5eta+epsilon.                         (4)
```

Every unsaturated nonprivate orientation contributes at least one to
`epsilon`, so

```text
s>=q-epsilon.                                   (5)
```

Eliminating `n3,h,p3,a3+b3` from the flag count, old-label capacity,
selected incidence, and oriented-union equations gives

```text
4q
 =297-3SF-3g-SH+epsilon+delta+eta.              (6)
```

Combining (5)--(6) and using `epsilon<=S5`,

```text
4s
 >=297-3SF-3g-SH-3epsilon+delta+eta
 >=297-(3SF+3g+SH+3S5).                         (7)
```

The parenthesis in (7) is at most `3B`: multiply (3) by three and compare
coefficients. Therefore, by (2),

```text
4s>=297-3B>=297-189=108,
s>=27.                                          (8)
```

## 3. Additive local fiber loss gives `s<=4`

For each center `x`, write

```text
c_x     =number of full-pool flags,
j_x     =number of distinct leaf labels,
phi_x   =13-c_x,
delta_x =36-j_x,
s_x     =number of multiplicity-five selected orientations centered at x.
```

Then

```text
sum_x delta_x=delta,
sum_x s_x=s.                                    (9)
```

Different saturated labels at one center use different two-block fibers:
one flag has only one leaf in each fiber type. In a saturated fiber, five
occurrences are the same leaf, so that fiber loses four distinct labels.

### Tight center: `c_x=13`

The verified Hilton--Milner equality classification says the local family
is one of `H,K`, and exactly three pair fibers have degree five. Every
non-saturated degree-five fiber loses at least one label because it has
five occurrences and only four vertices. If `s_x` of the three fibers
are saturated, total loss from 39 leaf occurrences is at least

```text
4s_x+(3-s_x)=3+3s_x.
```

Hence

```text
j_x<=39-(3+3s_x)=36-3s_x,
delta_x>=3s_x.                                  (10)
```

### Deficient center: `c_x<=12`

The `s_x` saturated fibers are disjoint and each loses four labels, so

```text
j_x<=3c_x-4s_x.
```

Writing `phi_x=13-c_x>=1`,

```text
delta_x
 >=36-3c_x+4s_x
 =3phi_x-3+4s_x
 >=4s_x.                                        (11)
```

Both cases imply `3s_x<=delta_x`. Summing and using (4),

```text
3s<=delta<=S5/5<=B/5<=63/5.
```

Since `delta` is integral,

```text
delta<=12,
s<=4.                                           (12)
```

This contradicts (8). Therefore neither `Q0=7037` nor `Q0=7038` is
possible.

## 4. Consequence and stopping point

The Wave198 certificate gives `Q0>=7036.425`; integrality and the
two-face exclusion give

```text
Q>=Q0>=7039.
```

Adding the 693 verified edge-isolated projective circuits yields at least
7,732 projective short circuits in total, or 15,464 nonzero scalar circuit
words.

For `Q0=7039`, the multiplied budget is 103. The coarse lower bound in
(7) becomes nonpositive if 99 units are spent on `epsilon`, so the present
mechanism genuinely stops. No stronger claim is made.

## Boundary

```text
budget B<=63 on both near faces:          DERIVED
forced saturated count s>=27:             DERIVED
additive local loss 3s<=delta:             DERIVED
local/global cap s<=4:                     DERIVED
Q0=7037 and Q0=7038 faces:                 REFUTED
conditional Q>=7039:                       DERIVED
hostile Wave200 audit:                     pending
clean-room verifier promotion:             pending
endpoint contradiction:                    no
Conway-99 / external novelty:               UNKNOWN
```
