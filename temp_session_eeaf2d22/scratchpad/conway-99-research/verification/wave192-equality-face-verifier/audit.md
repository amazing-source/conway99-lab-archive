# Independent Wave192 equality-face audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Under the frozen conditional prism-free rank-11 endpoint assumptions,

```text
Q>=6238.
```

The entire `Q=6237` equality face is `REFUTED`.  The one-unit strict
improvement supplies no incompatible upper bound, so rank 11 and endpoint
existence remain open.

## Integrity and clean-room separation

The independent equality reconstruction, canonical-axis vectors, and both
branch contradictions were frozen before source inspection.  The frozen
mathematical payload has file SHA-256

```text
9da9dd584e3f004e9dc5e29c051eca71641165dddd1d0956cfbe7673956a669b.
```

The exact-two residual exclusion used to sharpen `Z` versus `Y` was already
sealed in the Wave191 verifier premise.  The final checker independently
reconstructs its capacity consequence before comparing the Wave192 exact
result.

The Wave192 source manifest has SHA-256

```text
630183eb6c94836daf2e4202b69acc5c7fbd1b7ce7c6c335573e99a7ea1d8ede.
```

All six direct inputs, all nine source entries, and every entry in the four
premise verifier manifests matched.  No discovery checker was imported or
executed before the independent mathematical result was frozen.

## 1. Complete equality face

Wave191 proves

```text
12Q
 >=9I+6(p2-n2)+p2+3(p3-n3)
 >=18C,
```

with `C=4158`.  Assume `Q=6237=3C/2`.  Equality forces

```text
I=2C,
n2=p2=0,
p3=n3.
```

Put

```text
m=n3=p3.
```

Then

```text
n1=C-2m,
B=n1+2n3=C,
A=n1+p3=C-m,
0<=m<=2079.                                      (1)
```

Let `r1` count exact-one low raw circuits, `t` count type-three raws on
them, `u=r1-t`, and `Z` count residual assignments outside every old pool.
Wave191 gives

```text
p3+u<=delta+Z,
2p2<=u+3h.                                       (2)
```

## 2. Strict residual capacity

After an exact-two type-three raw, the Wave190 residual crosses the same
label but omits coordinates of the unique Wave181 checkerboard through that
label.  The residual therefore cannot be exact-two: uniqueness would force
it to equal a circuit not contained in its support.

Close new exact-three residual circuits under companionship.  If the new
pool has `y` exact-one circuits and `g` exact-three pairs, then

```text
Y=y+2g,
Z<=y+3g,
2Z<=3Y.                                          (3)
```

There is no exact-two new residual type.

The Wave191 residual penalty admits the strengthened decomposition

```text
delta/2+h/2+Y

 >=(2delta+3Y)/6
  +(2delta+6h+3Y)/12
  +Y/4

 >=p2/3+p3/2+Y/4.                                (4)
```

Equality in Wave191 therefore forces `Y=0`.  Equations (2)--(4), old-pool
collision exclusion, and the local exact-three-raw exclusion then give

```text
Z=h=u=0,
t=r1=p3=m,
delta=m,
r=2079.                                          (5)
```

Combining (1) and (5), the complete equality face is

```text
n1=C-2m, n2=p2=0, n3=p3=m,
r=2079, r1=t=delta=m,
h=u=Y=Z=0,
0<=m<=2079.                                      (6)
```

Every type-three raw is exact-one.

## 3. Canonical `tau`-pair saturation

The remaining

```text
r-r1=2079-m
```

raw circuits are exact-two.  The number of type-one raw assignments is

```text
n1=C-2m=2(2079-m).
```

They saturate the exact-two circuits with two distinct labels each.
Wave181's canonical nonedge involution `tau` identifies the two labels of
each exact-two checkerboard.  Hence the type-one label set is a union of
exactly `2079-m` complete `tau`-pairs.  No equality-face exact-two circuit
crosses a label outside that set.

## 4. The `m=0` affine-axis contradiction

When `m=0`, every nonedge `e` owns one selected exact-one circuit `C_e`,
and every canonical quadrilateral supplies the raw exact-two checkerboard
`R_e`.

Apply the verified type-one majority translation to `C_e`.  It produces a
short true relation `W_e` on two proper endpoint-star subsets.  Equality
and Wave181 uniqueness make `R_e` the only possible raw circuit inside it.

If `R_e` were a proper subcircuit of `W_e`, subtracting a scalar multiple
of its relation would leave a nonzero relation on the same proper star
subsets.  A circuit in that difference would cross `e`, omit a coordinate
of `R_e`, and lie in a translated support that already omits a coordinate
of `C_e`.  It would therefore be neither known circuit through `e`.
Consequently

```text
W_e=R_e projectively.                             (7)
```

Normalize

```text
R_e=(1,2,0,0,0,0,0 | 2,1,0,0,0,0,0).
```

The two nonzero translations along the endpoint used in (7) both have
profile `6+2` and weight eight.  They omit opposite canonical coordinates,
so their supports are incomparable and neither contains `R_e`.  One is
`C_e`; the other contains a cross circuit but contains neither `C_e` nor
`R_e`.  This circuit is new, contradicting `Q=6237`.

Thus

```text
m=0 is impossible.                               (8)
```

## 5. Every `m>0` branch has a forbidden nonprivate leaf word

For `m>0`, a selected type-three circuit exists.  Equality `p3=n3=m` and
minimality force exactly one private label on each selected type-three
circuit.  Its other two leaf incidences are nonprivate.  Globally there are
exactly `m` nonprivate labels, each of selected degree two.

Choose a nonprivate leaf label `f` and form its weight-nine `3+6` leaf
relation.  Both endpoint-star sides are proper, so it contains a circuit
crossing `f`.

Wave191's local exact-three exclusion does not use privacy; hence the
contained circuit has exact multiplicity at most two.  It cannot be:

- an equality-face exact-one circuit, because every such circuit's sole
  label is private; or
- an equality-face exact-two circuit, because all of those checkerboards
  have both labels in the `tau`-invariant type-one set.

It is therefore new, again contradicting `Q=6237`.  Thus

```text
m>0 is impossible.                               (9)
```

Equations (8)--(9) exclude the entire equality face.  Since `Q` is an
integer,

```text
Q>=6238.
```

Adding the 693 verified edge-isolated projective circuits gives at least
6,931 projective short circuits and 13,862 scalar circuit words.  Wave188's
verified 18,018 all-short-word bound remains numerically stronger because
it includes nonminimal words.

## Reproducibility and boundary

```text
independent math replay:  PASS
independent full replay:  PASS
independent tests:        7/7 PASS
source replay:            PASS
source tests:             6/6 PASS
all frozen hashes:        PASS
```

No graph, cover, code, SAT, LP, configuration, enumeration, or isomorphism
search was used.  No graph or code is constructed; rank 11, endpoint
existence, strict original `n3` improvement, external novelty, and
Conway-99 remain `UNKNOWN`.
