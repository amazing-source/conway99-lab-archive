# Wave 192 proof B: canonical-square translation obstruction

```yaml
role: proof_b
date_utc: 2026-07-29T03:08:51Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: complete equality-face analysis
  for the Wave191 bound Q>=6237, canonical-C4 axis-translation obstruction,
  type-three private leaf-word minimality, and strict exclusion of Q=6237.
inputs:
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256: fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4
  verification/wave190-residual-stability-verifier/package-manifest.sha256: 15686d17472fd60122072b3d679980d90d3cfe12fd87e5359344e52e216f1280
  attempts/wave191-exact-three-residual-proof-a/package-manifest.sha256: a0e2697b7e826f5543c2e007a1428633e37fb54e9e8449e73a731a7291f468c4
  verification/2026-07-29-wave191-refinement-verifier-addendum.md: 19f660194d78ea80428c40e66054791f10643002318f429b5a5e68fb46018c7c
  verification/2026-07-29-wave191-joint-capacity-verifier-addendum.md: c0d5af33fe37e95f1040658b0ebdf1ed67cc5c650ad2b5f648fc7c2176801b69
method: >-
  Equality-slack reconstruction, signed canonical-square/star cochains,
  ternary circuit elimination, exact-two uniqueness, proper-star
  independence, and the privacy incidence geometry of a minimal cover.
  No graph, cover, code, SAT, LP, configuration, isomorphism, or
  exhaustive search.
command: >-
  python -B attempts/wave192-c4-cohomology-proof-b/exact_check.py --verify
  attempts/wave192-c4-cohomology-proof-b/exact-results.json;
  python -B -m unittest -v
  attempts/wave192-c4-cohomology-proof-b/test_exact_check.py
outputs:
  - agents/2026-07-29-wave192-c4-cohomology-proof-b.md
  - attempts/wave192-c4-cohomology-proof-b/
limitations:
  - Independent verification is required.
  - The theorem is conditional on the prism-free rank-11 endpoint and the
    frozen Wave191 circuit bound.
  - The cohomological language records exact relation-code additions; no
    unproved topological exactness or square-span theorem is used.
  - Rank 11, endpoint existence, external novelty, and Conway-99 remain
    UNKNOWN.
```

## Verdict

The equality case in the conditional Wave191 bound is impossible:

```text
Q>=6238.
```

Here `Q` is the number of projective short circuits cross-realizing at
least one graph nonedge.  The improvement is only one circuit, but it is a
genuine analytic exclusion of the complete `Q=6237` face.

Adding the 693 verified edge-isolated projective circuits gives

```text
at least 6931 projective short circuits,
B_4+...+B_9>=13862
```

from circuits alone.  The verified Wave188 bound `18018` for all short
dual words remains numerically stronger because it includes nonminimal
words.

## Signed relation-code interpretation

Let `K` be the ternary relation code on the 231 triangle columns.  For a
point `x`, write

```text
sigma_x=sum_(T contains x) e_T in K
```

for its full star word.  For a canonical quadrilateral paired by the
nonedge involution `e <-> e*`, write `q_e=q_e*` for its checkerboard word.
In its four boundary coordinates this is

```text
(1,2 | 2,1).
```

The operations below are additions in `K`.  Calling them cochains is only
a useful language: the proof does not assume that all square cocycles are
star coboundaries, nor the unproved rank identity from the Wave181
literature boundary.

The key local coset is

```text
q_e+<sigma_x>.
```

Its two nonzero axis translates have profiles `6+2`, weight eight, and
omit opposite `x`-side square coordinates.  Thus a saturated equality
face cannot identify the two supports.

## Equality reconstruction

Retain the Wave191 variables.  Its exact coefficient identity is

```text
12Q
 >=9I+6(p_2-n_2)+p_2+3(p_3-n_3)
 >=18C,
C=4158.
```

If `Q=6237`, every displayed slack vanishes:

```text
p_2=n_2=0,
p_3=n_3,
I=2C,
n_1+2n_3=C.                                      (1)
```

The Wave191 pool penalty is

```text
delta/2+h/2+Y
 =(delta+2Y)/3+(delta+3h+2Y)/6.
```

Equality therefore gives

```text
h=0,
delta+2Y=p_3,
u=0,
Z=2Y.                                            (2)
```

