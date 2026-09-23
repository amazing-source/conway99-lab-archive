# Wave 198 proof B: orientation-lift gluing obstruction

```yaml
role: proof_b
date_utc: 2026-07-29T05:43:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: lift selected exact-three
  incidence from unordered nonedges to their two orientations, derive the
  strict global row S5, exclude the Wave197 saturation row, and prove
  Q>=7037 by an exact nonnegative coefficient certificate.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave194-five-thirds-verifier/package-manifest.sha256: 236facbec2539a87e197fd0b2b8ca66bc0d53b12415fdf216acf410064d7ca64
  verification/wave196-four-fiber-hilton-milner-verifier/package-manifest.sha256: eb833bf4ad503fb2243882704492f6bf836525f4b619de8a1979ffc6f0f785c9
  attempts/wave197-ten-flag-capacity-proof-b-audit/package-manifest.sha256: 553c1b9699dc1865679d65a8a7d3f8011d7bb59990b0d7c21322a980ce310a05
method: >-
  Orientation-sensitive incidence counting, the five-flags-per-oriented-
  nonedge capacity, privacy, verified full-pool separation, and exact
  rational coefficient algebra. No graph, code, cover, SAT, LP,
  configuration, enumeration, isomorphism, or brute-force search.
command: >-
  python -B attempts/wave198-orientation-lift-proof-b/exact_check.py
  --verify attempts/wave198-orientation-lift-proof-b/exact-results.json;
  python -B -m unittest -v
  attempts/wave198-orientation-lift-proof-b/test_exact_check.py
outputs:
  - agents/2026-07-29-wave198-orientation-lift-proof-b.md
  - attempts/wave198-orientation-lift-proof-b/
limitations:
  - This is a proof-B derivation, not verifier promotion.
  - The result is conditional on the frozen prism-free rank-11 endpoint.
  - The new rational boundary row is not a graph, cover, code, or flag
    construction.
  - The improvement supplies no incompatible upper bound.
  - Rank 11, endpoint existence, strict original n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

The two orientations of one nonedge cannot be collapsed without losing
capacity information.  Restoring them gives a strict row that excludes
the Wave197 active rational boundary and proves, conditionally,

```text
Q>=7037.                                          (1)
```

## 1. Orientation-lifted selected incidence

Let `U` be the union of labels on the selected exact-three circuits.  For
`e={x,y} in U`, define

```text
s_e = number of selected exact-three flags containing e,
t_e = number of occupied orientations among x->y and y->x.
```

Wave197 proves that at most five canonical flags containing `e` can have
either fixed center.  Therefore

```text
s_e<=5t_e.                                       (2)
```

An inclusion-minimal selected cover cannot contain both members of one
canonical companion pair, because they realize the same three labels.
Thus selected exact-three circuits inject into flags and

```text
sum_(e in U) s_e=3n3.                            (3)
```

Each of the `p3` private type-three labels occurs in exactly one selected
circuit.  Hence on a private label

```text
s_e=t_e=1,
s_e+4=5t_e.                                      (4)
```

On every other label, (2) is enough.  Summing (2)--(4) over `U`, and
writing `T=sum t_e` for the selected oriented-label union, gives

```text
3n3+4p3<=5T.                                     (5)
```

## 2. Coupling to the full flag pool

The `a3+b3` old-raw assignments are distinct oriented private labels on
unordered labels outside `U`.  They are therefore disjoint from the `T`
selected orientations.  The verified Wave196 full exact-three flag pool
has oriented union `J<=H`, where

```text
V=99,
H=36V=3564.
```

Consequently

```text
T+a3+b3<=J<=H.
```

Together with (5), this proves

```text
S5=5H-3n3-4p3-5a3-5b3>=0.                       (6)
```

This is strictly stronger than the unordered degree-ten row in the
relevant direction.  If

```text
SP=3n3-p3>=0
```

is the trivial private-label capacity of selected type-three circuits,
then exact expansion gives

```text
S10=2S5+SP.                                      (7)
```

The Wave197 rational active row has `S10=0` but `S5=-165`; it is excluded
by the orientation lift rather than by an integrality convention.

## 3. Exact certificate

Retain the verified Wave194 rows

```text
SI =I-2C,
S2 =p2-n2,
SE2=2r2-a2-c2,
RA =3h+y+3g-a2-a3-2b3-c2,
SL =n1+2n2+c1+2r2+y+2W-C,
SH =3h-a3-b3,
```

and the verified Wave196 flag-count row

```text
SF=13V-n3-h-g.
```

With

```text
Q0=n1+n2+2n3+r1+r2+2h+y+2g+W,
```

and the four raw identities, exact coefficient expansion gives

```text
Q0-(76C-349V)/40

 =4SI/5
  +6S2/5
  +SE2/5
  +7RA/10
  +3SL/10
  +S5/40
  +3SH/40
  +13SF/40
  +a1/10
  +3b3/5
  +c2/5
  +9g/40
  +2W/5.                                         (8)
```

Every term on the right is nonnegative.  With `C=4158,V=99`,

```text
(76C-349V)/40=281457/40=7036.425.
```

The verified pools give `Q>=Q0`; integrality proves (1).  Adding the 693
verified edge-isolated projective circuits gives at least

```text
7730
```

projective circuit classes and `15460` nonzero scalar circuit words.

## 4. Exact rational boundary

All eight structural slacks in (8), and every displayed remainder term,
vanish at

```text
n1=a2=y=297/20,
n2=p2=6237/20,
n3=1287,
p3=c1=13959/4,
b1=6237/10,
r1=82269/20,
r2=297/40,
all other split/pool variables zero.
```

It has `Q0=281457/40`.  This is a rational control for the displayed
linear relaxation only; it does not assert that the 99 local
Hilton--Milner templates glue.

## Boundary

```text
five-per-orientation premise:        AUDIT PASS (Wave197)
orientation-lifted row S5:           DERIVED
Wave197 active null:                 REFUTED as a feasible row
exact rational replay:               PASS
conditional Q>=7037:                 DERIVED
independent Wave198 verification:    pending
endpoint contradiction:              no
Conway-99 / external novelty:         UNKNOWN
```
