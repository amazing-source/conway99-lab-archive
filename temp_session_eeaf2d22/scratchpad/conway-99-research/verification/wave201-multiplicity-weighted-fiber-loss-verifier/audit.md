# Independent Wave201 multiplicity-weighted fibre-loss audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Conditionally on the frozen prism-free rank-11 endpoint,

```text
delta_x >= sum_nonprivate_y (m_x(y)-2)          (1)
```

holds at every center.  Its global consequence and exact certificate
give

```text
Q>=7059.
```

Adding the 693 verified edge-isolated projective circuits gives at least
7,752 projective short circuits, or 15,504 nonzero scalar short-circuit
words.

The source-blind mathematical result was frozen at SHA-256

```text
b2f3bc49fd64d2297464a2a4a35ee3a6d0682dca85c86ae0af98eb638033828c
```

before either Wave201 source was opened.  The proof uses exact multiset
identities, the two fixed Hilton--Milner equality formulas, and rational
coefficient algebra.  It performs no graph, configuration, flag-family,
cover, SAT, LP, enumeration, isomorphism, or brute-force search.

## 1. Arbitrary multiplicities in one fibre

Fix a center and one pair type.  Let the distinct full-pool leaf labels
in its four-point fibre have positive multiplicities `n_z`; let a
selected nonprivate subcollection have multiplicities `m_z<=n_z`.
Write

```text
d=sum_z n_z,
u=number of full labels,
r=number of selected nonprivate labels.
```

The fibre's exact union loss is `d-u=sum_z(n_z-1)`.  Value-by-value
subtraction gives

```text
(d-u)-sum_selected(m_z-2)

 =sum_selected(n_z-m_z+1)
  +sum_unselected(n_z-1)
 >=r>=0.                                        (2)
```

This identity is the collision audit:

- any number of selected labels may share the same fibre;
- their charges occupy different leaf-value summands;
- selected multiplicity need only satisfy `m_z<=n_z`;
- unselected full-pool labels remain in both the union and the exact
  loss; and
- `m_z=1` is allowed and contributes `-1` to the proposed weight.

Thus no selected occurrence is mistaken for an independent full-pool
occurrence, and no repeated occurrence is charged twice.

## 2. Deficient and tight centers

Let `c_x` be the full-pool flag count, `j_x` its distinct oriented leaf
union, and `delta_x=36-j_x`.

If `c_x<=12`, the pair fibres partition the leaf occurrences, so

```text
delta_x
 =36-3c_x+sum_P(d_P-u_P)
 >=sum_nonprivate_y(m_x(y)-2),                  (3)
```

by (2) and the nonnegative spare term `36-3c_x`.

If `c_x=13`, the common-star branch is impossible by the sealed Wave196
theorem.  Each of the two Hilton--Milner equality formulas has exactly
three pair types of degree five.  Those three fibres each have at least
one unavoidable repeat because they contain only four leaf values.

For a degree-five fibre containing `r_P>=1` selected values, (2) gives

```text
(d_P-u_P)-1
 >=sum_selected(m_z-2)+(r_P-1)
 >=sum_selected(m_z-2).                         (4)
```

If `r_P=0`, the weighted sum is empty and the four-point cap gives
`(d_P-u_P)-1>=0`.  No baseline is subtracted from any other fibre.
Subtracting exactly the three baselines proves (1) at a tight center.

## 3. Global elimination

Let `q` count nonprivate selected orientations and

```text
epsilon=sum_nonprivate(5-m_y).
```

Summing (1) gives the new nonnegative slack

```text
SM=delta-3q+epsilon>=0,                          (5)
```

because

```text
sum_nonprivate(m_y-2)=3q-epsilon.
```

The independently reconstructed Wave198 identity is

```text
4q=3V-3SF-3g-SH+epsilon+delta+eta.              (6)
```

At `V=99`, eliminating `q` from (5)--(6) is equivalent to

```text
9SF+9g+3SH+delta+epsilon-3eta>=891.             (7)
```

The negative `eta` coefficient is not treated termwise.  Row (7) is a
derived inequality; its use below has a nonnegative exact remainder.

## 4. Exact certificate

Substitution into the Wave198 coefficient identity gives

```text
Q0-(19C-85V)/10

 =4SI/5+6S2/5+SE2/5+7RA/10+3SL/10
  +delta/10+eta/5+SM/10+SF/10
  +a1/10+3b3/5+c2/5+2W/5.                      (8)
```

Every term on the right is nonnegative.  Direct expansion after the four
raw split identities has zero residual coefficient vector.

At `C=4158,V=99`,

```text
(19C-85V)/10=70587/10=7058.7.
```

Since `Q0` is integral and `Q>=Q0`, equation (8) proves `Q>=7059`.

Equivalently, multiplying the old Wave198 budget by 40 and subtracting
(7) leaves

```text
32SI+48S2+8SE2+28RA+12SL
+4SF+4delta+8eta
+4a1+24b3+8c2+16W>=0.
```

The two certificate forms agree exactly.

## 5. Equality and near-equality controls

The independent checker supplies two arithmetic controls.

1. A rational row makes every term in (8) zero and has
   `Q0=70587/10`.
2. An integer row has `Q0=7059` and scaled certificate budget three,
   supplied solely by `delta=3`.  Its nonprivate multiplicity profile is

   ```text
   one label of multiplicity 1,
   232 labels of multiplicity 2,
   four labels of multiplicity 3.
   ```

   Thus `q=237`, total nonprivate selected incidence is 477,
   `epsilon=708`, and `sum(m-2)=3=delta`.

These are coefficient/accounting controls only.  Neither is asserted to
be a graph, flag family, code, cover, or endpoint object.

## 6. Sealed source comparison

Only after the independent freeze were the two sources opened.

- Proof A manifest
  `36d95b7d1bee4739cc5f33c780d22168fe58bf974904031db86d25da77bce695`
  has ten matching entries, exact replay passes, and all 6 tests pass.
- Hostile proof B manifest
  `d0c98bd36172d010596c2b428e5827438c633e4db9e0ed5783e18d69e2caf97c`
  has eleven matching entries, exact replay passes, and all 7 tests
  pass.

Both sources agree with the independently frozen result on the
value-by-value fibre decomposition, the empty/single/multiple selected
cases, exactly three tight-center baselines, global row (5), budget floor
891, and `Q>=7059`.  No source repair is needed.

The independent checker additionally includes a literal multiplicity-one
hostile profile and the rational/integer sharpness controls.

## Boundary

```text
arbitrary same-fibre multiplicities:    VERIFIED
m=1 and selected-vs-full guard:         VERIFIED
deficient and tight local cases:        VERIFIED
delta>=3q-epsilon:                      VERIFIED
exact target 70587/10:                  VERIFIED
conditional Q>=7059:                    VERIFIED_WITH_SCOPE
graph / flag family / code / cover:     not constructed
endpoint contradiction:                 no
rank 11 / Conway-99 / novelty:          UNKNOWN
```
