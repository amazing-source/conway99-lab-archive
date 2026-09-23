# Wave 33 rootless motif: clean-room precomparison reconstruction

```yaml
role: verifier
date_utc: 2026-07-24T10:29:09Z
git_commit: b2595baa40d50e9c259051751fe27090bee6a449
claim_label: DERIVED
scope: >-
  Independent reconstruction, before candidate inspection, of the fused
  triangle algebra, two formal local tables invisible to every bilinear
  fused-algebra contraction, the exact vertex-incidence transport, and the
  actual lambda/mu multiplicity board around an R2 triangle pair. This is a
  scoped non-forcing result, not a proof of global motif existence or
  avoidance.
```

## Independence wall

This reconstruction and its checker, tests, and first result JSON were
written without opening, printing, hashing through content-sensitive tools,
importing, or executing:

```text
agents/2026-07-24-wave33-rootless-motif.md
attempts/wave33-rootless-motif/
verification/wave33-rootless-motif-candidate-freeze.sha256
```

Only the public base commit, the Wave 33 continuation protocol, and verified
Wave 20/Wave 32 premises were used.  Candidate comparison remains pending.

## 1. Frozen triangle relations

Let `N` be the `99 x 231` vertex-triangle incidence matrix, `A` the
putative target adjacency, and `Gamma` the triangle-intersection graph.
The verified public identities are

```text
N N^T=7I+A,
N^T N=3I+Gamma,
spec(Gamma)=18^1,7^54,0^44,(-3)^132.
```

For two disjoint graph triangles `T,U`, let `r(T,U)` be their number of
cross edges.  The cross edges form a matching, so `r` lies in
`{0,1,2,3}`.  Put

```text
C=Gamma^2-5Gamma-18I.
```

The verified Wave 20 incidence argument gives:

```text
C_TU=0                        if T=U or T intersects U,
C_TU=r(T,U)                   if T,U are disjoint.
```

Write `R_i` for the disjoint relation `r=i`.  At `n3=708`, Wave 32
requires the mixed motif consisting of one `R2` pair and a third triangle
in relation `R3` with both endpoints to be absent.  Equivalently,

```text
tr(A_R2 A_R3^2)=0.
```

One unordered motif contributes exactly two to this trace.

## 2. Exact multiplication in `Q[Gamma]`

The four distinct eigenvalues give minimal polynomial

```text
x(x-18)(x-7)(x+3)
 =x^4-22x^3+51x^2+378x.
```

The public cubic relation is

```text
Gamma^3-4Gamma^2-21Gamma=18J.
```

Consequently

```text
Q[Gamma]=span_Q{I,J,Gamma,C}.                       (1)
```

The evaluation matrix of this ordered basis on eigenvalues
`18,7,0,-3` has determinant `48510`, so the four elements are independent.
Direct reduction gives the complete multiplication table:

```text
J^2       =231J,
J Gamma   =18J,
J C       =216J,

Gamma^2   =18I+5Gamma+C,
Gamma C   =-18I+18J-2Gamma-C,
C^2       =72I+216J-16Gamma-14C.                   (2)
```

Together with multiplication by `I`, equations (2) determine every
product in (1).  The checker verifies them independently at all four
eigenvalues.

The coefficient `-5` in the definition of `C` is active.  Replacing it by
`-4` makes an intersecting off-diagonal entry equal one rather than zero,
so the mutated matrix is not the cross-edge count.

## 3. What the fused algebra can and cannot see

On a disjoint pair with cross-edge count `r`, a general element of (1) has
entry

```text
alpha+beta*r.                                       (3)
```

The four individual relation indicators on `r=0,1,2,3` are not affine.
In particular,

```text
A_R2 not in Q[Gamma],
A_R3 not in Q[Gamma].                               (4)
```

Thus closure of the four-dimensional algebra cannot by itself determine

```text
(A_R3^2)_TU,
```

the number of common `R3` triangles at an `R2` pair.  This dimension loss
is exact; it is not a numerical heuristic.

## 4. Two fused-algebra-indistinguishable local tables

For a fixed triangle with activity `q`, the verified relation margins in
category order

```text
(D,Gamma,R0,R1,R2,R3)
```

are

```text
(1,18,20+q,180-3q,3q,12-q).
```

At `q(T)=q(U)=2`, these are

```text
(1,18,22,174,6,10).                                (5)
```

Assume formally that `(T,U)` is an `R2` pair with both activities two.
The table entry in row `X`, column `Y` counts third triangles `V` with
`(T,V)` in `X` and `(U,V)` in `Y`.  Consider:

```text
             D   G  R0   R1  R2  R3
N_0 =
 D           0   0   0    0   1   0
 G           0   2   0   16   0   0
 R0          0   0  13    0   5   4
 R1          0  16   0  152   0   6
 R2          1   0   5    0   0   0
 R3          0   0   4    6   0   0
```

and

```text
             D   G  R0   R1  R2  R3
N_1 =
 D           0   0   0    0   1   0
 G           0   2   0   16   0   0
 R0          0   0   9    4   5   4
 R1          0  16   4  149   0   5
 R2          1   0   5    0   0   0
 R3          0   0   4    5   0   1.
```

Both are symmetric, nonnegative, integral, total 231, and have margins
(5).  Their fixed pair cells are

```text
N(D,R2)=N(R2,D)=1,
N(Gamma,Gamma)=2.
```

For the entry vectors of `I,J,Gamma,C`, every one of the 16 bilinear
contractions has the same matrix:

