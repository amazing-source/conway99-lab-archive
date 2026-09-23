# Independent audit

## Verdict

`VERIFIED_WITH_SCOPE`.

Assuming the previously verified conditional branch

```text
n3=4158, P=0, rank_F3(D)=11,
```

the Wave 176 star-projector, trace-rank, cross-incidence, radical, and
rank-10 support claims are correct.  No endpoint exclusion follows.

## Star projector and trace Gram

The seven centered columns in a point-star have Gram matrix `J_7-I_7` and
sum zero.  This Gram matrix has rank six and kernel spanned by the all-one
coefficient vector.  Consequently the columns span a nondegenerate
six-space `E_x`.

For

```text
P_x=-sum_(T contains x) z_T tensor z_T,
```

the simplex Gram and the zero sum give `P_x z_U=z_U` for every star column.
The operator vanishes on `E_x^perp`, so it is the orthogonal projector onto
`E_x`.  Thus

```text
P_x^2=P_x, rank(P_x)=6, tr(P_x)=0 in F_3.
```

Each triangle belongs to three stars, giving `sum_x P_x=0`.

Directly expanding traces of rank-one maps gives

```text
tr(P_x P_y)=(B D^(o2) B^T)_(x,y).
```

At the endpoint, `D^(o2)-D=2L` and `BD=0`, hence

```text
(tr(P_x P_y))=2BLB^T.
```

Self-adjoint endomorphisms of an 11-space form a 66-dimensional space.
Trace is a nonzero functional because `tr(I)=11=2` in `F_3`; its kernel
therefore has dimension 65.  All `P_x` lie in that kernel, proving

```text
rank_F3(BLB^T)<=65.
```

The integer checks also reproduce.  The diagonal of `BLB^T` is zero, an
original graph edge has entry 12, the full row sum is 756, and the sum over
the 84 nonneighbors is `756-14*12=588`, with average seven.  These integer
averages do not determine the ternary nonedge residues.

## Adjacent cross-incidence graph

For adjacent `x,y`, remove their unique common triangle.  If `u` is one of
the twelve outer neighbors represented in an outer `x`-star triangle, then
`u` is nonadjacent to `y`.  The `mu=2` condition supplies, besides `x`,
exactly one common neighbor of `u,y`, and it lies in an outer `y`-star
triangle.  Thus each outer `x`-triangle has two cross incidences.

The two incidences cannot land in the same opposite triangle: that would
give two additional cross edges on top of `xy`, hence a disjoint
triangle-pair with three cross edges, excluded by `P=0`.  Reversing `x,y`
gives degree two on both sides.  The graph is therefore a simple
2-regular bipartite graph on `6+6` vertices.

Every component is an even cycle of length at least four.  Dividing its
length by two, the only partitions of six into parts at least two are

```text
(6), (4,2), (3,3), (2,2,2).
```

This classification uses no candidate-graph enumeration.

## Independent Gram-rank derivation

Write a coefficient vector as `(a,x,y)` for the common block and the two
sets of six outer blocks.  If `A` is the cycle biadjacency matrix, the Gram
kernel equations reduce to

```text
x=Ay+a*1,
y=A^T x+a*1,
```

because the first equation also forces `sum(x)+sum(y)=0`.  Since
`A^T 1=2*1`, substitution gives

```text
(I-A^T A)y=0.
```

On a cycle of half-length `m`, take `A=I+S`.  The last equation is the
periodic second-difference equation.  Its solutions are
`y_i=c+d*i`; periodicity forces `d*m=0` in `F_3`.  Each component therefore
contributes one kernel direction, plus one more exactly when `3` divides
`m`.  The free scalar `a` supplies one further direction.  Hence:

```text
cycle type       6   4+2   3+3   2+2+2
Gram nullity     3     3     5       4
Gram rank       10    10     8       9
```

The independent checker also performs direct modular row reduction as a
cross-check.

## Radical versus true relations

Let `U` be the actual column span, `r=dim(U)`, and `g` the Gram rank.  The
restricted-form radical has dimension `r-g` and lies in `U^perp`.  The
ambient 11-space is nondegenerate, so

```text
r-g <= 11-r,
r <= floor((11+g)/2).
```

Together with `g<=r`, this yields:

```text
type       possible r   true relation dim   cross quotient dim
6              10               3                  1
4+2            10               3                  1
3+3          8 or 9          at least 4         at least 2
2+2+2       9 or 10          at least 3         at least 1
```

The cross quotient is after removing the two independent star circuits.
For nonadjacent stars, 14 columns in dimension 11 similarly give at least
three true relations and therefore at least one cross-star class.

This is the crucial kernel distinction.  A true coefficient relation is
always a Gram-kernel word, but the converse can fail when the restriction
is degenerate.  Only types `6` and `4+2` force `r=g=10`; only there do the
three-dimensional coefficient and Gram kernels coincide.  Independent
enumeration of those 27 already-derived kernel words gives:

```text
type 6:   minimum non-star support 8
type 4+2: minimum non-star support 4
```

No support claim is promoted for types `3+3` or `2+2+2`.

## Integrity and execution

- all five frozen discovery inputs matched;
- all nine Wave 176 package-manifest entries matched;
- the archived discovery result replay passed;
- all eight discovery tests passed;
- the clean-room checker reproduced the four ranks, radical bounds, and
  rank-10 support distributions;
- all eight clean-room tests passed.

The tests are finite exact algebra on matrices of order at most 13.  They do
not search graphs, codes, SAT instances, or isomorphism classes.

## Status wall

```text
conditional projector and trace-rank identities: VERIFIED
four adjacent cycle types and Gram ranks:          VERIFIED
true cross-relation dimension bounds:              VERIFIED
rank-10 minimum supports 8 and 4:                  VERIFIED
endpoint or rank 11 excluded:                      NO
global compatibility of pairwise relations:       UNKNOWN
strict n3 improvement / Conway-99:                 UNKNOWN
external novelty:                                  UNKNOWN
```
