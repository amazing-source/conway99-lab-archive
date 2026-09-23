# Wave 201 proof A: multiplicity-weighted fiber loss

## Verdict

`DERIVED_PENDING_HOSTILE_AUDIT`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
Q>=7059.
```

The new lemma charges every selected oriented label by its full
multiplicity inside a four-element pair fiber. At a 13-flag center, the
three unavoidable Hilton--Milner degree-five repetitions are removed
exactly once; all remaining repetition is available for the global
certificate. This yields an integral budget floor of 891 and raises the
conditional projective nonedge-circuit bound from 7,039 to 7,059.

No graph, code, cover, SAT, LP, configuration, enumeration, isomorphism,
or brute-force search is used.

```yaml
role: proof_a
date_utc: 2026-07-29T06:50:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: prove a
  multiplicity-weighted four-fiber repetition lemma at every flag
  center, couple it to the Wave198 oriented incidence equations, derive
  a universal certificate budget B>=891, and conclude Q>=7059.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave196-four-fiber-hilton-milner-verifier/package-manifest.sha256: eb833bf4ad503fb2243882704492f6bf836525f4b619de8a1979ffc6f0f785c9
  attempts/wave198-orientation-lift-proof-b/package-manifest.sha256: ba949fa2ededb7a23596fa0b05ca9e2d259f0e6a18c042814e2f3bc87b5b9054
  attempts/wave198-orientation-lift-proof-a-audit/package-manifest.sha256: 60f5b4a87893fe0e820f05989e666c26abaaa8f30b9a5598a7a7db571740c924
  attempts/wave200-two-face-gluing-proof-a/package-manifest.sha256: b909a16d3324f76e394322e6058f844bcf3bcc61409d567fdfd6f50ab53aced4
method: >-
  Multiplicity-weighted multiset repetition in disjoint four-element
  fibers, Hilton--Milner equality baselines, exact oriented incidence
  elimination, and rational coefficient algebra. No graph, code, cover,
  SAT, LP, configuration, enumeration, isomorphism, or brute-force
  search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave201-multiplicity-weighted-fiber-loss-proof-a\exact_check.py
  --verify
  attempts\wave201-multiplicity-weighted-fiber-loss-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave201-multiplicity-weighted-fiber-loss-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave201-multiplicity-weighted-fiber-loss-proof-a.md
  - attempts/wave201-multiplicity-weighted-fiber-loss-proof-a/
limitations:
  - This is a proof-A derivation pending hostile and verifier audits.
  - It is conditional on the prism-free rank-11 endpoint.
  - No endpoint graph, cover, code, flag system, or circuit family is
    constructed.
  - It supplies no incompatible endpoint upper bound.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain
    UNKNOWN.
```

## 1. Full pair-fiber repetition

Fix a center `x`. For each two-block type `P` among the seven local star
blocks, define:

```text
d_P   = number of full-pool flags whose A-set contains P,
u_P   = number of distinct full leaf labels of type P,
rho_P = d_P-u_P.
```

Every flag contributes one leaf occurrence to each of its three pair
types, so

```text
sum_P d_P=3c_x.
```

The 21 four-element fibers partition the leaf labels, hence

```text
j_x=sum_P u_P,
sum_P rho_P=3c_x-j_x.                           (1)
```

Now restrict attention to nonprivate selected oriented labels `x->y` of
type `P`. Let `m_y` be the number of selected flags centered at `x`
containing `y`. The selected occurrences are a subset of the full
occurrences in the fiber.

If several such labels lie in the same fiber, their occurrences remain
disjoint by leaf value. Writing `r_z` for the full multiplicity of every
distinct full leaf `z` in the fiber,

```text
rho_P
 =sum_z (r_z-1)
 >=sum_(selected nonprivate y of type P) (m_y-1).   (2)
```

This is the crucial multiple-label check: no two different leaf values
are charged to the same repeated occurrence.

## 2. Deficient centers

Define the local oriented-union deficit

```text
delta_x=36-j_x.
```

If `c_x<=12`, equations (1)--(2) give

```text
delta_x
 =36-3c_x+sum_P rho_P
 >=sum_(nonprivate selected x->y) (m_y-2).      (3)
