# Wave 191 adversarial memo: exact-three residual stability

```yaml
role: verifier
date_utc: 2026-07-29T02:50:57Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: REFUTED
scope: >-
  Adversarial reconstruction of the full equality face of the verified
  conditional Wave190 bound Q>=5544, followed by an independent support and
  collision audit of exact-three private-leaf translations. The putative
  Q=5544 orbit-closed geometry is excluded. A stronger candidate coefficient
  consequence Q>=5891 is derived.
inputs:
  verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256: fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4
  verification/wave190-residual-stability-verifier/package-manifest.sha256: 15686d17472fd60122072b3d679980d90d3cfe12fd87e5359344e52e216f1280
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave186-star-translation-cover-verifier/package-manifest.sha256: edb833cbed8706f164199d4ecab8ff26757c54dfc46915819e150e17d73fef76
method: >-
  Equality-slack reconstruction, exact-two uniqueness, canonical exact-three
  center and support analysis, relation subtraction over F_3, and a
  label-level raw-plus-residual capacity certificate. No discovery code,
  graph, code, SAT, LP, configuration, isomorphism, or enumeration search.
command: None.
outputs:
  - verification/2026-07-29-wave191-exact-three-residual-verifier-memo.md
limitations:
  - The argument is conditional on the frozen prism-free rank-11 endpoint.
  - This standalone memo is not a sealed clean-room verification package.
  - The stronger Q>=5891 coefficient bound should remain CANDIDATE until
    separately frozen and independently promoted.
  - No graph or code is constructed, and rank 11, the endpoint, external
    novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`REFUTED_WITH_SCOPE`.

The scalar row displayed in Wave190 is not the complete equality face.
After reconstructing every equality slack, however, exact-two uniqueness
eliminates the apparent type-two branch.  Every remaining `Q=5544` branch
would pack all private type-three leaf translations into exact-three
companion orbits.

That packing cannot be sharp.  A private-leaf relation whose raw circuit is
exact-three always forces a further cross circuit outside the raw orbit.
Keeping the unused old-pool capacity rather than assuming distinctness gives
the stronger candidate consequence

```text
Q>=5891.
```

In particular, no orbit-closed translation geometry can realize `Q=5544`.

## 1. Full equality conditions from Wave190

Use the frozen notation

```text
C=4158,
A=n_1+2p_2+p_3,
B=n_1+n_2+2n_3,
delta=2r+3h-A,
```

where `r` counts low raw-pool circuits, `h` counts complete exact-three
companion pairs in the orbit-closed raw pool, and `Y` counts residual
circuits outside every old pool.  Wave190 proves

```text
Q>=B+A/2+delta/2+h/2+Y
 >=B+A/2+p_3/6,

6Q>=4I+n_1+2(p_2-n_2)>=8C,

I=2n_1+2n_2+3n_3+p_2+p_3>=2C.
```

Assume `Q=4C/3=5544`.  Equality in the coefficient row first gives only

```text
I=2C,  n_1=0,  p_2=n_2.                         (1)
```

It does not by itself force `n_2=0` or `p_3=3n_3`.

Equality in the intermediate residual estimate is more restrictive.  Its
two steps are

```text
delta+3h+3Y>=p_3,
3delta+3h+6Y>=delta+3h+3Y.
```

Both must be equalities.  Hence

```text
delta=Y=0,  p_3=3h.                              (2)
```

The five-slack identity in the Wave190 verifier then gives

```text
r_1=0,
a_H=q_H,
k=b_H=p_3-q_H,
a_H+b_H=3h.                                     (3)
```

Since `delta=0`, raw-assignment capacity is saturated:

```text
A=2r+3h.
```

Equations (1)--(2) give `A=2n_2+3h`, so

```text
r=n_2.                                           (4)
```

Every one of the `r` low circuits is therefore exact-two and receives both
of its possible raw label assignments.  Every exact-three orbit receives
three raw assignments, one for each of its three distinct labels.

Moreover, (3) forces all assignments received by exact-three orbits to be
type-three.  Indeed, global capacity saturation makes `a_H=3h`; then

```text
a_H=q_H=p_3=3h,  k=b_H=0.                        (5)
```

Consequently all `2p_2=2n_2` type-two assignments would have to fill the
`r=n_2` exact-two circuits.

This is impossible when `n_2>0`.  Each private type-two label produces two
distinct raw circuits.  If both are exact-two, both cross that same label.
Wave181 identifies at most one projective exact-two circuit through a fixed
nonedge: its canonical checkerboard conic.  Thus

```text
n_2=p_2=r=0.                                     (6)
```

The genuine scalar equality face is therefore

```text
1386<=n_3<=2079,
h=2772-n_3,
p_3=3h=8316-3n_3,
delta=r=r_1=Y=0.                                 (7)
```

Every selected label has selected degree one or two.  There are exactly
`p_3` degree-one labels, and the `h` raw exact-three orbit label sets
partition those private labels into triples.  Each orbit receives exactly
one type-three leaf assignment for each of its three labels.

The often displayed row

```text
n_3=h=1386,  p_3=4158
```

is only the endpoint of (7).  In that endpoint all selected triple label
sets partition the nonedges.  It is not the unique scalar equality row.

## 2. Exact center of an exact-three leaf extraction

Fix a selected exact-three flag

```text
F=(x,T),  T={y,u,v},
```

and its private label `e=xy`.  Let `A_x` be the three `x`-star blocks in
the source weight-four conic.  The private-leaf relation is

```text
w_e=c_4+2s_y.
```

It has coefficient two on every occupied coordinate and support

```text
supp(w_e)=A_x union (S_y minus {T}),
```

with profile `3+6`.

Let the extracted raw circuit `D` have exact cross-multiplicity three.
Its common center is either `x` or `y`.

### Owner-center case is impossible

If `D` is centered at `x`, its center-star part must fit in the three
available `A_x` blocks.  Hence it can only be the weight-four member

```text
D=z_S+2*sum_(R in A_x) z_R
```

for some outer `y`-star block `S`.  Subtracting `D` from `w_e` cancels all
three `x`-star coordinates and leaves a nonzero relation supported on six
blocks of the `y`-star.  This contradicts the verified fact that every
proper star subset is independent.

Therefore the raw exact-three circuit is centered at the leaf:

```text
center(D)=y.                                     (8)
```

### Exactly one companion member is contained

Write its canonical orbit as

```text
c_4'=z_S+2*sum_(R in A_y) z_R,
c_5'=z_S+  sum_(R in B_y) z_R,
A_y disjoint_union B_y=S_y.
```

The leaf block `S` is one of the three blocks in `A_x`.  Since `w_e` omits
`T`, containment of `c_4'` requires `T in B_y`, while containment of
`c_5'` requires `T in A_y`.  Exactly one alternative holds.  Thus one and
only one member of the target orbit can be the raw extraction.

