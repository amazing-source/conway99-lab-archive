# Independent Wave 57 star-complement audit

Verdict: `REFUTED_IN_PART`.

The central projector and star-set argument is correct, but the discovery
package materially overstates the size of the surviving endpoint parameter
space.  Two independent corrections are required:

1. `X` is a cubic graph on 36 vertices, so
   `4 C4(X) <= 36 binom(3,2)=108` and therefore `C4(X)<=27`, not merely
   `C4(X)<=89`.
2. The already verified Wave 36 block transfer proves
   `mult_Y(3)=18` and `mult_Y(-4)=7+kappa`, where the component count
   `kappa` is in `{1,2,3}`.  Thus only `(18,8)`, `(18,9)`, and `(18,10)`
   are live in the project, not all 18 rows of the weaker Wave 57 moment
   relaxation.

The endpoint is not excluded, no graph is constructed, and Conway-99 remains
`UNKNOWN`.

## Clean-room boundary

The verifier protocol and upstream hashes were frozen before the discovery
implementation was inspected.  The sealed discovery package was then hashed
separately.  The checker imports no discovery code and uses only standard
library integer and rational arithmetic.  No automorphism of the completed
graph, the fixed triangle, or its fibres is assumed.

## 1. Fixed-triangle quotient and supported eigenspaces

For an arbitrary triangle `T={t0,t1,t2}`, let `Xi` be the 12 neighbors of
`ti` outside `T`, put `X=X0 union X1 union X2`, and let `Y` be the remaining
60 vertices.  The SRG equations and prism-free endpoint give the equitable
quotient

```text
[2 12  0
 1  3 10
 0  6  8],
```

whose characteristic polynomial is

```text
x^3-13x^2-26x+168=(x-14)(x-3)(x+4).
```

For either `lambda=3` or `lambda=-4`, choose
`beta_0+beta_1+beta_2=0`, give `Xi` the constant value `beta_i`, give
`ti` the value `lambda beta_i`, and give `Y` value zero.  The coordinate
equations reduce exactly to

```text
lambda(lambda+1)=12.
```

The sum-zero plane is two-dimensional.  The claimed two-dimensional full
graph eigenspaces supported on `U=T union X` are therefore `VERIFIED`.

## 2. Projector blocks and equality wording

Exact multiplication in `Q[I,A,J]`, using
`A^2=12I-A+2J`, verifies

```text
E_3  = ( A+4I-(2/11)J)/7,   rank 54,
E_-4 = (-A+3I+(1/9)J)/7,   rank 44.
```

The two projectors are idempotent and orthogonal.  Because `A_Y` is
8-regular, the all-one direction has nonzero block eigenvalues `12/77` and
`5/21`.  On its orthogonal complement, the kernels are precisely the
`-4` and `3` eigenspaces of `A_Y`.  Writing

```text
a=mult_Y(3),  b=mult_Y(-4),
```

gives the exact equalities

```text
rank E_3[Y,Y]  = 60-b,
rank E_-4[Y,Y] = 60-a,

dim(full 3-eigenvectors supported on U)  = b-6,
dim(full -4-eigenvectors supported on U) = a-16.
```

These are equalities, not merely lower bounds.  The explicit sectors imply
the weaker bounds `b>=8` and `a>=18`.  No improper strict-interlacing step is
used: after all copies of the boundary eigenvalues are removed, the residual
roots are strictly in `(-4,3)` by definition and principal-projector
positivity.

## 3. Exact star-set intersections

A star set is a coordinate basis for the relevant eigenspace.  The maximum
number of basis columns selectable from `Y` is exactly the rank of the
corresponding principal projector block.  A maximum independent subset
extends to a basis, so the discovery's minima are exact:

```text
min |S_3 intersect U|  = b-6,
min |S_-4 intersect U| = a-16.
```

Thus no relevant full-graph star set lies wholly in `Y`.  The Wave 57
argument itself gives ranges `2..7` and `2..4`; after applying the prior
Wave 36 transfer, the project-valid values sharpen to:

```text
min |S_3 intersect U|  in {2,3,4},
min |S_-4 intersect U| = 2.
```

This exact minimum-hit packaging is a valid additional consequence.  It does
not identify a canonical star set and supplies no safe symmetry reduction.

## 4. `Y` counts and moment formulas

The 231 graph triangles split as

```text
T / TXX / XXX / XXY / XYY / YYY
1 /  18 /   0 /  36 / 144 /  32.
```

Hence `G[Y]` has order 60, degree 8, 240 edges, and 32 triangles, with

```text
tr(A_Y^0..3)=(60,0,480,192).
```

After removing eigenvalue 8 and the `a` copies of 3 and `b` copies of -4,
the residual power sums are exactly

```text
p0=59-a-b,
p1=-8-3a+4b,
p2=416-9a-16b,
p3=-320-27a+64b.
```

