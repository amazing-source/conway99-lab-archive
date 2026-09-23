# Wave 195 proof B: fixed-center packet geometry and `Q>=6980`

```yaml
role: proof_b
date_utc: 2026-07-29T03:42:46Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: derive the fixed-center
  oriented-label row SG>=0 for all canonical exact-three flags and combine
  it exactly with the verified Wave194 slack system to prove Q>=6980.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave174-no-weight3-dual/package-manifest.sha256: ac34c8a3b045bec70e3a2080cb4365c0ea43cc732b313ecb3cec355a28f23450
  verification/wave180-capacity3-companion/package-manifest.sha256: 28788edf010292a2c17763a744dfcf1a90a6343c5f72981e82e1aeb5853b7bc5
  verification/wave194-five-thirds-verifier/package-manifest.sha256: 236facbec2539a87e197fd0b2b8ca66bc0d53b12415fdf216acf410064d7ca64
method: >-
  Exact ternary coefficient addition, injection into intersecting
  three-subsets of a seven-block point star, the (7,3) Hilton-Milner
  theorem, oriented private-label incidence, the degree-14 neighbor
  budget, and an exact rational dual certificate. No graph, code, cover,
  SAT, LP, configuration, enumeration, isomorphism, or brute-force search.
command: >-
  python -B attempts/wave195-packet-cohomology-proof-b/exact_check.py
  --verify attempts/wave195-packet-cohomology-proof-b/exact-results.json;
  python -B -m unittest -v
  attempts/wave195-packet-cohomology-proof-b/test_exact_check.py
outputs:
  - agents/2026-07-29-wave195-packet-cohomology-proof-b.md
  - attempts/wave195-packet-cohomology-proof-b/
limitations:
  - This is a proof-B derivation, not verifier promotion.
  - The theorem is conditional on the frozen prism-free rank-11 endpoint.
  - No endpoint, cover, packet system, code, or graph is constructed.
  - The exact rational relaxation remains feasible at a nonintegral row.
  - The improvement supplies no incompatible upper bound.
  - Rank 11, endpoint existence, strict original n3 improvement, external
    novelty, and Conway-99 remain UNKNOWN.
```

## Verdict

`DERIVED_PENDING_INDEPENDENT_VERIFICATION`.

The fixed-center exact-three geometry supplies a new inequality valid
before imposing equality.  Combining it with the verified Wave194 system
gives

```text
Q>=6980,                                           (1)
```

where `Q` counts projective short circuits cross-realizing at least one
graph nonedge.

This is a finite-set and incidence-theoretic improvement, not a search.
It also avoids a genuine gap found during hostile audit in an attempted
type-one leaf-support argument.

## 1. Canonical flags give intersecting 3-subsets

For every selected or old-raw exact-three companion pair, Wave180
recovers a unique canonical flag

```text
(x,T),  T={y,u,v},  x anticomplete to T,
```

and a 3-subset `A_x(T)` of the seven graph-triangle blocks through `x`
such that

```text
c4(x,T)
 =z_T+2*sum_(S in A_x(T)) z_S
=0.                                               (2)
```

The verified pool separation prevents a selected pair from being reused
as a raw pair, and canonical companion uniqueness prevents two distinct
pairs from producing the same `(x,T)`.

Fix `x`.

First, the map `T -> A_x(T)` is injective.  Equal `A`-sets in (2) would
subtract to a nonzero weight-two relation `z_T-z_T'=0`, contrary to the
verified dual distance at least four.

Second, the image is intersecting.  If `A=A_x(T)` and `A'=A_x(T')` were
disjoint, let `L` be the seventh star block.  Adding their two relations
(2) to the full-star relation gives

```text
z_T+z_T'+z_L=0.                                   (3)
```

The three columns are distinct, so (3) is a forbidden weight-three
relation.

Thus all exact-three flags at a fixed center inject into an intersecting
family of 3-subsets of a seven-set.

## 2. The oriented-label local bound

Let

```text
c_x = number of exact-three flags centered at x,
j_x = number of distinct oriented labels x->y in their leaf union.
```

If `c_x=0`, the desired bound is immediate.  If the nonempty intersecting
family has empty total intersection, the
`(n,k)=(7,3)` Hilton--Milner theorem gives

```text
c_x
 <=C(6,2)-C(3,2)+1
 =13.
```

Since each flag has three leaves,

```text
j_x<=3c_x<=39.                                    (4)
```

If instead every `A_x(T)` contains one block

```text
S={x,p,q},
```

