# Wave 191 verifier addendum: canonical residual and closed-new capacity

```yaml
role: verifier
date_utc: 2026-07-29T02:56:49Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: CANDIDATE
scope: >-
  Independent audit of two proposed refinements to the Wave191 residual
  route: the exact local position of the omitted owner triangle in a
  leaf-centered exact-three raw orbit, and orbit closure of genuinely new
  residual circuits. The first refinement yields a contradiction stronger
  than the proposed residual; the second yields the candidate bound Q>=6048.
inputs:
  verification/2026-07-29-wave191-exact-three-residual-verifier-memo.md: 0f175720ba6ac4c461b52bd11c132b447add5e22e223274e8dfaf3a7a612eaa9
  verification/wave189-degree7-star-orbit-verifier/package-manifest.sha256: fc17484bd8c32a5886ecdcc65d153903cef5f3b60a3de1c9905ed96697c273c4
  verification/wave190-residual-stability-verifier/package-manifest.sha256: 15686d17472fd60122072b3d679980d90d3cfe12fd87e5359344e52e216f1280
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave186-star-translation-cover-verifier/package-manifest.sha256: edb833cbed8706f164199d4ecab8ff26757c54dfc46915819e150e17d73fef76
method: >-
  Local common-neighbor incidence pairing, exact F_3 relation subtraction,
  canonical quadrilateral Gram-kernel comparison, orbit-closed assignment
  capacity, and an optimized rational coefficient certificate. No discovery
  code, graph, code, SAT, LP, configuration, isomorphism, or enumeration
  search.
command: None.
outputs:
  - verification/2026-07-29-wave191-refinement-verifier-addendum.md
limitations:
  - The argument is conditional on the frozen prism-free rank-11 endpoint.
  - This is an append-only verifier memo, not a sealed two-party package.
  - The new Q>=6048 consequence remains CANDIDATE pending a frozen source
    package and separate clean-room promotion.
  - Rank 11, the endpoint, external novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`CANDIDATE_PASS_WITH_STRENGTHENING`.

Both proposed capacity refinements are sound.  The first local statement is
actually stronger than proposed:

```text
an exact-three raw private-leaf extraction cannot exist.
```

Its purported `2+2` residual has the canonical quadrilateral support, but
the subtraction gives the all-equal coefficient word, whereas the verified
canonical Gram kernel is checkerboard.  Thus the premise is contradictory
rather than a new canonical circuit.

Closing genuinely new exact-three residuals under companionship and using
the stronger type-two uniqueness row improve the numerical candidate bound
from `5891` to

```text
Q>=6048.
```

## 1. The three source `A_x` blocks pair distinct leaf types

Fix a selected exact-three flag

```text
F=(x,T),  T={y,u,v},
```

with `x` anticomplete to `T`.  Each of the three nonedges from `x` to a
leaf has two common neighbors.  Wave180 proves that the resulting six
incidences are six distinct vertices and that the source set `A_x` consists
of three `x`-star blocks, each containing two incidences.

The two incidences in one `x`-star block cannot belong to the same leaf.
Indeed, they would be the two common neighbors of one nonedge, and they are
adjacent because they lie in a graph triangle with `x`.  Their edge would
then have both `x` and that leaf as common neighbors, contradicting
`lambda=1`.

Thus the three `A_x` blocks pair the three leaf types as

```text
yu, yv, uv
```

in some order.  In particular, there is a unique block

```text
S in A_x
```

which contains no common-neighbor incidence for the leaf `y`.

## 2. A leaf-centered target forces `T in A_y`

Consider the private label `e=xy` and its all-two leaf relation

```text
w_e=c_4+2s_y,
supp(w_e)=A_x union (S_y minus {T}).
```

Suppose a raw circuit `D` contained in this support is exact-three and
centered at `y`.  Its unique non-`y` leaf block must be some member of
`A_x`.  Since an exact-three center is anticomplete to its leaf triangle,
that block must be anticomplete to `y`.  The two `A_x` blocks of types `yu`
and `yv` each contain a common neighbor adjacent to `y`; they are therefore
impossible.  Hence the target leaf block is the unique block `S` of type
`uv`.

Write

```text
S={x,a,b},
```

where, after possibly swapping `a,b`, the vertex `a` is adjacent to `u`
and `b` is adjacent to `v`.  Neither is adjacent to another member of `T`,
by the six-distinct-incidences argument.  Since `x` is anticomplete to
`T`, the cross-edge count is exactly

```text
j(S,T)=2.
```

For the target flag `(y,S)`, its set `A_y` is precisely the set of
`y`-star blocks having cross-edge count two with `S`.  Therefore

```text
T in A_y.                                        (1)
```

The target companion pair is

```text
c_4'=z_S+2*sum_(R in A_y) z_R,
c_5'=z_S+  sum_(R in B_y) z_R,
A_y disjoint_union B_y=S_y.
```

Since `w_e` omits `T`, equation (1) excludes `c_4'` from its support and
forces the only possible raw member to be

```text
D=c_5'.                                          (2)
```

There is no orientation alternative.

## 3. The purported residual has an impossible coefficient word

Subtract twice (2) from `w_e`.  The `S` coordinate and all four `B_y`
coordinates cancel.  The remaining relation is

