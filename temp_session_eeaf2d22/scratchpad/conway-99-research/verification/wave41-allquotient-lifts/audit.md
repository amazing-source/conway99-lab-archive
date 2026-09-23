# Wave 41 all-quotient lift clean-room audit

Date: 2026-07-27 UTC

Verdict: **PASS / `VERIFIED_SCOPED_CONDITIONAL`** for the theorem

```text
n3=4158, r3=12, and every edge type 2+2+2
  ==> every base-triangle K39 block has rank_F7 at least 33
  ==> r7>=33
  ==> parity sharpens this branch to even r7>=34.
```

The endpoint, the all-`222` hypothesis, the rank-twelve hypothesis, a
99-vertex graph, endpoint exclusion, and an upper bound below `4158` remain
unproved or `UNKNOWN`.

## Clean-room boundary

The verifier reconstructed the claim from the frozen Wave 36 modular parity,
Wave 38 centered quotient bridge, and Wave 40 edge-coupling artifacts.  It
did not read or import
`attempts/wave41-allquotient-lifts/exact_check.py` or the Wave 41 discovery
report.

The independent checker and tests were frozen at

```text
5d9c2c01ebe0e134b366a526615b1870647f507f43f68e4cb7145ec5e9ea0261
4d94289aaff949d29c858a1b529b266c40b5821bb88a26f4b2dc1ba4b5d74a61
```

before the final discovery JSON was opened.  The final discovery artifact
first matched its supplied SHA-256
`da8098c5048c9b45ca3625131a98eb5473d29f864ea0c78a3e26d3b091b38e6d`.

## 1. Complete normalization

There are fifteen perfect matchings on six points.  The 48-element
stabilizer of a fixed matching has exactly three orbits on them:

```text
relative type 111: 1
relative type 12:  6
relative type 3:   8
```

Fixing the `01` relation as `3C4`, choosing one representative for the
relative pairing at fibre 1, and then specifying the final side by two
arbitrary pairings and a three-block bijection gives

```text
3 * 15 * 15 * 6 = 4050
```

complete normalized representatives.  No graph automorphism or transitivity
of a completed graph is assumed.

Exact elimination of `2I+A_Q=P_T-I` over `F_3` gives

```text
11:8, 12:1, 13:400, 14:46, 15:2616, 16:979.
```

The eight rank-eleven records are eight distinct labelled quotient graphs.

## 2. Strict fibre-coloured isomorphism

Here “fibre-coloured” means that each of the three named six-vertex fibres is
preserved setwise; the verifier does not permute the fibre colours.

Every normalized graph has the same fixed `01` relation.  Its
colour-preserving automorphism group has order

```text
3! * 2^3 * 2^3 = 384.
```

For each of the other seven rank-eleven quotients, the checker exhausts
these possible maps on fibres 0 and 1.  Equal-signature twins in fibre 2 are
handled by an exact bijection backtrack.  Emitted vertex permutations verify
the entire adjacency relation.  All eight quotients form one strict
fibre-coloured isomorphism class.

An early pre-freeze implementation incorrectly required the fibre-2
neighbourhood signature to be unique.  A hostile run exposed twins, and the
shortcut was replaced by the complete bijection search before the
implementation hashes were frozen.  No discovery artifact was consulted
during that correction.

## 3. Complete affine 18-bit lift space

At each quotient vertex the two half-edges toward either other fibre must
use the two endpoints of the contracted pair bijectively.  There are four
raw local choices.  A simultaneous swap of the two endpoints is a gauge
symmetry, leaving one relative bit.  Independently at all eighteen quotient
vertices, this gives exactly

```text
2^18 = 262144
```

relative endpoint-pairing masks.

For every quotient triangle, the lifted edges meet the same endpoint
precisely at one affine pattern of its three local bits.  The canonical
rank-eleven quotient has sixteen quotient triangles.  Rejecting all sixteen
patterns leaves exactly

```text
37378
```

triangle-free masks.