In the more explicit flag geometry, `S` is the unique `x`-star triangle
whose two noncenter vertices supply the common-neighbor incidences for the
two leaves in `T minus {y}`.  It is anticomplete to `y`.  The transition

```text
(x,T; y) -> (y,S; x)
```

is involutive on the labeled flag incidence: applying the same construction
at the label `xy` returns `(x,T)`.  This supplies a necessary transition
geometry, not an existence construction.

## 3. The missing exact-three residual

The contained member always forces a further relation.

If `T in A_y`, the raw member is `c_5'` and

```text
w_e-2c_5'
```

has profile `2+2` and weight four: its support consists of the two blocks
in `A_x minus {S}` and the two blocks in `A_y minus {T}`.

If `T in B_y`, the raw member is `c_4'` and

```text
w_e-c_4'
```

has profile `3+3` and weight six: its support consists of all three
`A_x` blocks and the three blocks in `B_y minus {T}`.

Both are nonzero true relations.  Each side is a proper subset of its
seven-star, so any support-minimal circuit in the relation meets both
stars and cross-realizes `e`.  It is not:

- the raw circuit, because raw coordinates were cancelled;
- its companion, because the companion contains the omitted block `T`;
- the selected owner or its selected companion, because both contain `T`;
- any other selected circuit, by privacy of `e`.

Thus every type-three raw assignment that is not exact-one forces a
residual assignment, including when the raw circuit is exact-three.  This
is precisely the case not charged by Wave190.

For the equality face (7), every raw assignment is exact-three, every old
exact-three orbit already uses each of its three labels once, and there is
no low pool or `Y` pool.  The residual through any private label is
therefore a new short circuit.  This directly contradicts equality in the
disjoint-pool count and already proves

```text
Q>=5545.                                         (9)
```

## 4. Collision-safe global strengthening

The same argument gives more than a one-unit equality exclusion without
assuming residual circuits are all new.

Let `r_1` be the exact-one circuits among the `r` low raw circuits.  The
raw capacity row gives

```text
r_1<=delta.
```

At least `p_3-r_1` type-three raw assignments are not exact-one, so they
force residual assignments.  Exact-one raw circuits cannot absorb a
residual.  Across the remaining old raw pool:

- an exact-two circuit has two labels total;
- one exact-three companion pair has three labels total;
- raw and residual use of the same circuit-label pair is impossible; and
- for an exact-three orbit, raw and residual use are mutually exclusive
  label by label.

After the raw assignments are placed, the number of still unused combined
label slots in the exact-two and exact-three old pool is exactly

```text
delta-r_1.
```

If `Y` counts genuinely new residual circuits, capacity three therefore
gives

```text
3Y
 >=(p_3-r_1)-(delta-r_1)
 =p_3-delta,

delta+3Y>=p_3.                                   (10)
```

There is a second independent capacity row.  A private type-two label has
two distinct raw circuits.  They cannot both be exact-two, by Wave181
uniqueness.  Hence at least one is exact-one or exact-three.  An exact-one
circuit can be charged by only one label, and an exact-three orbit by at
most its three labels.  Therefore

```text
p_2<=r_1+3h<=delta+3h.                           (11)
```

The disjoint raw-pool bound is

```text
Q>=B+A/2+delta/2+h/2+Y.
```

Adding (11) to twice (10) gives

```text
3delta+3h+6Y>=p_2+2p_3,
```

and hence

```text
Q>=B+A/2+p_2/6+p_3/3.                            (12)
```

Multiplying by 24 and expanding yields the exact identity

```text
24Q
 >=36n_1+24n_2+48n_3+28p_2+20p_3

 =17I
  +2n_1
  +10(p_2-n_2)
  +p_2
  +3(p_3-n_3).
```

All remainder terms are nonnegative, while `I>=2C`.  Thus

```text
24Q>=34C,
Q>=ceil(17C/12)=5891.                            (13)
```

Adding the 693 verified edge-isolated projective circuits would give at
least

```text
6584
```

projective short-circuit classes, hence at least

```text
13168
```

scalar short-circuit words.  Wave188's verified `18018` bound for all short
dual words remains numerically stronger because it also counts nonminimal
words.

## 5. Boundary

The Wave190 equality geometry is refuted, not constructed.  The argument is
analytic and uses only star-simplex independence, the Wave180 exact-three
classification, the Wave181 exact-two uniqueness, private-label ownership,
and label-level capacity.

The new coefficient row (13) is recorded as a candidate consequence in this
standalone memo.  It does not exclude rank 11, improve the original graph
parameter `n3`, construct the graph or code, or resolve Conway-99.
