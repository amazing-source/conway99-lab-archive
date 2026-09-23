# Wave 197 proof-B audit: ten-flag label capacity

```yaml
role: proof_b
date_utc: 2026-07-29T05:18:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Hostile audit of the ten-flag capacity of one nonedge, its private-label
  weighted incidence row S10, its coupling to the Wave196 flag and label
  caps, and the exact conditional certificate Q>=7033.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave194-five-thirds-verifier/package-manifest.sha256: 236facbec2539a87e197fd0b2b8ca66bc0d53b12415fdf216acf410064d7ca64
  attempts/wave196-four-fiber-proof-b-audit/package-manifest.sha256: 1eb6c6abdc6855af950459ac524653108f5582d9686fbe4e6a0df89e9c39c14a
method: >-
  SRG triangle incidence, minimum-cover companion exclusion, a weighted
  private-label capacity count, and exact rational coefficient expansion.
  No graph, code, cover, SAT, LP, configuration, enumeration,
  isomorphism, or brute-force search.
command: >-
  python -B attempts/wave197-ten-flag-capacity-proof-b-audit/exact_check.py
  --verify attempts/wave197-ten-flag-capacity-proof-b-audit/exact-results.json;
  python -B -m unittest -v
  attempts/wave197-ten-flag-capacity-proof-b-audit/test_exact_check.py
outputs:
  - agents/2026-07-29-wave197-ten-flag-capacity-proof-b-audit.md
  - attempts/wave197-ten-flag-capacity-proof-b-audit/
limitations:
  - This is a proof-B derivation and audit, not verifier promotion.
  - It is conditional on the frozen prism-free rank-11 endpoint.
  - The rational active row is not a graph, cover, code, or flag system.
  - The improvement supplies no incompatible upper bound.
  - Rank 11, endpoint existence, strict original n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`AUDIT_PASS_DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

The per-label capacity, both couplings, and the exact certificate survive.
Conditionally,

```text
Q>=7033.
```

## 1. At most ten flags through one nonedge

Fix a nonedge `e={x,y}`.  The seven graph triangles through `y` partition
the 14 neighbors of `y` into pairs.  The two common neighbors of `x,y`
lie in distinct triangles: if they were adjacent, their edge would have
both `x` and `y` as common neighbors, contradicting `lambda=1`.

Those two triangles are not anticomplete to `x`.  Every other neighbor of
`y` is not adjacent to `x`, because `mu=2` has already accounted for all
common neighbors.  Hence exactly five graph triangles through `y` are
anticomplete to `x`.

A canonical exact-three flag centered at `x` and containing the oriented
label `x->y` must use one of those five triangles as its leaf triangle.
Canonical uniqueness permits at most one flag for each.  Thus at most
five flags containing `e` are centered at `x`; symmetrically, at most
five are centered at `y`.  Since the center of a flag realizing `e` must
be one endpoint of `e`,

```text
number of exact-three flags containing e <=10.  (1)
```

## 2. Weighted selected-type-three incidence

Let `U` be the label union of the selected exact-three circuits, and let
`s_e` be the number of selected exact-three circuits using `e in U`.
An inclusion-minimal cover cannot contain both members of one canonical
companion pair, because they have the same three labels.  Selected
exact-three circuits therefore inject into canonical flags, so (1) gives
`s_e<=10`.

Every selected exact-three circuit has three labels:

```text
sum_(e in U) s_e=3n3.                            (2)
```

The `p3` private type-three labels are distinct, and privacy gives
`s_e=1` on each of them.  On the other labels only the cap ten is used.
Therefore

```text
3n3
 <=p3+10(|U|-p3),
3n3+9p3<=10|U|.                                 (3)
```

This explains the coefficient nine; it is not an assumed multiplicity.

## 3. Coupling to the full flag pool

Wave196 proves, for `V=99` and `H=36V=3564`,

```text
J<=H,
|U|+a3+b3<=J,
SF=13V-n3-h-g>=0.                               (4)
```

The `a3+b3` assignments are distinct oriented private labels outside
`U`, including opposite orientations for the two type-two assignments
on one nonedge.  Combining (3)--(4),

```text
3n3+9p3+10a3+10b3<=10H,

S10=10H-3n3-9p3-10a3-10b3>=0.                  (5)
```

Also retain the verified old exact-three slot row

```text
SH=3h-a3-b3>=0.                                 (6)
```

## 4. Exact certificate

Use the Wave194 notation

```text
SI =I-2C,
S2 =p2-n2,
SE2=2r2-a2-c2,
RA =3h+y+3g-a2-a3-2b3-c2,
SL =n1+2n2+c1+2r2+y+2W-C,

Q0=n1+n2+2n3+r1+r2+2h+y+2g+W.
```

After the four raw identities, exact coefficient expansion gives

```text
Q0-(57C-263V)/30

 =4SI/5
  +6S2/5
  +SE2/5
  +7RA/10
  +3SL/10
  +S10/90
  +4SH/45
  +11SF/30
  +a1/10
  +3b3/5
  +c2/5
  +4g/15
  +2W/5.                                        (7)
```

Every term on the right is nonnegative.  At `C=4158,V=99`,

```text
(57C-263V)/30=70323/10.
```

Since `Q>=Q0` and `Q` is integral, (7) proves `Q>=7033`.  Adding the 693
verified edge-isolated projective circuits gives at least 7,726
projective circuit classes and 15,452 nonzero scalar circuit words.

The exact replay checks the active rational row

```text
n1=a2=y=33/5,
n2=p2=1518/5,
n3=1287,
p3=c1=3531,
b1=3036/5,
r1=20691/5,
r2=33/10,
all other split/pool variables zero.
```

All displayed slacks vanish and `Q0=70323/10`; this is arithmetic only,
not an asserted object.

## Boundary

```text
five flags per orientation:          DERIVED
ten flags per nonedge:               DERIVED
weighted private-label row S10:      DERIVED
Wave196 rows SF and J<=3564:          AUDIT PASS
exact coefficient identity:          PASS
conditional Q>=7033:                 DERIVED
independent verifier promotion:       pending
endpoint contradiction:              no
Conway-99 / external novelty:         UNKNOWN
```