The degree-one localizer determinants reproduce

```text
158976-7644a,
96480-7056b,
```

and therefore the weaker moment box `18<=a<=20`, `8<=b<=13`.  Exact
enumeration confirms that all 18 Cartesian-product pairs pass this truncated
order-three system.

## 5. Four-cycle double count and the missed bound

Let `q=C4(X)`.  The discovery's block-overlap double count is correct:

```text
n0=342+2q,  n1=900-4q,  n2=288+2q,
C4(Y)=171+q,
tr(A_Y^4)=8568+8q.
```

In particular, the two opposite pairs account for each four-cycle exactly
twice; no double-count defect was found in these formulas.

However, nonnegativity of `n1` is far from the best elementary bound.
At each vertex of the cubic graph `X`, at most its three unordered neighbor
pairs can lie on a four-cycle through that vertex.  The two neighbors are
nonadjacent, and `mu=2` leaves at most one second common neighbor after the
central vertex, so a neighbor pair closes at most one such cycle.  Counting
vertex-cycle incidences gives

```text
4q <= 36*3,
q <= 27.
```

The discovery's localizer

```text
[ 300  -192
 -192  840-8q ]
```

correctly gives `q<=89`, but this is weaker.  Intersecting the 18-row moment
ledger with `q<=27` leaves only nine rows:

```text
(18,8..12) and (19,8..11).
```

Using the already verified Wave 36 spectral transfer leaves only

```text
(18,8), (18,9), (18,10), each with 0<=q<=27
```

at this level of constraints.

## 6. Scalar controls

All 18 supplied scalar controls exactly reproduce power sums through degree
four.  The two quadratic controls use conjugate roots of

```text
x^2+4x+1,
x^2+5x+5,
```

which are exact algebraic integers strictly inside `(-4,3)`.  Their power
sums, equal conjugate multiplicities, and Newton divisibilities through
degree four all check.

This verifies only the stated weaker scalar moment system.  Just eight of the
18 supplied controls have `q<=27`; notably, the supplied `(18,12)` control
uses `q=33` even though that row still has moment-feasible values `24..27`.
The controls are not graph spectra and do not satisfy the stronger Wave 36
spectral-transfer requirement by construction.

## 7. Project-prior chronology and the corrected smaller target

Wave 36 had already verified the full one-triangle block equations.  If
`kappa` is the number of components of `X`, its component analysis gives
`kappa in {1,2,3}` and

```text
rank(B)=35-kappa.
```

The transferred `A_Y` spectrum and the kernel trace equations then give

```text
a+b=25+kappa,
3a-4b=26-4kappa,
a=18,
b=7+kappa.
```

It had also already verified 32 triangles in `Y` and
`C4(Y)=171+C4(X)`.  Wave 57's multiplicity box and four-cycle transfer are
therefore redundant and weaker inside this repository.  No novelty claim is
supported.

The exact `Y` rank target should be recorded with the strongest known project
constraints:

```text
rank(11A_Y+44I-2J) in {50,51,52},
rank(-9A_Y+27I+J) = 42.
```

Equivalently, inside `Y` a `3`-star complement has order exactly 42, and a
`-4`-star complement has order 50, 51, or 52.  This is a legitimate necessary
60-vertex subproblem.  It reconstructs `A_Y`, not the missing `T/X/Y`
incidence data, so solving it alone would not construct the 99-vertex
endpoint.

## Reproduction

```powershell
python -B verification\wave57-star-complement\independent_check.py
python -B verification\wave57-star-complement\independent_check.py `
  --verify verification\wave57-star-complement\independent-results.json
python -B -m unittest discover `
  -s verification\wave57-star-complement -p "test_*.py" -v
```

The verifier has 12 tests: one baseline and 11 hostile checks covering the
quotient, supported dimension, projector rank, multiplicity box, triangles,
four-cycle ranges, scalar power sums, quadratic factors, prior multiplicity
transfer, star-complement orders, and status inflation.

## Final classification

```text
quotient and supported 3/-4 sectors:             VERIFIED, conditional
projector ranks and supported dimensions:        VERIFIED, conditional
exact star-set minimum-hit argument:              VERIFIED, conditional
Y order/degree/triangles/moments:                 VERIFIED, conditional
C4(Y)=171+C4(X) and trace-four ledger:            VERIFIED, conditional
18-row truncated moment ledger:                   VERIFIED as weaker relaxation
18 scalar controls:                              VERIFIED as weaker controls
C4(X)<=89 as the active combinatorial bound:      REFUTED; sharpened to <=27
18 pairs as live endpoint possibilities:          REFUTED; project prior leaves 3
Wave57 multiplicity/C4-transfer novelty in repo:  REFUTED by Wave36 chronology
60-vertex Y graph or reconstruction matrix:       UNKNOWN
endpoint exclusion/construction, Conway-99:       UNKNOWN
```
