# Wave 33: a contraction wall and an eight-vertex board for the rootless motif

```yaml
role: proof_b
date_utc: 2026-07-24T09:48:53Z
git_commit: b2595baa40d50e9c259051751fe27090bee6a449
claim_label: UNKNOWN
scope: >-
  Under the frozen n3=708 endpoint package, test whether actual
  vertex-triangle incidence and the projector/Schur identities force
  tr(A_-1 A_-2^2)>0. The report derives an exact local null trade proving
  that the complete two-leg spectral/incidence contraction algebra does
  not determine the decisive count, and it reduces every actual R2 pair
  to an eight-vertex board with four transversal-triangle candidates.
  It does not prove that a complete target can keep all candidates open.
inputs:
  verification/wave33-continuation-protocol.md: b98b6bb8228b54b67cd949ee1bf6eb05ebd6ebe74f1cbc9e49b041a55e2d2fe6
  agents/2026-07-24-wave32-indecomposable-proof.md: 5e0e0ce6e33cd8f943d8026c2b9b01b74d9668234d4c9b2c46da6c0c9921b8ef
  attempts/wave32-indecomposable/exact-results.json: bccde9635d973e030e004800abc08c37089e036faca1edc2bb85ed70ee731472
  verification/wave32-indecomposable/audit.md: 15285e618b3a38c91c5d2e373dcb859720a2062d9ca108cd79cae12506a53f44
  verification/wave32-indecomposable/independent-results.json: 4b90ef54358a14abc92c925c8e0f94ed9510b4f80857fde5aa4e2abf4ba89e2a
  agents/2026-07-24-wave31-survivor-proof.md: 075566744e2622a4dfa402a125d394aef16dfcb3fc53b172176dce88bd951aaa
  verification/wave31-sign-commutant/audit.md: f6145a3c4f4e787b23440a6ea071d606477821abab0ab8e7e5fe52042d6528a0
  agents/2026-07-23-wave20-global-schur.md: 64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
  agents/2026-07-24-wave32-rooted-proof.md: 04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0
  verification/wave32-rooted-vector/audit.md: 36d83232d82e30205e0aefa30aedff0a517de1edb0adbaa54575ea68d04ce1a5
method: >-
  Exact adjacency-algebra multiplication; a nonnegative integral local
  relation-tensor null trade; reduction of every fully contracted two-leg
  vertex-incidence moment to Q[Gamma]; direct lambda/mu counting around an
  actual N3 pair; and hostile partial 99-vertex incidence assignments.
command: |-
  cd attempts/wave33-rootless-motif
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
limitations:
  - Discovery cannot self-promote; every scoped reduction needs a fresh verifier.
  - The two relation tables are local moment controls, not global matrices.
  - The q=2 base pair used by the null trade is permitted but is not proved
    to occur as an R2 pair in a target.
  - The 99-vertex incidence controls are partial edge assignments, not SRGs.
  - Uncontracted three-leg incidence and full projector/Schur compatibility
    are not captured by the null trade.
  - Actual-incidence motif forcing, the rootless endpoint, n3=708,
    Conway-99, and novelty remain UNKNOWN.
```

## Result

The rootless branch is not closed.  The strongest exact conclusion is:

```text
all two-leg spectral/incidence contractions are locally blind to the motif;
every actual R2 pair has exactly four transversal closure candidates;
whether full target compatibility closes any candidate is UNKNOWN.
```

More explicitly:

```text
Q[Gamma] two-leg local blindness:                    DERIVED
contracted two-leg vertex-incidence local blindness: DERIVED
eight-vertex board and four candidates per R2 pair:  DERIVED
actual incidence forces tr(A_-1 A_-2^2)>0:           UNKNOWN
rootless indecomposable endpoint:                     UNKNOWN
n3=708:                                               UNKNOWN
Conway-99 existence/nonexistence and novelty:         UNKNOWN
```

