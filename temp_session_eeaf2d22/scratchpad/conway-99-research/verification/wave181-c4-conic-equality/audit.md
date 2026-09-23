# Independent audit

## Verdict

`VERIFIED_WITH_SCOPE`.

## Shared-center exclusion

For exact multiplicity two with labels `{x,y},{x,z}`, the unique support
block avoiding `x` is `T={y,z,t}`; all other blocks lie in the `x`-star, so
the circuit relation puts `z_T` in `E_x`.

If `x~t`, the star block on `xt` intersects `T` and has pairing one.
Wave 171's verified rule for every disjoint outer block is
`D(T,S)=j(T,S) mod 3`, not `j-1`.  Thus the edge `xt` is a baseline cross
edge for all six outer blocks.

Besides `t`, the nonedges `xy,xz` have distinct extra common neighbors
`a,b`.  If their outer star blocks coincided, that disjoint block and `T`
would have the three cross edges `xt,ay,bz`, forbidden by `P=0`.  Therefore
two outer blocks have pairing two and four retain pairing one.  Including
the intersecting block gives five ones and two twos.  All seven squares are
one in `F_3`, contradicting

```text
<z_T,P_x z_T>=-sum h_i^2=0.
```

If `x` is nonadjacent to `t`, it is anticomplete to `T`; Wave 180 then
forces the conic/complement pair, both of which also realize `{x,t}`.
Exact multiplicity two is again impossible.

## Canonical quadrilateral and conic

Multiplicity two therefore has disjoint nonedge labels `X,Y`.  The four
cross edges show that `Y` is the two-element common-neighbor set of `X`;
symmetrically `X` is the common-neighbor set of `Y`.  This is a
fixed-point-free involution on 4,158 nonedges, giving 2,079 induced
quadrilaterals.

Adjacent edge-triangle blocks intersect and pair to one.  Opposite blocks
are disjoint and already have two square cross edges; `P=0` forbids a
third, so their pairing is two.  The resulting Gram is

```text
[0 1 1 2
 1 0 2 1
 1 2 0 1
 2 1 1 0].
```

It has rank three and projective kernel `(1,2,2,1)`.  For an already
existing four-column circuit, its true relation must be this checkerboard
word.  Switching by the coefficients gives `2(J_4-I_4)`, so the four
singular points form the complete conic `Q(2,3)`.  The Gram-kernel word is
not promoted for a square not already known dependent.

## Equality face

Let `N,a` be Wave 180's minimal-cover counts.  If the total number of
nonedge-realizing projective circuits is `Q=2079`, then

```text
4158<=2N+a,
N+a<=Q=2079.
```

These force `a=0`, `N=2079`, and equality everywhere.  Every selected
support realizes exactly two disjoint labels, the label sets partition all
nonedges, and the cover contains all `Q` circuits.  Hence all 2,079
canonical quadrilaterals—and no other nonedge-realizing short supports—are
checkerboard conics.

## Signed incidence identity

Each graph edge lies in 12 induced quadrilaterals.  A triangle block has
three edges, and an induced square cannot contain two of them, so every
column occurs 36 times.

Two intersecting blocks occur in four squares as adjacent boundary edges;
checkerboard products contribute `-4`.  Two disjoint blocks occur together
oppositely exactly once when they have two cross edges, contributing `+1`.
Therefore, over the integers and then over `F_3`,

```text
R^T R=36I-4K+L,
R^T R=2K+L mod 3.
```

Under equality every row is a true relation, so `rank_F3(R)<=220`.  No
lower bound 221 is proved.

Switching conic columns does not change pure squares.  Since every block
occurs 36 times,

```text
sum_C Q_C=36*sum_T z_T tensor z_T=0 in F_3.
```

The first projector sum is therefore a null boundary, not a contradiction.

## Integrity

- all eight frozen inputs and nine discovery entries matched;
- discovery replay and seven tests passed;
- an independent checker reproduced the baseline profile, C4 kernel,
  equality arithmetic, signed coefficients, and projector null;
- all seven independent tests and eight verification entries passed.

Rank 11, equality, the endpoint, and Conway-99 remain `UNKNOWN`.

