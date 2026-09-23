# Wave 203 proof B: two-center nonedge incidence geometry

```yaml
role: proof_b
date_utc: 2026-07-29T07:20:00Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Structurally independent two-center analysis of one nonedge: define
  the partial third-block maps between the five opposite star triangles,
  prove matched reverse flags are impossible through the canonical
  four-column Gram, derive combined directional flag capacity five and
  epsilon>=5 per both-oriented selected label, and delimit what does not
  follow for low multiplicities or endpoint existence.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave196-four-fiber-hilton-milner-verifier/package-manifest.sha256: eb833bf4ad503fb2243882704492f6bf836525f4b619de8a1979ffc6f0f785c9
  verification/wave198-orientation-lift-verifier/package-manifest.sha256: 9d76bf2a0f5fa1ec2d3d532446c7bd249fd780e96c47de159244ceda790d7432
method: >-
  Two-center star-block incidence, the verified exact-three 6-cycle
  leaf-type rule, canonical c4 relation addition over F_3, and the
  verified four-column quadrilateral Gram. No graph, code, cover, SAT,
  LP, configuration, enumeration, isomorphism, or brute-force search.
command: >-
  python -B attempts/wave203-two-center-incidence-proof-b/exact_check.py
  --verify
  attempts/wave203-two-center-incidence-proof-b/exact-results.json;
  python -B -m unittest -v
  attempts/wave203-two-center-incidence-proof-b/test_exact_check.py
outputs:
  - agents/2026-07-29-wave203-two-center-incidence-proof-b.md
  - attempts/wave203-two-center-incidence-proof-b/
limitations:
  - This proof-B lane was completed without opening any Wave202 proof-A
    equality-face note or package.
  - It is conditional on the frozen prism-free rank-11 endpoint.
  - The third-block map is only a partial injection; existence on all
    five candidate triangles is not proved.
  - Low multiplicities force orientation-certificate loss but no extra
    circuit, private label, or local fiber repetition by themselves.
  - No endpoint contradiction, strict original n3 improvement, novelty
    claim, or Conway-99 resolution follows.
```

## Verdict

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

For every graph nonedge `e={x,y}`, the complete exact-three flag pool
satisfies the strengthened two-center capacity

```text
m_(x->y)+m_(y->x)<=5.                            (1)
```

Thus the natural five-to-five third-block correspondence is not a
bijection of all candidate triangles. It is an injective partial map,
and a flag on a matched reverse block is impossible.

## 1. The two five-element candidate sets and shared slots

Let `a,b` be the two common neighbors of the nonedge `xy`. In the seven
triangle blocks through `x`, they lie in two distinct blocks

```text
X_a, X_b.
```

They are distinct because otherwise `a,b` would be adjacent and their
edge would have both `x,y` as common neighbors. The other five `x`-star
triangles are anticomplete to `y`: `mu=2` says `a,b` are all neighbors
of `y` inside `N(x)`. Denote this five-set by `C_x(y)`.

Symmetrically, the blocks through `y` containing `a,b` are `Y_a,Y_b`,
and the remaining five form `C_y(x)`, each anticomplete to `x`.

The common option set for the capacity argument is `C_x(y)`. A forward
`x->y` flag is assigned its third block `S in C_x(y)`. A reverse
`y->x` flag is assigned its leaf block, also an element `S in C_x(y)`.
This is a genuine five-slot identification: the identity bijection on
`C_x(y)`. It does not assert that a flag exists in every slot.

Every flag centered at `x` containing the oriented label `x->y` has leaf
triangle `T in C_y(x)`. Its exact-three set contains the two-block type
of `y`,

```text
A_x(T)={X_a,X_b,S}
```

for a unique third block `S in C_x(y)`. Define

```text
phi_xy(T)=S.                                      (2)
```

The verified fixed-center map `T -> A_x(T)` is injective. Since
`X_a,X_b` are fixed, (2) is injective on its domain. It is therefore a
bijection only from the existing `x->y` flags to their image, not from
all five candidates to all five candidates.

## 2. What a matched reverse flag would have to be

Write `T={y,u,v}`. The verified leaf-type 6-cycle for

```text
A_x(T)={X_a,X_b,S}
```

assigns type `X_aX_b` to `y` and types `X_aS`, `X_bS` to `u,v` in some
order. Hence the two noncenter vertices of `S` meet `u,v`, one each:

```text
j(S,T)=2.                                        (3)
```

