# Wave 33 rootless motif: failed routes and exact boundary

## Treating the five off-diagonal classes as an association scheme

This is not justified.  The triangle-intersection relation `G` is regular,
and the weighted cross-edge matrix

```text
C=R1+2R2+3R3
```

is regular, but the individual disjoint-pair relations have row degrees

```text
deg(R0)=20+q(T),
deg(R1)=180-3q(T),
deg(R2)=3q(T),
deg(R3)=12-q(T).
```

At `n3=708`, `sum q(T)=472`, so these valencies need not be
constant.  Replacing their local intersection counts by association-scheme
intersection numbers would add an unproved regularity hypothesis.

## The full two-leg spectral algebra is locally blind

The exact adjacency algebra is

```text
Q[Gamma]=span_Q{I,J,Gamma,C},
```

with

```text
Gamma^2 = 18I+5Gamma+C,
Gamma C = -18I+18J-2Gamma-C,
C^2     = 72I+216J-16Gamma-14C.
```

For a permitted formal `q(T)=q(U)=2` `R2` pair, the checker gives two
nonnegative integral third-triangle tables.  They have identical margins,
identical contractions against every pair of elements of `Q[Gamma]`, and
the same projector entry `(M^2)[T,U]=-21`, but their common `R3` counts are
zero and one.

The signed difference is an exact local null trade.  It preserves every
bilinear contraction in this algebra while changing the decisive cell by
one.  This blocks any argument that only rewrites already-known
two-leg spectral products.

The control is local.  It does not assert that a `q=2` `R2` pair must occur
in a target, or that either table extends to a simultaneous global relation
tensor.

## Fully contracting vertex incidence adds no two-leg separator

The exact incidence identities give, for every nonnegative integer `k`,

```text
N^T A^k N=(3I+Gamma)(Gamma-4I)^k.
```

Thus every expression with two triangle legs obtained by contracting
`N`, a polynomial in the vertex adjacency matrix, and `N^T` lands back in
`Q[Gamma]`.  The local null trade is invisible to that whole family.

This does not cover uncontracted vertex labels, diagonal selectors depending
on a chosen vertex, or genuine three-leg and higher incidence compatibility.
Those are precisely where a successful continuation must add information.

## Pair density does not force a mixed triangle

At the endpoint the unordered edge counts are

```text
|R2|=708,
|R3|=1150.
```

Positive counts of both colors do not imply that an `R2` edge has a common
`R3` neighbor.  In graph language, rootlessness asks every `R3`
neighborhood to be independent in `R2`; the two global edge totals alone
do not contradict this.

For a fixed triangle `T`, put `H=N_R3(T)` and `h=12-q(T)`.  If the frame
vectors are `u_U`, then

```text
s=sum_(U in H) u_U,
<u_T,s>=-2h,
||s||^2>=h^2.
```

Expanding gives only

```text
4h+2(e_R0-e_R2-2e_R3)>=h^2
```

for the relation counts inside `H`.  Setting `e_R2=0`, as rootlessness
requires, does not make this scalar inequality inconsistent.  For example,
at `h=10`, the formal values `e_R0=30`, `e_R3=0`, and fifteen remaining
zero-product pairs meet it with equality.  This is not a local Gram
construction; it records why the first PSD projection does not close the
branch.

## Schur positivity does not currently isolate the target trace

The matrices

```text
W=M o M,
A4=MWM
```

are positive semidefinite in the frozen endpoint package.  Their known
traces control weighted sums of colored triangles, but no inherited identity
determines `tr(MW^2)`, `tr(W^3)`, or an equivalent combination that
separates

```text
tr(A_R2 A_R3^2).
```

Assuming that `W` commutes with `M`, or that `R2` and `R3` themselves lie in
`Q[Gamma]`, would silently add exactly the missing association-scheme
property.

## The exact eight-vertex board is a reduction, not a closure proof

For every actual `R2` pair, the six base vertices force an eight-vertex
double-neighbor board with cell multiplicities

```text
[1 0 1]
[0 1 1]
[1 1 2].
```

Exactly four selections take one board vertex from each row and each column.
A selected triple closes to a graph triangle exactly when it is a common
`R3` neighbor of both base triangles.

The checker builds two partial 99-vertex edge assignments.  Both give all six
base vertices degree 14, realize every base-pair `lambda/mu` count exactly,
and violate no already-present common-neighbor cap.  One fixes every board
edge absent; the other closes one transversal.  Most outside-outside edges,
degrees, and common-neighbor equations remain unspecified.  These controls
prove that the first local incidence layer does not decide closure; they are
not SRG completions.

At `n3=708`, there are

```text
4*708=2832
```

pair-indexed transversal candidates.  Rootlessness requires every one to
remain open.  Counting 2832 candidates is not a contradiction because
candidates can overlap and no verified global lower bound on their closure
count has been obtained.

## Exact boundary and strongest objection

```text
Q[Gamma] two-leg local blindness:                    DERIVED
contracted two-leg vertex-incidence local blindness: DERIVED
eight-vertex board and four candidates per R2 pair:  DERIVED
all 2832 pair-indexed candidates can remain open:    UNKNOWN
actual incidence forces positive mixed trace:        UNKNOWN
rootless indecomposable endpoint:                     UNKNOWN
n3=708:                                               UNKNOWN
Conway-99 and novelty:                                UNKNOWN
```

The strongest objection is valid and blocking: neither local table is a
globally compatible relation tensor, and neither partial incidence assignment
is a graph.  A global projector, Schur, or higher-incidence compatibility
argument could still force the target trace positive.