The matrix-only and actual-incidence parts of the report are separated
below.  No automorphism, orbit, transitivity, or restricted graph search is
used.

## 1. The exact weighted adjacency algebra

Let `Gamma` be the 231-vertex triangle-intersection adjacency matrix and
write

```text
C=Gamma^2-5Gamma-18I.
```

For two disjoint graph triangles, `C[T,U]` is their number
`r(T,U)` of cross edges.  Put `Rj` for the off-diagonal relation `r=j`,
and let `G` denote intersecting triangle pairs.  Then

```text
C=R1+2R2+3R3,
M=3I+J-Gamma-C.
```

Thus `M` has the relation values

| relation | `D` | `G` | `R0` | `R1` | `R2` | `R3` |
|---|---:|---:|---:|---:|---:|---:|
| `Gamma` | 0 | 1 | 0 | 0 | 0 | 0 |
| `C` | 0 | 0 | 0 | 1 | 2 | 3 |
| `M` | 4 | 0 | 1 | 0 | -1 | -2 |

The spectra

```text
spec(Gamma)={18,7,0,-3},
spec(C)={216,-4,-18,6}
```

give the exact multiplication identities

```text
Gamma^2 = 18I+5Gamma+C,                           (1)
Gamma C = -18I+18J-2Gamma-C,                     (2)
C^2     = 72I+216J-16Gamma-14C.                  (3)
```

These products stay in

```text
mathcal A=Q[Gamma]=span_Q{I,J,Gamma,C}.           (4)
```

The individual `Rj` need not lie in (4).  Their degrees depend on
`q(T)`, so promoting them to association-scheme relations would be an
unsupported assumption.

## 2. A complete local null trade for an `R2` pair

Fix a formal allowed `R2` pair `(T,U)` with

```text
q(T)=q(U)=2.
```

For each third triangle `V`, record the relation `a` from `T` to `V`
and `b` from `V` to `U`.  In relation order

```text
(D,G,R0,R1,R2,R3),
```

the row and column margins must be

```text
(1,18,22,174,6,10).                              (5)
```

The following two exact symmetric tables both satisfy (5).  The first has
no common `R3` neighbor:

```text
       D  G R0  R1 R2 R3
D      0  0  0   0  1  0
G      0  2  9   2  1  4
R0     0  9  7   0  0  6
R1     0  2  0 172  0  0
R2     1  1  0   0  4  0
R3     0  4  6   0  0  0.                       (6)
```

The second has exactly one:

```text
       D  G R0  R1 R2 R3
D      0  0  0   0  1  0
G      0  2 10   0  2  4
R0     0 10  3   3  1  5
R1     0  0  3 171  0  0
R2     1  2  1   0  2  0
R3     0  4  5   0  0  1.                       (7)
```

Against basis order `(I,J,Gamma,C)`, both (6) and (7) have the exact
bilinear contraction matrix

```text
[ 0   1  0   2 ]
[ 1 231 18 216 ]
[ 0  18  2  16 ]
[ 2 216 16 188 ].                               (8)
```

The lower-right `3`-by-`3` entries of (8) are exactly (1)--(3) evaluated
at an `R2` pair.  Both tables also give

```text
sum_V M[T,V]M[V,U]=(M^2)[T,U]=-21.               (9)
```

Subtracting (6) from (7) gives a signed integral trade with zero row and
column margins and zero contraction against every ordered pair of basis
elements in (4), while its `(R3,R3)` entry is `+1`.  By bilinearity, it is
invisible to `(FG)[T,U]` for every `F,G in mathcal A`.

This is stronger than a pair-count objection, but it remains local.  It does
not prove that either table can be used simultaneously at all pairs.

## 3. Fully contracted two-leg incidence returns to the same algebra

The actual vertex-triangle incidence matrix satisfies

```text
N^T N=3I+Gamma,
N N^T=7I+A.
```

Consequently, for every nonnegative integer `k`,

