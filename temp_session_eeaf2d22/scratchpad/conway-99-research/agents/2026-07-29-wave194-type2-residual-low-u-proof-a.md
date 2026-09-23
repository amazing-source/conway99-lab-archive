# Wave 194 proof A: type-two residuals and joint low-target capacity

## Verdict

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

Under the frozen conditional prism-free rank-11 endpoint assumptions, the
number `Q` of projective short circuits cross-realizing graph nonedges
satisfies

```text
Q>=6930.
```

The improvement has two analytic inputs beyond Wave193:

1. every exact-three type-two raw circuit forces a second, distinct
   exact-one/exact-three residual assignment; and
2. a selected type-two label incidence cannot be charged once outside the
   selected-type-three label union and again inside it.

An exact nonnegative coefficient identity gives `3Q>=5C`. No graph, code,
cover, SAT, LP, configuration, enumeration, or isomorphism search is used.

```yaml
role: proof_a
date_utc: 2026-07-29T03:20:41Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: force a new residual from each
  exact-three type-two raw; split the new residual pool into exact-one
  circuits and exact-three companion pairs; couple the inside/outside
  use of selected type-two incidences in the type-three label union; and
  certify 3Q>=5C, hence Q>=6930.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave188-affine-star-word-amplification-verifier/package-manifest.sha256: e58bd132b1e1579f5e4e6570d7e0b4318a6c5f970342d4b9493e0c35a3c0dc74
  verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256: fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4
  verification/wave191-exact-three-residual-verifier/package-manifest.sha256: a14f43310fb5ead05c4bd50b376f3d9d90ec77a92bc00f8c3b7326013f975ab2
method: >-
  Ternary affine circuit elimination in the translated 6+2 and 2+6
  supports, exact-two uniqueness, exact-three center orientation,
  companion-closed residual capacity, joint label-union accounting, and
  an exact rational dual certificate. No graph, code, cover, SAT, LP,
  configuration, enumeration, or isomorphism search.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave194-type2-residual-low-u-proof-a\exact_check.py --verify
  attempts\wave194-type2-residual-low-u-proof-a\exact-results.json;
  .\.venv\Scripts\python.exe -B -m unittest -v
  attempts\wave194-type2-residual-low-u-proof-a\test_exact_check.py
outputs:
  - agents/2026-07-29-wave194-type2-residual-low-u-proof-a.md
  - attempts/wave194-type2-residual-low-u-proof-a/
limitations:
  - This is a proof-agent derivation, not verifier promotion.
  - The theorem is conditional on the frozen prism-free rank-11 endpoint.
  - The equality-face rows are arithmetic/accounting null controls, not
    endpoint, cover, circuit-family, code, or graph constructions.
  - The five-circuit packet description is an equality accounting face;
    no globally compatible packet system is constructed.
  - The bound supplies no incompatible upper bound.
  - Rank 11, endpoint existence, strict original n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## 1. Frozen pool system

Retain the selected-cover counts `n_i`, private-label counts `p_i`, and

```text
C=4158,
I=2*n1+2*n2+3*n3+p2+p3>=2*C,
p2>=n2,
p3>=n3.
```

Split raw assignment incidence by selected source type and exact
cross-multiplicity:

```text
a1+a2+a3=n1,       type-one raws;
b1+b3=2*p2,        type-two raws;
c1+c2=p3,          type-three raws.              (1)
```

There is no `b2`: a selected type-two circuit is already the unique
Wave181 exact-two circuit through either private label, and the two outside
translates differ from it. There is no `c3`: the verified Wave191 local
argument excludes exact-three type-three leaf extraction without using
privacy.

Let `r1`, `r2`, and `h` count, respectively, exact-one old raw circuits,
exact-two old raw circuits, and exact-three old raw companion pairs.
Then

```text
r1=a1+b1+c1,
a2+c2<=2*r2,
a3+b3<=3*h.                                      (2)
```

The last row counts three label slots per companion pair, not six
circuit-label incidences. The selected cover, selected type-three
companions, and the closed old raw pool are pairwise disjoint by the
verified Wave189 separation audit.

## 2. Exact-three type-two raws force new residuals

Fix a private label `e={x,y}` of a selected type-two checkerboard conic.
Wave186 supplies two outside translated relations:

```text
W_x: profile 6 on the x-star and 2 on the y-star,
W_y: profile 2 on the x-star and 6 on the y-star.
```

Suppose the raw circuit `D_x` extracted from `W_x` is exact-three.
Wave180 gives it a unique center. Since one of its three labels is
`{x,y}`, that center is `x` or `y`; its `(3 or 4)+1` center/leaf profile
fits in `W_x` only when the center is `x`. Thus `D_x` has a unique
`y`-star leaf coordinate.

The circuit `D_x` is a proper subcircuit of the weight-eight relation
`W_x`. Cancel its unique leaf coordinate. The difference is a nonzero
relation whose support is nonempty and proper on both endpoint stars:
one `y`-star coordinate remains, while at least two `x`-star coordinates
remain because `D_x` uses only three or four of the six. Every proper
subset of either point-star is independent, so a minimal dependent subset
of the difference crosses `e`. Call one such circuit `R_x`.

The support of `R_x` omits:

- the canceled coordinate common to the two exact-three companions, so it
  is neither `D_x` nor its mate; and
- a canonical conic coordinate already omitted by `W_x`, so it is not the
  selected checkerboard conic.

Wave181 uniqueness therefore excludes exact multiplicity two for `R_x`.
It has exact multiplicity one or three. The symmetric argument gives
`R_y` from every exact-three raw inside `W_y`.

First, `R_x` cannot silently be the other raw circuit extracted from
`W_y`. If that other raw is exact-one, a common support would lie in at
most two `x`-star coordinates (from `W_y`) and the single remaining
`y`-star coordinate of `R_x`, hence would have weight at most three. If it
is exact-three, it is centered at `y`, whereas every exact-three circuit
inside the support of `R_x` is centered at `x`; it is neither the same
circuit nor a companion mate. Exact multiplicity two is already excluded.

The two same-label residuals, when both raws are exact-three, also consume
distinct residual capacity. Indeed:

- `R_x` has at most one `y`-star coordinate, while `R_y` has at most one
  `x`-star coordinate. If they were the same exact-one circuit, its support
  would have at most one coordinate on each side and hence weight at most
  two, contradicting dual distance at least four.
- If both are exact-three, containment orients `R_x` at center `x` and
  `R_y` at center `y`. They are neither the same circuit nor companion
  mates, because an exact-three companion pair has one common center.

Thus every assignment counted by `b3` forces one additional residual
assignment. This is separate from the original `b3` raw assignment.

The type-one `a2` residual lemma from Wave193 and the verified type-three
`c2` checkerboard subtraction supply one residual assignment for every
`a2+c2` assignment. The old exact-three raw pairs already have
`a3+b3` occupied label slots. Therefore the total label-slot demand on old
and new exact-three/one pools is

```text
a2+a3+2*b3+c2.                                  (3)
```

There is no hidden exact-one collision in this count. An exact-one circuit
realizes only its source label, so residuals keyed by different private
labels cannot coincide with one another or with old exact-one raws for
different labels. For one type-two private label, the only other raw is
the opposite translated extraction, excluded above even when it is
exact-one; if both raws are exact-three, the two residuals are separated
above as well. Type-one and type-three sources have only one raw
assignment for each private label. These observations exhaust the
same-label cases.

## 3. Split residual capacity

Close every genuinely new exact-three residual under the Wave180 companion
involution. Let

```text
y = number of exact-one circuits in the new residual pool,
g = number of exact-three companion pairs in that pool.
```

The new pool contains `y+2g` circuits and has assignment capacity at most
`y+3g`. Combining this with the `3h` old-pair slots and (3) gives

```text
S_R
 =3*h+y+3*g-(a2+a3+2*b3+c2)
 >=0.                                             (4)
