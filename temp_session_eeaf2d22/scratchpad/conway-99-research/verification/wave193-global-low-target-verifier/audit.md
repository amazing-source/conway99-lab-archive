# Independent Wave193 global low-target audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
117Q>=177C,
Q>=6291.
```

The theorem is a lower bound, not an endpoint contradiction.  Rank 11 and
endpoint existence remain open.

## Integrity and clean-room separation

The independent split-variable theorem, both capacity slacks, coefficient
identity, and an integer arithmetic control were frozen before source
inspection.  The mathematical payload has file SHA-256

```text
b26d13635181726b915f3698d663d61e74cecccd04c4879d29ed0af9678ff423.
```

The Wave193 source manifest has SHA-256

```text
0c6262b857d189c61d2ce4a9ea1804fbad4706727af29c4b1e011e44960060be.
```

All six direct inputs, all nine source entries, and every entry in the four
premise verifier manifests matched.  No discovery checker was imported or
executed before the independent mathematical result was frozen.

The independent audit found a different integer arithmetic control than the
source.  Both rows satisfy the displayed inequalities and give `Q0=6291`;
neither is asserted to be an object.

## 1. Raw assignments by source and multiplicity

Split raw assignment incidence as

```text
a1+a2+a3=n1,
b1+b3=2p2,
c1+c2=p3.                                       (1)
```

The subscript records exact cross multiplicity.

There is no `b2`: the selected type-two owner is already the unique
Wave181 exact-two circuit through each private label, while both outside
translates differ from it.  There is no `c3`: the privacy-free Wave191
local theorem excludes an exact-three circuit inside the type-three leaf
relation.

For the orbit-closed raw pool,

```text
r1=a1+b1+c1,
a2+c2<=2r2,
a3+b3<=3h,                                      (2)
```

and its number of circuits is `r1+r2+2h`.

## 2. Type-one exact-two raws force residuals

Fix a selected type-one owner with private label `e`.  Let `W_e` be the
short majority-axis relation and suppose its raw circuit is the canonical
exact-two checkerboard `D_e`.

If `D_e` is a proper subcircuit of `W_e`, subtract a scalar multiple of its
relation to cancel one conic coordinate.  The nonzero difference remains
on two proper endpoint-star subsets and therefore contains a circuit
crossing `e`.  It is not:

- the owner, because the majority translation omitted an owner coordinate;
  or
- `D_e`, because the subtraction omitted a conic coordinate.

If `W_e=D_e` projectively, the owner is one of the two nontrivial
checkerboard-axis words.  The other has profile `6+2`, weight eight, and
support containing neither the owner nor the conic.  It therefore forces
the same kind of residual.

In both cases the residual cannot be exact-two.  Wave181 uniqueness would
force it to equal `D_e`, whose support is not contained after cancellation.
Thus every `a2` assignment forces an exact-one or exact-three residual.
Wave190 gives the same conclusion for each `c2` assignment.

## 3. Residual flow and `SR`

The forced residual incidence is

```text
a2+c2.
```

No residual can enter an old exact-one raw circuit: a different label would
raise its multiplicity, while the source private label has only one raw
assignment.  It cannot enter an old exact-two raw circuit, by Wave181
uniqueness and the omitted support.

The old exact-three raw pairs contain the raw assignments `a3+b3`.
These occupy distinct label slots.  In particular, the two type-two
translates for one label cannot be companion mates.  A residual source had
an exact-two raw, so raw and residual cannot use the same orbit-label slot.
The old pairs therefore have unused capacity

```text
3h-a3-b3.
```

Close genuinely new exact-three residuals under companionship.  If `Y`
counts the resulting exact-one circuits and complete exact-three pairs,
their assignment capacity is at most `3Y/2`.  Consequently

```text
SR
 =3h+3Y/2-(a2+a3+b3+c2)
 >=0.                                            (3)
```

Old orbit closure and privacy keep the new pool disjoint from every
previous pool.

## 4. Privacy-free low leaf targets and `SL`

Let `U` be the union of labels served by selected type-three circuits.
Every label outside `U` must be covered by a selected type-one or type-two
circuit, so

```text
|U|>=C-(n1+2n2).                                 (4)
```

Choose one selected type-three leaf relation for each distinct label in
`U`.  The `3+6` relation has two proper star sides and contains a circuit
crossing its target label.  Wave191's local exclusion does not use privacy,
so the target circuit has exact multiplicity at most two.

The available low-label capacity is

```text
selected low:       n1+2n2,
old raw low:        r1+2r2,
new residual pool:  at most Y,
additional low W:   at most 2W.
```

The new residual contribution is `Y`, not `2Y`.  That closed pool contains
only exact-one circuits and exact-three pairs; an exact-three member cannot
be a low leaf target, so only its exact-one portion contributes, and that
portion is at most `Y`.

Combining with (4),

```text
SL
 =2n1+4n2+r1+2r2+Y+2W-C
 >=0.                                            (5)
```

The pool `W` is defined only after charging targets to every preceding
pool, making it disjoint by construction.

## 5. Exact coefficient identity

The disjoint circuit inventory is

```text
Q>=Q0,

Q0=n1+n2+2n3+r1+r2+2h+Y+W.
```

Using (1)--(5), direct exact expansion gives

```text
Q0-59C/39

 =(29/39)(I-2C)
  +(23/39)(p2-n2)
  +(3/13)(p3-n3)
  +(38/117)(2r2-a2-c2)
  +(2/117)(3h-a3-b3)
  +(76/117)SR
  +(1/39)SL
  +(17/39)(a1+a2)
  +(5/39)a3
  +(4/13)b1
  +(35/117)r2
  +(37/39)W.
```

Every term on the right is nonnegative.  Hence

```text
117Q>=177C.
```

For `C=4158`,

```text
59C/39=6290+4/13,
Q>=6291.
```

Adding the 693 verified edge-isolated projective circuits gives at least
6,984 projective short circuits and 13,968 scalar circuit words.  Wave188's
verified 18,018 all-short-word bound remains numerically stronger because
it includes nonminimal words.

## 6. Arithmetic controls and boundary

The independently frozen arithmetic control is

```text
b3=1280, c1=1598, c2=1,
n2=640, n3=1599, r2=1, h=427,
all other split and new-pool variables zero.
```

It has `Q0=6291`.  The source uses the equally valid row

```text
b3=1280, c1=r1=1599,
n2=p2=640, n3=p3=1599, h=427,
r2=Y=W=0,
all other split variables zero.
```

Both are arithmetic null controls only.  Neither constructs a cover,
circuit family, code, graph, or endpoint.

```text
independent math replay:  PASS
independent full replay:  PASS
independent tests:        8/8 PASS
source replay:            PASS
source tests:             6/6 PASS
all frozen hashes:        PASS
```

No graph, cover, code, SAT, LP, configuration, enumeration, or isomorphism
search was used in the proof or verifier package.  Rank 11, endpoint
existence, strict original `n3` improvement, external novelty, and
Conway-99 remain `UNKNOWN`.