then `S in A_x(T)` means `j(T,S)=2`.  A vertex outside `T` cannot be
adjacent to two vertices of the graph triangle `T`, because it would be a
second common neighbor of the edge between those two vertices.  Hence
both `p` and `q` contribute exactly one cross edge to `T`.  The two leaf
vertices are distinct: otherwise that leaf would be a second common
neighbor, besides `x`, of the edge `pq`.

Across the distinct leaf union, the possible `p`-neighbors lie among the
12 neighbors of `p` outside `{x,q}`, and the possible `q`-neighbors lie
among the 12 neighbors of `q` outside `{x,p}`.  Each flag has at most one
remaining leaf.  The ordinary `(7,3)` Erdos--Ko--Rado bound also gives
`c_x<=15`.  Consequently

```text
j_x<=12+12+c_x<=39.                               (5)
```

Equations (4)--(5) prove the universal local cap

```text
j_x<=39.                                          (6)
```

## 3. The new global row

Let `J=sum_x j_x`.  Summing (6) over 99 centers gives

```text
J<=99*39
 =3861.                                           (7)
```

For the reverse inequality, let `U` be the union of labels served by
selected exact-three circuits.  The selected cover gives

```text
|U|>=C-n1-2n2.                                    (8)
```

Every `a3` or `b3` assignment is an oriented private label carried by an
old exact-three flag.  These oriented labels are distinct:

- type-one private labels are distinct;
- the two raw translations for one type-two private label have opposite
  centers and hence opposite orientations; and
- assignments on different private labels cannot collide.

Privacy keeps all of them outside `U`.  Therefore

```text
J>=|U|+a3+b3
 >=C-n1-2n2+a3+b3.                               (9)
```

Combining (7)--(9) gives the new nonnegative slack

```text
SG
 =3861-C+n1+2n2-a3-b3
 >=0.                                            (10)
```

No equality assumption is used in (10).

## 4. Exact certificate

Retain the verified Wave194 notation

```text
SI=I-2C,
S2=p2-n2,
SE2=2r2-a2-c2,
RA=3h+y+3g-a2-a3-2b3-c2,
SL=n1+2n2+c1+2r2+y+2W-C,

Q0=n1+n2+2n3+r1+r2+2h+y+2g+W.
```

The counted pools are disjoint, so `Q>=Q0`.  Using

```text
n1=a1+a2+a3,
2p2=b1+b3,
p3=c1+c2,
r1=a1+b1+c1,
```

exact coefficient expansion gives

```text
Q0-(11C-3861)/6

 =2SI/3
  +4S2/3
  +SE2/6
  +2RA/3
  +SL/3
  +SG/6
  +a1/6
  +b3/2
  +c2/6
  +W/3.                                          (11)
```

Every term on the right is nonnegative.  With `C=4158`,

```text
(11C-3861)/6=13959/2.
```

Thus `Q>=13959/2`, and integrality proves (1).

Adding the 693 verified edge-isolated projective circuits gives at least

```text
7673
```

projective short-circuit classes and the circuit-specific scalar
consequence

```text
B4+B5+B6+B7+B8+B9>=15346.
```

Wave188's verified `18018` bound on all short dual words remains
numerically stronger because it includes nonminimal words.

## 5. Sharp rational boundary

The six slack rows `SI,S2,SE2,RA,SL,SG` and every extra term in (11)
vanish at the nonnegative rational control

```text
n1=a2=99,
n2=p2=99,
n3=1386,
b1=198,
p3=c1=3663,
r1=3861,
r2=99/2,
y=99,
all other variables zero.                        (12)
```

It has

```text
Q0=13959/2.
```

This is not integral and does not represent a cover, packet system, code,
or graph.  It shows only that certificate (11) is exact for the displayed
linear relaxation.

## 6. Hostile audit of the abandoned leaf route

An attempted alternate proof tried to show that every type-one-oriented
packet owner equals a canonical all-equal `3+6` leaf circuit.  Its second
circuit subtraction can return the already selected owner: the translated
word differs from that owner by a full star, and the exact-three
center-star direction lies in the span of the companion pair.  Subtracting
the companion may also reintroduce a coordinate omitted by the first
translation.

No such leaf-support claim is used in (2)--(11).  The successful proof
uses only canonical exact-three flags and distinct oriented private-label
assignments.

## Boundary

```text
conditional Q>=6930 theorem:          VERIFIED (Wave194)
universal fixed-center row SG:        DERIVED
conditional Q>=6980 theorem:          DERIVED
exact rational replay:                PASS
independent Wave195 verification:     pending
rank 11 / endpoint excluded:          no
strict original n3 improvement:       no
Conway-99 / external novelty:         UNKNOWN
```
