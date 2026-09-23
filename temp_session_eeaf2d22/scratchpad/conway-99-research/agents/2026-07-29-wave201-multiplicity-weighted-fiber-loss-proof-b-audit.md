# Wave 201 proof-B audit: multiplicity-weighted fiber loss

```yaml
role: proof_b
date_utc: 2026-07-29T07:02:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Hostile audit of the multiplicity-weighted four-fiber lemma,
  including multiple selected leaf values in one fiber, the three
  Hilton--Milner baselines at a tight center, the global row
  delta>=3q-epsilon, the budget difference, and conditional Q>=7059.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave196-four-fiber-hilton-milner-verifier/package-manifest.sha256: eb833bf4ad503fb2243882704492f6bf836525f4b619de8a1979ffc6f0f785c9
  attempts/wave198-orientation-lift-proof-b/package-manifest.sha256: ba949fa2ededb7a23596fa0b05ca9e2d259f0e6a18c042814e2f3bc87b5b9054
  attempts/wave198-orientation-lift-proof-a-audit/package-manifest.sha256: 60f5b4a87893fe0e820f05989e666c26abaaa8f30b9a5598a7a7db571740c924
  attempts/wave200-two-face-gluing-proof-b-audit/package-manifest.sha256: ca6e8763c085a1789a72390c6f6cf02a65c31c3235481d8b2bca833996aebeab
  attempts/wave201-multiplicity-weighted-fiber-loss-proof-a/package-manifest.sha256: 36d95b7d1bee4739cc5f33c780d22168fe58bf974904031db86d25da77bce695
method: >-
  Per-leaf multiset repetition decomposition in disjoint four-element
  pair fibers, separate deficient and Hilton--Milner equality centers,
  exact symbolic elimination, and coefficientwise budget subtraction.
  No graph, code, cover, SAT, LP, configuration, enumeration,
  isomorphism, or brute-force search.
command: >-
  python -B
  attempts/wave201-multiplicity-weighted-fiber-loss-proof-b-audit/exact_check.py
  --verify
  attempts/wave201-multiplicity-weighted-fiber-loss-proof-b-audit/exact-results.json;
  python -B -m unittest -v
  attempts/wave201-multiplicity-weighted-fiber-loss-proof-b-audit/test_exact_check.py
outputs:
  - agents/2026-07-29-wave201-multiplicity-weighted-fiber-loss-proof-b-audit.md
  - attempts/wave201-multiplicity-weighted-fiber-loss-proof-b-audit/
limitations:
  - This is a proof-B hostile audit, not clean-room verifier promotion.
  - The result is conditional on the frozen prism-free rank-11 endpoint.
  - It supplies no incompatible endpoint upper bound.
  - Rank 11, endpoint existence, strict original n3 improvement,
    external novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

The multiple-label fiber charge, all tight/deficient cases, global
elimination, and budget domination survive hostile audit. Conditionally,

```text
Q>=7059.                                          (1)
```

## 1. Same-fiber charges do not overlap

Fix a center and pair type `P`. Let the distinct full leaf values in its
four-element fiber have positive full multiplicities `r_z`. Then

```text
d_P=sum_z r_z,
u_P=number of such z,
rho_P=d_P-u_P=sum_z(r_z-1).                      (2)
```

For every selected nonprivate leaf value `y`, its selected multiplicity
satisfies `1<=m_y<=r_y`. Therefore

```text
rho_P-sum_selected(m_y-1)
 =sum_selected(r_y-m_y)+sum_unselected(r_z-1)
 >=0.                                           (3)
```

This identity is the clean multiple-label check. Distinct values use
different summands; no repeated occurrence is charged twice.

For a non-baseline fiber with `k` selected values, (3) gives

```text
rho_P-sum_selected(m_y-2)
 =[rho_P-sum_selected(m_y-1)]+k
 >=0.                                           (4)
```

For a degree-five baseline fiber with `k>=1`,

```text
(rho_P-1)-sum_selected(m_y-2)
 =[rho_P-sum_selected(m_y-1)]+(k-1)
 >=0.                                           (5)
```

If `k=0`, then `d_P=5` and the fiber contains at most four values, so
`rho_P=d_P-u_P>=1`; hence `rho_P-1>=0`. Thus (5) is valid in the empty,
singleton, and multiple-value cases.

## 2. Exactly three baselines at a tight center

Let `c_x` be the full flag count, `j_x` the distinct leaf count, and
`delta_x=36-j_x`.

If `c_x<=12`, the fiber partition and (4) give

```text
delta_x
 =36-3c_x+sum_P rho_P
 >=sum_selected_at_x(m_y-2).                    (6)
```

If `c_x=13`, the common-star branch is impossible. The complete
Hilton--Milner equality classification has exactly three pair types
with degree five in each of its two templates. Consequently

```text
delta_x
 =sum_(d_P=5)(rho_P-1)+sum_(d_P<5)rho_P.        (7)
```

There are exactly three, not merely at least three, baseline
subtractions in (7). Applying (4)--(5) fiber by fiber proves

```text
delta_x>=sum_selected_at_x(m_y-2)               (8)
```

at every center.

## 3. Global row and exact elimination

For `q` nonprivate selected orientations and

```text
epsilon=sum(5-m_y),
```

their total multiplicity is `5q-epsilon`. Summing (8) gives

```text
delta
 >=sum(m_y-2)
 =3q-epsilon.                                   (9)
```

Combine this with the exact Wave198 identity

```text
4q=297-3SF-3g-SH+epsilon+delta+eta.
```

Multiplying (9) by four and substituting for `4q` gives

```text
9SF+9g+3SH+delta+epsilon-3eta>=891.             (10)
```

The negative coefficient of `eta` is harmless: (10) is a derived row,
not a termwise nonnegative decomposition.

## 4. Budget subtraction

Substitute

```text
S5=5delta+5eta+epsilon
```

into the Wave198 multiplied budget `B`. Subtracting the left side of
(10) leaves exactly

```text
32SI+48S2+8SE2+28RA+12SL
 +4SF+4delta+8eta
 +4a1+24b3+8c2+16W.                            (11)
```

Every coefficient and every variable in (11) is nonnegative. The `g`,
`SH`, and `epsilon` coefficients cancel exactly. Hence `B>=891`.

At `C=4158,V=99`,

```text
Q0>=281457/40+891/40=7058.7.
```

Since `Q0` is integral and `Q>=Q0`, (1) follows. Adding the 693 verified
edge-isolated projective circuits gives 7,752 projective circuit classes
and 15,504 nonzero scalar circuit words.

The sealed proof-A package has 10 matching manifest entries, exact replay
passes, and all six tests pass. No source file was modified.

```text
same-fiber multiset charge:               AUDIT PASS
empty/single/multiple degree-five cases:  AUDIT PASS
exactly three HM baselines:               AUDIT PASS
global delta>=3q-epsilon:                 AUDIT PASS
budget difference:                       AUDIT PASS
budget floor B>=891:                      DERIVED
conditional Q>=7059:                     DERIVED
clean-room verifier promotion:           pending
endpoint contradiction:                  no
Conway-99 / external novelty:             UNKNOWN
```