For each fibre-coloured quotient isomorphism, the verifier derives rather
than assumes:

1. the endpoint swap at every contracted pair;
2. the permutation of the eighteen mask variables; and
3. the affine XOR constant.

All 72 directed quotient half-edges satisfy the derived transport equations.
All `2^18` masks are then checked for preservation of triangle status for
each of the eight quotients, and rank witnesses are checked at the lifted
36-vertex graph level.  Hence each quotient has exactly 37,378
triangle-free lifts.

## 4. Exact F7 ranks and the 39-block identity

Exact sparse symmetric elimination over `F_7`, with independent dense
controls, gives the canonical cubic-core distribution

```text
rank_F7(3I-A_core): 32:264, 33:7348, 34:29766.
```

For the transported principal block,

```text
rank_F7(K39)=1+rank_F7(3I-A_core).
```

The identity follows by eliminating the invertible `I-J_3` base block.  The
Schur complement kills the fibre-indicator space and is
`2(3I-A_core)` on its 33-dimensional fibre-sum kernel; the quotient action
of `3I-A_core` has rank two.  Dense checks on canonical witnesses and
periodic masks accompany the algebra.

Therefore every one of the eight quotients has

```text
rank_F7(K39): 33:264, 34:7348, 35:29766.
```

## 5. Conditional theorem

Wave 38 verified only the one-way local ceiling

```text
rank_F3(P_T-I) <= rank_F3(C+J)=r3-1.
```

Under `r3=12`, every actual all-`222` base triangle therefore has quotient
rank at most eleven.  The complete normalization has minimum rank eleven,
so the quotient must be one of the eight forms just verified.  The actual
neighbor core is a triangle-free lift, and its `K39` rank is at least 33.

The block is principal in `K=N M N^T`, while the verified rank transfer gives
`rank_F7(K)=rank_F7(M)=r7`.  Thus `r7>=33`.  The independently verified
endpoint index condition says `r3+r7` is even.  With `r3=12`, `r7` is even,
so this branch has

```text
r7>=34.
```

This is conditional branch elimination of `r7<=32`, not endpoint exclusion.

## 6. Hostile compact-kernel roadblock

The rank-33 witness has nullity six.  Three independent kernel vectors are
structural: for each fibre, put `(4,1,1)` on the base triangle with `4` at
the corresponding base vertex, put `1` on the entire twelve-point fibre,
and put zero on the other two fibres.

Every legal outside column is nonadjacent to the three base vertices and has
two neighbors in each twelve-point fibre.  Its dot product with the matching
structural vector is

```text
(4+1+1)+(10-2)=14=0 mod 7.
```

The checker tests all `3*C(12,2)=198` fibre components.  Thus the projection
of the outside border on the six-dimensional local kernel has rank at most
three.  The arbitrary-border lemma cannot promote the local rank 33 to 45
by claiming a full six-dimensional projection.  This veto does not weaken
the verified local rank-33 floor.

## 7. Discovery comparison and scope

Every mathematical field needed for the theorem matches the frozen
discovery JSON: normalized counts, rank distribution, the set of eight
quotient hashes, the strict coloured class count, per-case triangle-free
counts, per-case rank distributions, the minimum witness, theorem floor, and
compact-kernel roadblock.

The only representation difference is the ordering of the same 54 undirected
witness edges.  The verifier sorts them lexicographically; discovery retains
set iteration order.  Their edge sets, mask `51739`, and ranks are identical.

Discovery additionally reports lift-count censuses for quotient ranks 12
through 16.  Those fields are not needed for the candidate theorem and were
not independently verified here.

Final status:

```text
conditional all-222, r3=12 floor r7>=34: VERIFIED SCOPED
n3=4158:                                UNKNOWN
all edges type 222:                      ASSUMPTION NOT PROVED
r3=12:                                   ASSUMPTION NOT PROVED
endpoint exclusion / bound below 4158:   NOT PROVED
graph or counterexample:                 NONE
novelty and priority:                    UNKNOWN
```