```

Privacy excludes the selected pools, exact-two uniqueness excludes the old
low conics, and orbit closure prevents a new companion from silently
returning to an old exact-three pair.

## 4. Joint capacity on the type-three label union

Let `U` be the set of nonedge labels appearing in at least one selected
type-three circuit. For each `e in U`, choose one selected type-three flag
containing `e` and form its `3+6` leaf relation. Its two star sides are
proper, so it contains a circuit crossing `e`; the privacy-free Wave191
local exclusion makes every chosen target exact-one or exact-two.

Let `k` be the number of selected type-two label incidences that lie in
`U`. Every selected type-one label is private and hence outside `U`.
Counting selected incidences outside `U` gives

```text
C-|U|<=n1+2*n2-k.                                (5)
```

For targets inside `U`, the available already-counted low capacity is:

```text
selected type-two incidences in U:        k,
old raw exact-one from type three:        c1,
old raw exact-two circuits:             2*r2,
new exact-one residual circuits:           y.
```

The sharper terms deserve emphasis:

- a selected type-two circuit contributes only its actual `k` incidences
  in `U`; the complementary incidences have already been used in (5);
- `a1` and `b1` exact-one raw circuits serve private type-one/type-two
  labels outside `U`, so only `c1` can contribute here; and
- exact-three new pairs `g` cannot be low leaf targets.

Let `W` count all additional low circuits needed after those collisions.
They have capacity at most two labels each. Hence

```text
|U|<=k+c1+2*r2+y+2*W.                            (6)
```

Adding (5) and (6) cancels the unknown `k`:

```text
S_L
 =n1+2*n2+c1+2*r2+y+2*W-C
 >=0.                                             (7)
