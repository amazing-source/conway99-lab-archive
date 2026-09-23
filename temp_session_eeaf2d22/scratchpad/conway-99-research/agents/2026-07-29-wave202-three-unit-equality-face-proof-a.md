# Wave 202 proof A: the three-unit equality face

## Verdict

`DERIVED_FACE_CHARACTERIZATION_NO_EXCLUSION`.

Conditionally on the sealed Wave201 derived theorem, the case

```text
Q0=7059
```

has an exact three-unit integer certificate. Every slack partition falls
into one of three symbolic classes. Every center has 12 or 13 full flags,
and at most three nonprivate selected orientations can have multiplicity
one.

I do not find a valid two-center obstruction. A multiplicity-one
orientation must be paired with an occupied opposite orientation of the
same unordered label, but the local equations permit the two orientations
to occupy degree-five baseline fibers at their respective centers. This
is a surviving necessary local pattern, not a construction or existence
claim. The conditional lower bound remains `Q>=7059`.

No graph, code, cover, SAT, LP, configuration, isomorphism, or brute-force
search is used. The only finite split is the three-unit symbolic slack
partition.

```yaml
role: proof_a
date_utc: 2026-07-29T07:15:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional on sealed Wave201: derive the exact integer certificate at
  Q0=7059, characterize all three-unit slack partitions and local
  equality conditions, and test the multiplicity-one two-center route
  without claiming exclusion when the local pattern survives.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave196-four-fiber-hilton-milner-verifier/package-manifest.sha256: eb833bf4ad503fb2243882704492f6bf836525f4b619de8a1979ffc6f0f785c9
  attempts/wave198-orientation-lift-proof-b/package-manifest.sha256: ba949fa2ededb7a23596fa0b05ca9e2d259f0e6a18c042814e2f3bc87b5b9054
  attempts/wave198-orientation-lift-proof-a-audit/package-manifest.sha256: 60f5b4a87893fe0e820f05989e666c26abaaa8f30b9a5598a7a7db571740c924
  attempts/wave201-multiplicity-weighted-fiber-loss-proof-a/package-manifest.sha256: 36d95b7d1bee4739cc5f33c780d22168fe58bf974904031db86d25da77bce695
method: >-
  Exact integer certificate algebra, symbolic three-unit partitioning,
  local multiset-slack decomposition, and analytic two-center incidence
  scrutiny. No graph, code, cover, SAT, LP, configuration, isomorphism,
  or brute-force search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave202-three-unit-equality-face-proof-a\exact_check.py --verify
  attempts\wave202-three-unit-equality-face-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave202-three-unit-equality-face-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave202-three-unit-equality-face-proof-a.md
  - attempts/wave202-three-unit-equality-face-proof-a/
limitations:
  - Wave201 is a sealed derived input pending verifier promotion.
  - No global endpoint, cover, or code satisfying the face is constructed.
  - The two-center baseline pattern is not excluded and is not asserted
    realizable.
  - No improvement beyond conditional Q>=7059 is claimed.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain
    UNKNOWN.
```

## 1. Exact integer certificate

Let

```text
L=delta-3q+epsilon>=0.
```

This is exactly the slack in the Wave201 weighted row
`delta>=3q-epsilon`. Combining it with the Wave198 certificate gives

```text
10Q0-(19C-85V)

 =8SI+12S2+2SE2+7RA+3SL
  +L+delta+2eta+SF
  +a1+6b3+2c2+4W.                               (1)
```

At `C=4158,V=99`,

```text
19C-85V=70587.
```

Thus `Q0=7059` makes the nonnegative integer right side of (1) equal

```text
3.                                               (2)
```

It follows immediately that

```text
SI=S2=RA=b3=W=0.                                (3)
```

The complete remaining equation is

```text
3SL+2(SE2+eta+c2)+(L+delta+SF+a1)=3.            (4)
```

## 2. Every symbolic slack partition

Put

```text
E=SE2+eta+c2,
U=L+delta+SF+a1.
```

All quantities are nonnegative integers. Equation (4) has exactly the
following three classes:

```text
A. SL=1, E=0, U=0;

B. SL=0, E=0, U=3;

C. SL=0, E=1, U=1.
```

In class B, the four unit-weight slacks `L,delta,SF,a1` are arbitrary
nonnegative integers summing to three. In class C, exactly one of
`SE2,eta,c2` equals one, and exactly one of `L,delta,SF,a1` equals one.
This is a symbolic partition statement; no endpoint configurations are
enumerated.

## 3. Exact local form of the weighted slack

At center `x` and pair type `P`, let

```text
R_P = selected nonprivate leaf values of type P,
k_P = |R_P|,
e_P =rho_P-sum_(y in R_P)(m_y-1)>=0.
```