```

Indeed, `36-3c_x>=0`; and for every `m_y>=1`,

```text
m_y-1>=m_y-2.
```

Labels of multiplicity one contribute `-1` to the right and therefore
cannot invalidate the inequality.

## 3. Tight centers and the three baseline slots

Suppose `c_x=13`. The common-star case has at most 12 flags, so the local
three-set family is one of the two Hilton--Milner equality templates
`H,K`. In either template exactly three pair types have

```text
d_P=5.
```

Every such fiber has only four leaves, so `rho_P>=1`. Equation (1) becomes

```text
delta_x
 =sum_P rho_P-3
 =sum_(d_P=5) (rho_P-1)+sum_(d_P<5) rho_P.      (4)
```

We now verify that subtracting the baseline `1` is safe even when several
selected labels occupy one degree-five fiber.

Let `R_P` be the set of nonprivate selected leaf values of type `P`.

- If `d_P=5` and `R_P` is empty, then
  `rho_P-1>=0`, matching the empty weighted sum.
- If `d_P=5` and `k=|R_P|>=1`, equation (2) gives

  ```text
  rho_P-1
   >=sum_(y in R_P)(m_y-1)-1
   =sum_(y in R_P)(m_y-2)+(k-1)
   >=sum_(y in R_P)(m_y-2).                    (5)
  ```

- If `d_P<5`, no baseline is subtracted and (2) directly gives

  ```text
  rho_P>=sum_(y in R_P)(m_y-2).                (6)
  ```

Thus (4)--(6) prove the same local inequality as (3):

```text
delta_x
 >=sum_(nonprivate selected x->y) (m_y-2)       (7)
```

for every center `x`.

The three baseline subtractions in (4) are exactly the three
Hilton--Milner degree-five pair types; no baseline is removed from any
other fiber.

## 4. The global multiplicity row

Let

```text
q       = number of nonprivate selected oriented labels,
epsilon =sum_nonprivate (5-m_y),
delta   =3564-J=sum_x delta_x.
```

The total selected multiplicity on nonprivate orientations is

```text
sum_nonprivate m_y=5q-epsilon.
```

Summing (7) over centers gives the new global row

```text
delta
 >=sum_nonprivate(m_y-2)
 =3q-epsilon.                                   (8)
```

Retain the exact Wave198 elimination identity

```text
4q
 =297-3SF-3g-SH+epsilon+delta+eta,              (9)
```

where

```text
eta=J-T-(a3+b3)>=0.
```

Substituting (9) into (8) and clearing the denominator gives

```text
9SF+9g+3SH+delta+epsilon-3eta>=891.             (10)
```

This row may contain the negative term `-3eta`; it is not asserted term by
term. Its nonnegativity follows from the proved rows (8)--(9).

## 5. Exact budget domination

Let

```text
B=40Q0-(76C-349V).
```

The sealed Wave198 certificate gives

```text
B
 =32SI+48S2+8SE2+28RA+12SL
  +S5+3SH+13SF
  +4a1+24b3+8c2+9g+16W,                        (11)
```

and the oriented row decomposes as

```text
S5=5delta+5eta+epsilon.                         (12)
```

Subtract the left side of (10) from (11). Exact coefficient comparison
gives

```text
B-(9SF+9g+3SH+delta+epsilon-3eta)

 =32SI+48S2+8SE2+28RA+12SL
  +4SF+4delta+8eta
  +4a1+24b3+8c2+16W
 >=0.                                           (13)
```

Equations (10) and (13) prove

```text
B>=891.                                         (14)
```

## 6. Consequence

At `C=4158,V=99`,

```text
Q0
 >=281457/40+891/40
 =282348/40
 =7058.7.
```

Since `Q0` is integral and `Q>=Q0`,

```text
Q>=7059.
```

Adding the 693 verified edge-isolated projective circuits gives at least
7,752 projective short circuits in total, or 15,504 nonzero scalar circuit
words.

## Boundary

```text
same-fiber multiset repetition (2):       DERIVED
deficient-center weighted loss (3):       DERIVED
tight HM baseline subtraction (4)-(6):    DERIVED
global row delta>=3q-epsilon:              DERIVED
budget floor B>=891:                       DERIVED
conditional Q>=7059:                       DERIVED
hostile Wave201 audit:                     pending
clean-room verifier promotion:             pending
endpoint contradiction:                    no
Conway-99 / external novelty:               UNKNOWN
```
