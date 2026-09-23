# Wave 190 proof B: residual-cancellation stability

```yaml
role: proof_b
date_utc: 2026-07-29T02:45:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional rank-11 endpoint: quantify the extra short circuits forced
  when type-three leaf extractions land on exact-two checkerboard conics,
  and derive a stability improvement from Q>=4852 to Q>=5544.
inputs:
  attempts/wave189-degree7-star-complete/package-manifest.sha256: dce4157a05fc20f9b3965ec9830a08f893eeefacdb347b084af13807fa417c90
method: >-
  Assignment-capacity slack, exact-one/exact-two/exact-three separation,
  checkerboard residual circuit extraction, companion-orbit label capacity,
  and an exact coefficient certificate. No graph, code, SAT, cover,
  configuration, isomorphism, LP, or enumeration search.
command: python -B attempts/wave190-residual-stability-proof-b/exact_check.py
outputs:
  attempts/wave190-residual-stability-proof-b/exact_check.py: cfe407503b2c327e89dab4ae3707d091228c2c5200e729cf9fc9406a6a856259
limitations:
  - Independent verification is required.
  - The argument inherits the derived Wave187 singleton-extraction input
    frozen by Wave189.
  - The sharp row is an arithmetic pool configuration, not an actual cover.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

The Wave 189 residual cancellation has a uniform stability form:

```text
Q>=5544,
```

where `Q` counts nonedge-realizing projective short circuits.  The gain is
not obtained by repeating the equality contradiction.  It follows by
charging every type-three leaf assignment that lands on an exact-two conic
and allowing maximal reuse by the existing exact-three companion orbits.

The result is `DERIVED`, not `VERIFIED`.

## 1. Assignment slack

Retain the Wave 189 notation.  The noncompanion extraction pool `X`
decomposes as

```text
r low circuits of exact multiplicity at most two,
h complete exact-three companion pairs.
```

The extraction-assignment count is

```text
A=n_1+2p_2+p_3.
```

The center-orientation theorem gives

```text
A<=2r+3h.
```

Define its integral slack

```text
delta=2r+3h-A>=0.                                (1)
```

Let `r_1` be the number of exact-one circuits among the `r` low circuits.
An exact-one circuit receives at most one assignment, an exact-two circuit
at most two, and an exact-three pair at most three.  Therefore

```text
A<=r_1+2(r-r_1)+3h=2r-r_1+3h,
r_1<=delta.                                      (2)
```

## 2. Many type-three assignments land on conics

Let `a_H` be the number of all raw extraction assignments landing in the
`h` exact-three companion pairs, and let `q_H` count the type-three raw
assignments among them.  There are `p_3` type-three leaf assignments.  At
most `r_1<=delta` land on exact-one circuits, and exactly `q_H` of them land
in the exact-three pairs.  Consequently at least

```text
k>=p_3-r_1-q_H
 >=p_3-delta-q_H                                 (3)
```

type-three leaf assignments land on exact-two circuits.

For each such private label `e`, Wave 181 makes the chosen extraction the
unique canonical checkerboard conic `r_e`.  Normalize the `3+6` leaf word
`w_e` to coefficient two on all nine positions.  As in Wave 189, either
residual

```text
w_e-r_e, w_e-2r_e
```

has profile `2+5` and contains a short circuit `E_e` crossing `e`.

## 3. Where a residual circuit can collide

The residual circuit `E_e` is outside the selected cover by privacy.  It is
outside the selected-companion pool: otherwise the selected twin of that
companion would also cover `e`, with the same-owner case excluded by the
omitted leaf triangle.

It is also outside the low part of `X`.

- If `E_e` has exact multiplicity one, it cannot be an extraction chosen
  for a different private label, because it would then cross both labels.
  The sole type-three extraction chosen for `e` is `r_e`, not `E_e`.
- If `E_e` has exact multiplicity two, Wave 181 uniqueness makes it the
  canonical conic `r_e`, which the residual does not contain.

Thus an existing member of `X` can absorb `E_e` only if it lies in one of
the `h` exact-three companion pairs.  Raw and residual assignments must now
be charged to the same three-label set of each pair.

For any private label `e`, at most one raw assignment can land in a fixed
pair.  Type one and type three supply only one raw circuit.  Type two
supplies two, but Wave 189's center-orientation theorem says they cannot be
companion mates.  Moreover:

- if the owner of `e` has type one or two, there is no type-three residual
  for `e`; and
- if its owner has type three, a raw assignment in the exact-three pair
  means that the raw assignment did not land on an exact-two conic, so no
  residual for `e` was generated.

Therefore raw and residual uses are mutually exclusive label by label.
After `a_H` raw uses, the `h` pairs can absorb residuals for at most

```text
3h-a_H
```

further labels.

Let `Y` count residual circuits genuinely outside the selected cover,
selected companions, and `X`.  Each new circuit crosses at most three
labels.  Equations (2)--(3) therefore give

```text
3Y
 >=k-(3h-a_H)
 >=p_3-r_1-q_H-3h+a_H
 >=p_3-delta-3h,

delta+3h+3Y>=p_3.                                (4)
```

The last inequality uses `a_H>=q_H`.  Every collision allowed by exact
cross-multiplicity is retained in (4).

## 4. Stability inequality

The disjoint pools give

```text
Q>=N+n_3+r+2h+Y.
```

From (1),

```text
r=(A+delta-3h)/2.
```

Hence

```text
Q
 >=N+n_3+A/2+delta/2+h/2+Y.
```

Equation (4), together with nonnegativity of `delta,Y`, implies

```text
3delta+3h+6Y
 >=delta+3h+3Y
 >=p_3.
```

After multiplying the bound for `Q` by twelve,

```text
12Q
 >=12N+12n_3+6A+2p_3.
```

Dividing by two gives

```text
6Q
 >=6N+6n_3+3A+p_3
 =9n_1+6n_2+12n_3+6p_2+4p_3.                   (5)
```

Its coefficient row has the exact decomposition

```text
9n_1+6n_2+12n_3+6p_2+4p_3

=4(2n_1+2n_2+3n_3+p_2+p_3)
 +n_1+2(p_2-n_2).                                (6)
```

Minimality gives `p_2>=n_2`.  The private-incidence row is at least `2C`.
Therefore

```text
6Q>=8C,
Q>=4C/3.
```

With `C=4158`,

```text
Q>=5544.                                          (7)
```

## 5. Sharp relaxation row

The following integer row meets the derived bound:

```text
n_3=1386, p_3=4158,
n_1=n_2=p_2=0,
r=0, h=1386,
delta=0, Y=0,
Q=5544.
```

Here every raw type-three assignment lands in an exact-three extraction
pair, so no checkerboard residual is generated.  This is only an arithmetic
hostile control.  No cover realizing it is asserted.

## 6. Consequence and boundary

Adding the 693 verified edge-isolated projective circuits gives

```text
projective short circuit classes>=5544+693=6237,
B_4+B_5+B_6+B_7+B_8+B_9>=12474                  (circuits only).
```

Wave 188's verified `18018` lower bound remains stronger for all short dual
words, including nonminimal ones.  The present result is a circuit-level
stability refinement.

No rank-11 contradiction follows.  Endpoint existence, Conway-99, and
external novelty remain `UNKNOWN`.