```text
w_e-2c_5',
```

supported on

```text
(A_x minus {S}) union (A_y minus {T}),
```

with two blocks on each endpoint star.  All four surviving coefficients
are equal to two.

This support is exactly the canonical induced-quadrilateral support for the
nonedge `xy`:

- the two blocks in `A_x minus {S}` are the `x`-star blocks through the two
  common neighbors of `x,y`;
- the two blocks in `A_y minus {T}` are the corresponding `y`-star blocks.

The first statement follows because the two remaining source pair-types
are `yu` and `yv`.  For the target flag, `T` is the `uv` pair-type, so the
two remaining `A_y` blocks are the `x u` and `x v` pair-types and contain
the same two common neighbors of `x,y`.

Wave181 independently fixes the projective kernel on these four canonical
blocks as the checkerboard word

```text
(1,2 | 2,1),
```

up to scalar and reordering within the two endpoint sides.  The all-equal
word

```text
(2,2 | 2,2)
```

is not in that one-dimensional kernel.  Hence the true relation
`w_e-2c_5'` cannot exist.

The contradiction arose only from assuming the raw circuit was
exact-three.  Combining this with Wave191's owner-center exclusion proves

```text
every type-three raw leaf extraction has exact multiplicity one or two.
                                                               (3)
```

Thus refinement (1) is correct about `T in A_y` and the `c_5'` support, but
the phrase “the residual is the canonical circuit” is too weak: its support
is canonical while its coefficients are incompatible with the canonical
kernel.

## 4. Closing genuinely new residuals

Retain

```text
A=n_1+2p_2+p_3,
delta=2r+3h-A,
```

and let `r_1` count exact-one circuits in the low raw pool.  Raw capacity
gives

```text
r_1<=delta.
```

By (3), at least `p_3-r_1` type-three raw assignments land on exact-two
circuits and force checkerboard residual assignments as in Wave190.

Exact-one old raw circuits cannot absorb a residual.  The number of unused
combined circuit-label slots in the old exact-two and exact-three raw pools
is

```text
delta-r_1.
```

Therefore at least

```text
(p_3-r_1)-(delta-r_1)=p_3-delta
```

residual assignments land outside every old pool.

Now close every genuinely new exact-three residual circuit under the
Wave180 companion involution.  Write the closed new pool as

```text
y low circuits and g complete exact-three companion pairs,
Y=y+2g total circuits.
```

A low circuit receives assignments for at most two labels, while one
complete exact-three pair receives assignments for at most its common
three-label set.  Hence the new pool has assignment capacity at most

```text
2y+3g<=2(y+2g)=2Y.
```

The added mate cannot collide with an old pool: if one member of its orbit
were old, orbit closure would already place both members there.  Privacy
also excludes the selected and selected-companion pools.  Consequently

```text
delta+2Y>=p_3.                                   (4)
```

This is the proposed closed-new refinement, with `Y` understood as the
number of circuits after exact-three orbit closure.

## 5. Both type-two translates are non-exact-two

Fix a private label of a selected type-two circuit.  Wave186 supplies two
distinct raw translates, and both differ from the selected owner.

Wave181 gives at most one projective exact-two circuit through that fixed
label.  The selected owner is already that unique circuit.  Therefore
neither outside translate can be exact-two.  Each of the `2p_2` type-two
raw assignments must land on:

- an exact-one low circuit, of which there are `r_1`; or
- an exact-three raw orbit, whose three-label set has capacity three.

Thus

```text
2p_2<=r_1+3h<=delta+3h.                          (5)
```

This strengthens the previous row by a factor of two on `p_2`.

## 6. Optimized coefficient certificate

The disjoint pools give

```text
Q
 >=B+A/2+delta/2+h/2+Y,

B=n_1+n_2+2n_3.
```

Multiply (4) by `9/22` and (5) by `1/11`.  Their left-hand sides sum to

```text
delta/2+(3/11)h+(9/11)Y
 <=delta/2+h/2+Y.
```

Therefore

```text
Q>=B+A/2+(2/11)p_2+(9/22)p_3.                   (6)
```

Multiplying by 22 gives

```text
22Q
 >=33n_1+22n_2+44n_3+26p_2+20p_3

 =16I
  +n_1
  +10(p_2-n_2)
  +4(p_3-n_3),

I=2n_1+2n_2+3n_3+p_2+p_3.
```

Every remainder is nonnegative and `I>=2C`, so

```text
22Q>=32C.
```

Since `C=4158=11*378`,

```text
Q>=16C/11=6048.                                  (7)
```

Thus the refinements improve the numerical bound, not merely the equality
description.

Adding the 693 verified edge-isolated projective circuits gives at least

```text
6741
```

projective short-circuit classes and therefore at least

```text
13482
```

scalar short-circuit words.  Wave188's verified `18018` all-short-word
bound remains numerically stronger because it includes nonminimal words.

## 7. Boundary

The exact-three raw branch is locally refuted, and the two new capacity
rows pass this adversarial audit.  Equation (7) is nevertheless retained as
`CANDIDATE` because this append-only memo is not a frozen source plus
independent verifier package.

No rank-11 or endpoint exclusion, graph or code construction, strict
improvement of the original graph parameter `n3`, or Conway-99 resolution
follows.