```text
N^T A^k N
 =(3I+Gamma)(Gamma-4I)^k
 in Q[Gamma].                                    (10)
```

The checker audits (10) on all four eigenspaces for `k=0,...,5`.
Therefore contracting both vertex legs of any expression of this form
does not escape the null-trade wall.

Equation (10) does not erase actual incidence from the problem.  It shows
precisely that a successful incidence argument must retain vertex labels or
use genuine three-leg or higher compatibility instead of contracting back
to two triangle indices.

## 4. Actual incidence around an `R2` pair

Now use the graph itself, not only the matrix algebra.  Label the two base
triangles

```text
T={t0,t1,t2},
U={u0,u1,u2},
```

with the two cross edges

```text
t0-u0, t1-u1.
```

An outside vertex is adjacent to at most one vertex of each base triangle:
otherwise an edge of the triangle would have two common neighbors, contrary
to `lambda=1`.

For each `(ti,uj)`, the number of common neighbors outside the six base
vertices equals `lambda` or `mu` minus those already inside.  The resulting
exact `3`-by-`3` board is

```text
       u0 u1 u2
t0      1  0  1
t1      0  1  1
t2      1  1  2.                                (11)
```

Thus exactly eight outside vertices see one vertex in each base triangle.
The rest of the 93 outside vertices have the exact census

```text
T-side only by row: 9,9,8,
U-side only by column: 9,9,8,
neither side:         33.                        (12)
```

All counts in (11)--(12) use actual target incidence.

## 5. Four exact closure candidates per `R2` pair

A triangle `V` is `R3` from both `T` and `U` exactly when its three
vertices lie on the board (11), occupy all three rows and all three columns,
and form a graph triangle.

Counting the two copies in cell `(t2,u2)`, there are exactly four
pair-indexed transversal selections:

```text
(00,11,22a),
(00,11,22b),
(00,12,21),
(02,11,20).                                     (13)
```

Therefore every unordered `R2` pair has exactly four candidates whose
closure would create the forbidden motif.  At `n3=708`, this is

```text
4*708=2832                                        (14)
```

pair-indexed candidates, with multiplicity across base pairs.

Rootlessness requires every candidate in (14) to remain open.  Equivalently,

```text
tr(A_R2 A_R3^2)=0.
```

The trace is twice the number of closed unordered pair-indexed candidates,
as in Wave 32.

## 6. Exact hostile partial-incidence controls

The checker realizes all 93 categories from (11)--(12) on a common
99-vertex set.  In both controls:

- the six base degrees are exactly 14;
- every base-base pair has its exact `lambda=1` or `mu=2` common-neighbor
  count;
- no already-present edge has more than one present common neighbor;
- no currently absent pair has more than two present common neighbors.

The first control fixes every board edge absent and closes zero candidates.
The second adds the graph triangle on `(00,11,22a)` and closes exactly one.

These are deliberately partial edge assignments.  Most outside-outside
edges, outside degrees, and `lambda/mu` equations remain unspecified.  The
controls prove only that the base-incidence census and immediate parameter
caps do not decide (13).  They are not graph constructions or extension
certificates.

## 7. Strongest self-objection and next obligation

The strongest objection is valid and blocking:

> The null trade is not a globally compatible relation tensor, and the
> partial controls are not SRGs.  Full uncontracted incidence, global
> projector idempotence, Schur-square origin, or overlap consistency across
> the 708 base pairs could still force at least one candidate in (14) to
> close.

Accordingly, the next exact obligation is:

```text
prove that all 2832 pair-indexed transversal clauses cannot remain open
under the complete SRG plus projector/Schur package,
or construct a complete valid endpoint satisfying every clause.          (15)
```

The full failed-route and premise-deletion record is
`attempts/wave33-rootless-motif/failed-routes.md`.  The standard-library
suite passes fourteen hostile tests and regenerates canonical LF-only JSON.
No solver status, numerical approximation, or failure-to-find inference is
used.