```

This joint row is stronger than bounding the inside and outside uses of a
selected type-two circuit separately.

## 5. Exact certificate

The disjoint circuit pools give

```text
Q>=Q0,

Q0=n1+n2+2*n3+r1+r2+2*h+y+2*g+W.                (8)
```

Define

```text
S_I=I-2*C,
S_2=p2-n2.
```

Using the four identities (1), direct exact expansion gives

```text
Q0-5*C/3

 =(2/3)*S_I
  +S_2
  +(2/3)*S_R
  +(1/3)*S_L
  +(1/3)*a1
  +(1/6)*b1
  +(1/2)*b3
  +(1/3)*r2
  +(1/3)*W.                                      (9)
```

Every term on the right is nonnegative. Therefore

```text
3*Q>=5*C.                                        (10)
```

For `C=4158`,

```text
Q>=6930.                                         (11)
```

Adding the 693 verified edge-isolated projective circuits gives at least

```text
7623
```

projective short-circuit classes and the circuit-specific scalar
consequence

```text
B4+B5+B6+B7+B8+B9>=15246.
```

Wave188's verified `18018` bound on all short dual words remains
numerically stronger because it also includes nonminimal words.

## 6. Full equality face

Equality in (9), together with the unused nonnegative capacity rows in
(2), forces

```text
n2=p2=a1=a2=b1=b3=c2=r2=y=g=W=0,
a3=n1=3*h,
p3=c1=r1=3*n3,
h+n3=C/3.                                        (12)
```

Conversely every nonnegative arithmetic row of the form

```text
0<=t<=C/3,

h=t,
n3=C/3-t,
n1=a3=3*t,
p3=c1=r1=C-3*t,
all other variables zero                         (13)
```

saturates all displayed inequalities and has `Q0=5C/3`.

This is a one-parameter five-circuit packet accounting face. The
`h+n3=C/3` disjoint label triples each carry:

- one exact-three companion pair; and
- three exact-one circuits, one for each label.

At the `n3` end of the orientation, one base exact-three circuit is
selected and its companion plus the three type-three leaf-extraction
circuits are outside the cover. At the `h` end, the three exact-one
circuits are selected type-one owners and the base companion pair is in
the raw pool. Thus each accounting packet has five circuits whichever
cover orientation is chosen.

Equation (13) is not a proof that compatible canonical packets, a cover,
an endpoint code, or a graph exist. In particular, the packet description
records the forced circuit/label incidence structure; it does not promote
an unverified global support gluing.

For `C=4158`, two endpoint null controls are:

```text
t=0:
  n3=1386, p3=c1=r1=4158, Q0=6930;

t=1386:
  n1=a3=4158, h=1386, Q0=6930.
```

Both are arithmetic controls only.

## Boundary

```text
conditional Q>=6237 theorem:      VERIFIED (Wave191)
conditional Q>=6238 theorem:      VERIFIED (Wave192)
conditional Q>=6291 theorem:      VERIFIED (Wave193)
conditional Q>=6930 theorem:      DERIVED
independent verification of 6930: pending
rank 11 / endpoint excluded:      no
strict original n3 improvement:   no
Conway-99 / external novelty:     UNKNOWN
```