Every residual forced from a type-three raw conic is outside the old low
pool by Wave190.  It also cannot have exact multiplicity two: Wave181
makes the raw conic the unique exact-two circuit through its label, while
the residual omits a coordinate of that conic.  After closing exact-three
residuals under companionship, write the new pool as `y` exact-one
circuits and `g` exact-three pairs.  Then

```text
Y=y+2g,
Z<=y+3g.
```

Together with `Z=2Y`, this forces

```text
Y=Z=y=g=0.                                       (3)
```

Consequently every type-three private raw is exact one, while every
type-one raw is exact two.  More precisely,

```text
delta=r_1=n_3,
r=2079,
r-r_1=n_1/2.                                    (4)
```

All `n_1` type-one assignments saturate the two label slots of the
`n_1/2` exact-two circuits.  Hence their private labels occur in canonical
involution pairs `{e,e*}`, one checkerboard conic `q_e` per pair.

## Type-one axis translations cannot saturate

Fix one type-one private label `e=xy`, its selected exact-one circuit
`c_e`, and the endpoint axis `x` used by its Wave189 majority translation.
Equality says that the extracted raw circuit is the canonical conic
`q_e`.

In fact the translated relation must equal `q_e` projectively.  If it
strictly contained `q_e`, subtracting a scalar multiple of `q_e` and
taking a minimal dependent subset would give another short cross circuit
for `e`.  Both star sides remain proper.  Privacy and the complete pool
description (3)--(4) exclude collision with any already counted circuit.

Thus, after normalization,

```text
c_e=q_e-a*sigma_x,  a in F_3^*.                  (5)
```

Now use the other nonzero axis translate

```text
c'_e=q_e+a*sigma_x.                              (6)
```

Because the two `x`-side coefficients of `q_e` are `1,2`, (5) and (6)
each have profile `6+2`, but they cancel opposite square coordinates.
Any circuit in `supp(c'_e)` crosses `e`.  It is neither `q_e` nor `c_e`,
because each of those uses the square coordinate omitted by (6).  It
cannot be any other counted circuit because `e` is private.

Equation (6) therefore supplies an extra nonedge-realizing short circuit,
contrary to `Q=6237`.  Hence

```text
n_1=0.                                           (7)
```

This answers the canonical-involution question sharply: two opposite
type-one private labels can be paired by one conic at the level of local
linear relations, but they cannot occur in the saturated `Q=6237`
geometry.  The unused sign on either chosen axis forces another circuit.

## Type-three singleton leaf words do not close globally

Equations (1) and (7) give

```text
n_3=p_3=2079.
```

For a selected type-three flag `(x,T)` and its private label `e=xy`, let

```text
w_(F,e)=c_4(x,T)+2*sigma_y.
```

It is the all-two `3+6` leaf relation of weight nine.  Equality forces its
assigned exact-one circuit to be the whole word.  Indeed, if a proper
circuit lay inside it, subtracting that circuit and extracting minimally
would give a distinct short circuit crossing the same private label.  It
cannot be one-sided because both star sides are proper, and it cannot
collide with the source companion pair because `w_(F,e)` omits `T`.
Thus every private leaf word must itself remain a circuit.

But the selected label incidence now has

```text
3n_3=6237
```

incidences on `C=4158` labels.  The `p_3=2079` private labels occur once.
Every remaining label occurs at least twice, and the remaining 4158
incidences force each of the other 2079 labels to occur exactly twice.

Choose such a shared label `f` and either selected flag containing it.
Form the same `3+6` leaf relation `w_(F,f)`.  The Wave191 local
exact-three exclusion is label-local and uses no privacy, so a minimal
circuit in this relation has exact multiplicity one or two.  It is
therefore outside every selected exact-three companion pair.  It is not a
private singleton leaf circuit, because those have exact multiplicity one
and cross their distinct private labels.  By (7), there is no type-one
conic pool.

This is again a new short nonedge-realizing circuit, contradicting
`Q=6237`.

## Boundary

```text
conditional Q>=6238 theorem:      DERIVED
Q=6237 equality face:             excluded
type-one paired-axis face:        excluded at saturation
private type-three leaf words:    forced circuits at equality
shared-label leaf continuation:   forces the strict circuit
independent verification:         pending
rank 11 / endpoint excluded:      no
Conway-99 / external novelty:     UNKNOWN
```