```text
[[  0,   1,  0,   2],
 [  1, 231, 18, 216],
 [  0,  18,  2,  16],
 [  2, 216, 16, 188]].                              (6)
```

This is exactly the multiplication table (2) evaluated at an `R2` pair.
By bilinearity, (6) proves equality for every pair of elements of
`Q[Gamma]`, not merely for a selected list of polynomials.

Nevertheless,

```text
N_0(R3,R3)=0,
N_1(R3,R3)=1.                                      (7)
```

The difference `N_1-N_0` has zero margins and zero contraction against
every ordered basis pair.  It is an explicit invisible direction of the
fused constraints.

This is a formal local control only.  Neither table is asserted to be the
intersection table of an actual 231-triangle configuration, and the
existence of a global `q=2,R2,q=2` pair is not proved.

## 5. Exact scope of vertex-incidence transport

Associativity applied to the two incidence Gram identities gives

```text
(7I+A)N=N(3I+Gamma),
A N=N(Gamma-4I).                                   (8)
```

Inductively, for every integer `k>=0`,

```text
N^T A^k N
 =(Gamma+3I)(Gamma-4I)^k
 in Q[Gamma].                                      (9)
```

The checker reduces the first nine powers exactly modulo the minimal
polynomial.  The first three are

```text
k=0: 3I+Gamma,
k=1: 6I+4Gamma+C,
k=2: 30I+18J+8Gamma-C.
```

At the `Gamma=-3` eigenspace, (9) vanishes as it must because that is the
kernel of `N`.

Equation (9) covers vertex-walk contractions mediated by `N`.  It does not
place arbitrary triple-incidence tensors, `A_R2`, or `A_R3` inside the
fused algebra.  In particular it does not undo the obstruction (4).  The
shift `-4` is forced by (8); the hostile shift `-3` fails.

## 6. Actual `lambda/mu` board at an `R2` pair

Now use actual graph incidence, not merely the fused algebra.  Relabel an
`R2` pair as

```text
T={t0,t1,t2},
U={u0,u1,u2},
cross edges t0-u0 and t1-u1.
```

For each cross pair `(ti,uj)`, count common neighbors outside `T union U`.
If the pair is adjacent, start from `lambda=1`; otherwise start from
`mu=2`.  Subtract common neighbors already inside the two triangles.
The internal and outside boards are:

```text
internal =
[[0,2,1],
 [2,0,1],
 [1,1,0]],

outside =
[[1,0,1],
 [0,1,1],
 [1,1,2]].                                         (10)
```

An outside witness cannot belong to two cells in different rows: it would
be a second common neighbor of an edge of `T`.  The same argument applies
to columns using edges of `U`.  Thus all board cells are disjoint.

A third triangle `V` in relation `R3` with both `T` and `U` must select
one witness in every row and column of (10), and the three selected
witnesses must induce a graph triangle.  Conversely, any such triangular
transversal is a common `R3` triangle.

The six permutations have total multiplicity:

```text
identity:       1*1*2 = 2,
(0,2,1):       1*1*1 = 1,
(2,1,0):       1*1*1 = 1,
other three:             0.
```

Hence there are exactly four candidate triples:

```text
(w00,w11,w22a),
(w00,w11,w22b),
(w00,w12,w21),
(w02,w11,w20).                                     (11)
```

The target value `mu=2` is active.  Mutating it to three changes (10) and
raises the weighted transversal count from 4 to 22.

## 7. Local zero-versus-one motif controls

The checker realizes the six vertices of `T,U`, the two `R2` cross edges,
and all eight outside witnesses from (10).  In both controls, all nine
`T-U` pairs have their exact target `lambda/mu` common-neighbor count.

The zero control adds no edges among witnesses, so none of the four
candidates (11) is a triangle.  The one control adds the three edges on

```text
(w00,w12,w21).
```

This realizes exactly one candidate triangle, with three cross edges to
each of `T` and `U`.  The two controls therefore have common-`R3` count
zero and one while preserving the complete board (10).

They have only 14 vertices and deliberately omit every `lambda/mu`
constraint outside the nine `T-U` cross pairs, global relation margins,
degree 14, and all projector/lattice/Schur identities.  They prove only:

> The exact board (10) identifies four candidates but does not locally
> decide which candidate triples induce triangles.

They do not prove global motif avoidance or existence.

## 8. Precomparison verdict and strongest objection

The clean-room evidence independently supports the five scoped synopsis
items:

1. the multiplication table of `Q[Gamma]`;
2. two formal `q=2,R2,q=2` tables invisible to every fused bilinear
   contraction but differing in common-`R3` count;
3. the transport identity (9), with its exact scope limit;
4. the actual board (10) and four candidates (11); and
5. the conclusion that these controls do not decide the global motif.

The strongest objection is scope inflation.  The two 6-by-6 tables are not
globally realizable objects, while the 14-vertex controls enforce only nine
selected `lambda/mu` constraints.  Neither can support a claim that actual
incidence globally permits, forces, or avoids the motif.  Conversely, the
four candidate triples do not constitute four actual triangles; their
three internal edges remain to be determined by the rest of the graph.

Therefore:

```text
fused-algebra non-forcing:             DERIVED PRECOMPARISON
local R2-board non-forcing:            DERIVED PRECOMPARISON
actual global motif trace:                         UNKNOWN
rootless endpoint:                                 UNKNOWN
n3=708:                                            UNKNOWN
Conway-99 existence/nonexistence:                   UNKNOWN
novelty:                                           UNKNOWN
```
