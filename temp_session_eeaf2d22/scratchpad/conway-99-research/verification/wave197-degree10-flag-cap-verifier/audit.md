# Independent Wave197 degree-ten audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Conditionally on the frozen prism-free rank-11 endpoint,

```text
Q>=7033.
```

The independent mathematics was frozen before opening either Wave197
source:

```text
SHA-256:
99f66cdb8da57fb79910c14c28fafb2fbd2749f543387515887e0da48a161040
```

The sealed proof-A manifest is
`b15af083fa4f106d56ce918b253ead47edbc9040f65b4dc59d6cc3813d2a1509`.
The hostile proof-B manifest is
`553c1b9699dc1865679d65a8a7d3f8011d7bb59990b0d7c21322a980ce310a05`.
Proof B is a secondary comparison, never a premise.

## 1. Five flags per orientation

Fix a nonedge `{x,y}` and the orientation `x->y`.  The 14 neighbors of
`y` form seven local matching edges, hence seven graph triangles through
`y`.  The two common neighbors of `x,y` lie in two distinct such
triangles.  Those two triangles meet `N(x)`; every vertex in each of the
other five triangles is nonadjacent to `x`.

An exact-three flag centered at `x` and using label `{x,y}` has a leaf
triangle through `y` anticomplete to `x`.  It must therefore be one of
these five triangles.  Thus at most five flags use the orientation
`x->y`; symmetrically at most five use `y->x`.  Every undirected label has
selected-flag degree at most ten.

Equivalently, Wave196 gives `P_x(y)={i,j}`.  A flag containing `x->y`
has `A_x(T)={i,j,k}`, and there are five choices for `k`.  Fixed-center
`A`-injectivity gives the same bound.

## 2. Simplicity and private labels

Wave180 shows that one canonical flag has exactly two companion circuit
supports.  Both realize the same three labels.  An inclusion-minimal
cover cannot select both, because either would be redundant.  Hence the
`n3` selected exact-three circuits give distinct edges in the selected
flag hypergraph.

Let `H` be its number of distinct undirected labels.  The `p3` private
labels have degree exactly one; every other label has degree at most ten.
Summing the three incidences of every selected flag gives

```text
3n3<=p3+10(H-p3),
S10_selected=10H-9p3-3n3>=0.                  (1)
```

Wave196 gives one oriented label for every label in `H`, plus the
distinct `a3+b3` old private orientations outside that union:

```text
J>=H+a3+b3.
```

With `J<=3564=36V`,

```text
S_head=36V-H-a3-b3>=0.                         (2)
```

Adding (1) to ten times (2) produces the source's weighted row

```text
S10=360V-3n3-9p3-10a3-10b3>=0.                (3)
```

This explains a harmless notation difference: the pre-source freeze kept
the selected-degree and headroom slacks separate, while both source
packages combine them as (3).

The other required rows are

```text
SH=3h-a3-b3>=0,
SF=13V-n3-h-g>=0.                              (4)
```

The first is the verified old exact-three pair capacity.  The second is
Wave196's `c_x<=13` summed over 99 centers.

## 3. Exact certificate

With the Wave194 slacks,

```text
SI =I-2C,
S2 =p2-n2,
SE2=2r2-a2-c2,
RA =3h+y+3g-a2-a3-2b3-c2,
SL =n1+2n2+c1+2r2+y+2W-C,
```

exact expansion after the four raw identities gives

```text
Q0-(57C-263V)/30
 =4SI/5+6S2/5+SE2/5+7RA/10+3SL/10
  +S10/90+4SH/45+11SF/30
  +a1/10+3b3/5+c2/5+4g/15+2W/5.               (5)
```

All terms are nonnegative.  At `C=4158,V=99`,

```text
(57C-263V)/30=70323/10.
```

Since `Q` is integral,

```text
Q>=7033.
```

Adding the 693 edge-isolated projective circuits gives 7,726 projective
short circuits, or 15,452 nonzero scalar circuit words.  Wave188's 18,018
all-short-word bound remains numerically stronger because it also counts
nonminimal words.

## 4. Independent integer rounding control

The verifier found the following integer accounting row:

```text
H=33,
a1=7, a2=8, a3=3531,
b1=596,
n2=298, n3=110,
r2=4, h=1177, y=8,
all other split and new-pool variables zero.
```

It gives

```text
n1=3546, p2=298, p3=0, r1=603,
I=8316,
Q0=7033.
```

Every slack in (1)--(5) is zero.  The `7/10` gap above the rational target
is exactly the explicit term `a1/10`.  This independently checks that the
integer rounding is sharp for the displayed linear accounting system.
It is not a graph, cover, code, flag family, or circuit construction.

Proof A and proof B use a different rational null at `70323/10`; it was
independently replayed and is likewise arithmetic only.

## Reproducibility and boundary

```text
independent math replay:       PASS
independent full replay:       PASS
independent tests:             11/11 PASS
primary replay/tests:          PASS / 6 of 6
proof-B replay/tests:          PASS / 6 of 6
all sealed hashes:             PASS
```

No graph, code, cover, SAT, LP, configuration, family, construction,
enumeration, isomorphism, or brute-force search was used.  Rank 11,
endpoint existence, strict original `n3` improvement, external novelty,
and Conway-99 remain `UNKNOWN`.