The inequality `e_P>=0` is value-by-value: it is the sum of unused full
multiplicity above selected multiplicity on selected leaves and all
repeat excess on unselected leaves.

Write

```text
L_x=delta_x-sum_(selected nonprivate x->y)(m_y-2).
```

Then `L=sum_x L_x`.

### Deficient center

If `c_x<=12`, exact expansion gives

```text
L_x
 =3(12-c_x)+q_x+sum_P e_P,                      (5)
```

where `q_x=sum_P k_P`.

### Tight center

If `c_x=13`, let `b_P=1` on the three Hilton--Milner degree-five pair
types and zero otherwise. Exact expansion gives

```text
L_x
 =sum_P(e_P+k_P-b_P)
 =q_x-3+sum_P e_P.                              (6)
```

For a degree-five type, `e_P+k_P-b_P>=0`: if `k_P=0`, the four-element
fiber gives `e_P=rho_P>=1`; if `k_P>=1`, its value is the nonnegative
same-fiber residual from Wave201.

These formulas give the exact local zero-slack conditions:

- at `c_x=12`, `L_x=0` iff `q_x=0` and every `e_P=0`;
- at `c_x=13`, `L_x=0` iff every non-degree-five type has
  `e_P=k_P=0`, while each of the three degree-five types has
  `e_P+k_P=1`.

For a degree-five type, the latter alternative is either `k_P=0,e_P=1`
or `k_P=1,e_P=0`. In the second case the selected value has multiplicity
at least two: a multiplicity-one value pays no selected repeat charge,
while the degree-five fiber still has `rho_P>=1`.

## 4. Consequences of the three-unit face

Since `SF=sum_x(13-c_x)` and `delta=sum_x(36-j_x)`, a center with
`c_x<=11` would contribute at least two to `SF` and at least three to
`delta`, already exceeding the three-unit total in (4). Therefore

```text
c_x in {12,13} for every x.                     (7)
```

Let `r_x` count multiplicity-one nonprivate selected orientations centered
at `x`, and put `r=sum_x r_x`.

For a deficient `c_x=12` center, (5) gives `L_x>=q_x>=r_x`. At a tight
center, each non-degree-five fiber contributes `e_P+k_P>=r_P`. A
degree-five fiber contributes

```text
e_P+k_P-1>=r_P.                                 (8)
```

To check (8), let `h_P` count the selected values of multiplicity at least
two. If `h_P>=1`, then the left side minus `r_P` is
`e_P+h_P-1>=0`. If `h_P=0` but `r_P>0`, then selected multiplicity-one
values pay no repeat charge, so the unavoidable `rho_P>=1` gives
`e_P>=1`. The empty case is immediate.

Thus

```text
r<=L<=3.                                        (9)
```

Class A has `L=0`, hence no multiplicity-one nonprivate orientation.
Class C permits at most one; class B permits at most three, according to
the chosen unit-weight partition.

## 5. The two-center route survives

Suppose `x->y` is a nonprivate selected orientation with multiplicity one.
Because its unordered label `{x,y}` is nonprivate, another selected circuit
contains the same label. It cannot have the same center `x`, or
`m_x(y)` would be at least two. Therefore the opposite orientation

```text
y->x
```

is occupied.

This coupling does not force an even number of multiplicity-one
orientations: the opposite multiplicity may be at least two.

The lowest-slack local placement is not contradicted by the displayed
rows:

- at the multiplicity-one center, the label may occupy a degree-five
  baseline fiber while the required baseline repeat is supplied elsewhere
  in that same full fiber, contributing one unit to `L_x`;
- at the opposite center, a single selected leaf value of multiplicity
  `m>=2` may occupy a degree-five baseline fiber with
  `e_P=0`, contributing no extra `L` beyond the baseline;
- fixed-center simplicity allows at most five flags through either pair
  type, and both statements respect that cap.

Degree five in both orientations is also not a contradiction in the
frozen rows. Pair degree five says there are five full occurrences in
each local fiber; it does not say that all five use the distinguished leaf
`y` or `x`. No frozen theorem couples the full leaf-multiplicity multiset
in `P_x(y)` to the one in `P_y(x)`. Therefore no incompatible sign,
parity, or distinctness condition follows from the available local
equations.

This is only a demonstration that the attempted obstruction is absent
from the current analytic rows. It is not a construction of a compatible
global flag system, cover, code, or endpoint graph.

## Boundary

```text
exact integer certificate (1):             DERIVED
three symbolic partition classes:          DERIVED
local slack formulas (5)-(6):               DERIVED
all centers have c_x in {12,13}:            DERIVED
multiplicity-one count r<=L<=3:             DERIVED
opposite-orientation coupling:              DERIVED
two-center baseline obstruction:            NOT FOUND
Q0=7059 excluded:                           no
conditional Q>=7059:                        unchanged
global realization of the face:             UNKNOWN
```