Suppose a reverse flag centered at `y` has leaf triangle exactly `S`.
The leaf `x` has type `{Y_a,Y_b}`, so both blocks belong to `A_y(S)`.
Equation (3) says `T also belongs to A_y(S)`. Since an exact-three set
has size three,

```text
A_y(S)={Y_a,Y_b,T}.                              (4)
```

Thus if the reverse flag existed on the matched block, its third
`y`-star block would indeed be `T`; the two partial maps would be inverse
on that pair. This proves the involution statement on every matched pair
where both directional flags are assumed to exist.

## 3. The matched reverse is impossible

The canonical weight-four relations of the two flags would be

```text
z_T+2(z_Xa+z_Xb+z_S)=0,
z_S+2(z_Ya+z_Yb+z_T)=0.                         (5)
```

Both formulas use the same globally frozen triangle columns `z_R`.
Wave180 fixes the displayed relation normalization by setting the leaf
column coefficient to one. There is no flag-dependent rescaling of an
individual column; only an entire relation may be scaled, and the
canonical normalization in (5) has fixed that scalar.

Adding the two canonically normalized relations in (5) over `F_3`
cancels `z_T,z_S` and forces

```text
z_Xa+z_Xb+z_Ya+z_Yb=0.                          (6)
```

The four columns in (6) are pairwise distinct. On the `x` side,
`X_a!=X_b` because `a,b` lie in distinct local matching blocks; likewise
`Y_a!=Y_b`. No `x`-side block can equal a `y`-side block, because a
common graph-triangle block would contain both nonadjacent vertices
`x,y`.

They are exactly the canonical quadrilateral blocks of the nonedge `xy`.
Their verified Gram, with the same frozen column normalization and up to
simultaneous permutation, is

```text
[0 1 1 2
 1 0 2 1
 1 2 0 1
 2 1 1 0].
```

Every row sums to `1 mod 3`, so the all-equal vector in (6) is not in
the kernel. The actual projective kernel is checkerboard, not all equal.
Therefore (6) is impossible.

Consequently

```text
phi_xy(domain of x->y flags)
  is disjoint from
domain of y->x flags,                            (7)
```

when both are regarded as subsets of the same five-slot set `C_x(y)`.
Forward flags occupy distinct slots by injectivity. Reverse flags occupy
distinct leaf blocks automatically. The identity matching on the five
slots is a bijection, and matched forward/reverse occupancy is forbidden
by (6). Therefore the two occupied slot sets are disjoint and their
cardinalities sum to at most five, proving (1).

## 4. Selected-incidence and orientation-loss consequences

For an unordered selected nonprivate label `e`, let `s_e` be its total
selected flag multiplicity across both orientations. Equation (1) gives

```text
s_e<=5.                                          (8)
```

Private selected type-three labels have `s_e=1`. If `U` is the unordered
selected label union, summing (8) gives the strengthened row

```text
3n3+4p3<=5|U|.                                   (9)
```

This has the same displayed `S5` consequence as the earlier oriented
capacity after coupling `|U|+a3+b3<=J<=3564`, but it records strictly
more local information.

Let `b` be the number of nonprivate selected labels whose two
orientations are both occupied. With the Wave198 notation

```text
epsilon=sum_over_occupied_orientations(5-m),
```

a both-oriented label contributes

```text
10-s_e>=5.
```

Therefore

```text
epsilon>=5b.                                     (10)
```

In particular, the low-multiplicity patterns contribute

```text
(1,1): 8,   (1,2): 7,   (2,2): 6
```

units to `epsilon`. These are unavoidable two-center certificate losses.

## 5. Boundary of the theorem

Equation (10) does not by itself produce a new circuit, private label, or
local four-fiber repetition. For multiplicities one and two, the
Wave201 one-center charge `m-2` is nonpositive or zero. The present gain
comes instead from the five shared third-block slots and the forbidden
matched pair.

Likewise, a pair type of degree five says only that all five simple
three-sets containing that pair occur; it does not say all five leaf
occurrences equal one distinguished endpoint. No such saturation
overreach is used.

```text
five candidate blocks per side:            DERIVED
third-block map:                            partial injection
matched reverse third block:                forced to be T
matched reverse flag:                       REFUTED
combined two-orientation capacity <=5:      DERIVED
epsilon>=5 per both-oriented label:         DERIVED
extra circuit/private/fiber loss at m<=2:   not proved
endpoint contradiction:                    no
Conway-99 / external novelty:               UNKNOWN
```
